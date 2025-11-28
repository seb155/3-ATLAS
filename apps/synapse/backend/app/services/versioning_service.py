"""
Asset Versioning Service

Provides complete version control for assets:
- Full snapshot versioning (entire asset state)
- Property-level change tracking
- Rollback capabilities (asset, property, batch)
- Diff comparison between versions

Design based on: .dev/design/2025-11-28-whiteboard-session.md
"""

import json
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from sqlalchemy import and_, desc
from sqlalchemy.orm import Session

from app.models.models import Asset
from app.models.workflow import (
    AssetChange,
    AssetVersion,
    BatchOperation,
    ChangeSource,
    LogLevel,
    LogSource,
    PropertyChange,
    WorkflowActionType,
    WorkflowEvent,
    WorkflowStatus,
)
from app.services.workflow_logger import WorkflowLogger, generate_correlation_id


@dataclass
class RollbackResult:
    """Result of a rollback operation."""

    success: bool
    asset_id: str | None = None
    restored_version: int | None = None
    new_version: int | None = None
    property_restored: str | None = None
    error: str | None = None


@dataclass
class BatchRollbackResult:
    """Result of a batch rollback operation."""

    success: bool
    batch_id: str
    assets_restored: int = 0
    results: list[RollbackResult] | None = None
    error: str | None = None


@dataclass
class VersionDiff:
    """Diff between two versions."""

    asset_id: str
    from_version: int
    to_version: int
    changes: list[dict]  # [{field, old_value, new_value, change_type}]
    added: list[str]  # New fields
    removed: list[str]  # Removed fields
    modified: list[str]  # Changed fields


class VersioningService:
    """
    Manages asset versioning with full snapshot and property-level tracking.

    Features:
    - Automatic version creation on asset changes
    - Snapshot comparison and diff generation
    - Rollback to any previous version
    - Property-level rollback
    - Batch rollback for import/rule execution undo
    """

    def __init__(
        self,
        db: Session,
        project_id: str,
        user_id: str | None = None,
    ):
        self.db = db
        self.project_id = project_id
        self.user_id = user_id
        self._workflow_logger = WorkflowLogger(db, project_id, user_id)

    # ==========================================================================
    # VERSION CREATION
    # ==========================================================================

    def create_version(
        self,
        asset: Asset,
        change_source: ChangeSource,
        change_reason: str | None = None,
        event_id: str | None = None,
        batch_id: str | None = None,
    ) -> AssetVersion:
        """
        Create a new version snapshot for an asset.

        Args:
            asset: The asset to version
            change_source: Source of the change (USER, RULE, IMPORT, etc.)
            change_reason: Human-readable reason for the change
            event_id: Related workflow event ID
            batch_id: Related batch operation ID

        Returns:
            Created AssetVersion
        """
        # Get current version number
        current_version = self._get_latest_version_number(asset.id)
        new_version_number = current_version + 1

        # Create snapshot of current asset state
        snapshot = self._create_snapshot(asset)

        # Create version record
        version = AssetVersion(
            asset_id=asset.id,
            version_number=new_version_number,
            snapshot=snapshot,
            created_by=self.user_id,
            change_reason=change_reason,
            change_source=change_source,
            event_id=event_id,
            batch_id=batch_id,
        )

        self.db.add(version)
        self.db.flush()

        # Track property changes if this isn't the first version
        if current_version > 0:
            self._track_property_changes(asset.id, version.id, new_version_number)

        self.db.commit()

        return version

    def create_initial_version(
        self,
        asset: Asset,
        change_source: ChangeSource = ChangeSource.IMPORT,
        batch_id: str | None = None,
    ) -> AssetVersion:
        """
        Create the initial version (v1) for a new asset.

        Args:
            asset: Newly created asset
            change_source: Source of creation
            batch_id: Related batch operation

        Returns:
            Created AssetVersion (v1)
        """
        snapshot = self._create_snapshot(asset)

        version = AssetVersion(
            asset_id=asset.id,
            version_number=1,
            snapshot=snapshot,
            created_by=self.user_id,
            change_reason="Initial creation",
            change_source=change_source,
            batch_id=batch_id,
        )

        self.db.add(version)
        self.db.commit()

        return version

    # ==========================================================================
    # VERSION QUERIES
    # ==========================================================================

    def get_asset_versions(
        self,
        asset_id: str,
        limit: int = 50,
    ) -> list[AssetVersion]:
        """Get all versions of an asset, newest first."""
        return (
            self.db.query(AssetVersion)
            .filter(AssetVersion.asset_id == asset_id)
            .order_by(desc(AssetVersion.version_number))
            .limit(limit)
            .all()
        )

    def get_version(self, asset_id: str, version_number: int) -> AssetVersion | None:
        """Get a specific version of an asset."""
        return (
            self.db.query(AssetVersion)
            .filter(
                and_(
                    AssetVersion.asset_id == asset_id,
                    AssetVersion.version_number == version_number,
                )
            )
            .first()
        )

    def get_latest_version(self, asset_id: str) -> AssetVersion | None:
        """Get the latest version of an asset."""
        return (
            self.db.query(AssetVersion)
            .filter(AssetVersion.asset_id == asset_id)
            .order_by(desc(AssetVersion.version_number))
            .first()
        )

    def _get_latest_version_number(self, asset_id: str) -> int:
        """Get the latest version number (0 if no versions exist)."""
        latest = self.get_latest_version(asset_id)
        return latest.version_number if latest else 0

    # ==========================================================================
    # PROPERTY HISTORY
    # ==========================================================================

    def get_property_history(
        self,
        asset_id: str,
        property_name: str,
        limit: int = 50,
    ) -> list[PropertyChange]:
        """Get the change history for a specific property."""
        return (
            self.db.query(PropertyChange)
            .filter(
                and_(
                    PropertyChange.asset_id == asset_id,
                    PropertyChange.property_name == property_name,
                )
            )
            .order_by(desc(PropertyChange.changed_at))
            .limit(limit)
            .all()
        )

    def get_property_at_version(
        self,
        asset_id: str,
        property_name: str,
        version_number: int,
    ) -> Any:
        """Get the value of a property at a specific version."""
        version = self.get_version(asset_id, version_number)
        if not version:
            return None

        snapshot = version.snapshot
        if not isinstance(snapshot, dict):
            return None

        # Handle nested properties (e.g., "specs.electrical.voltage")
        if "." in property_name:
            parts = property_name.split(".")
            value = snapshot
            for part in parts:
                if isinstance(value, dict) and part in value:
                    value = value[part]
                else:
                    return None
            return value

        return snapshot.get(property_name)

    def _track_property_changes(
        self,
        asset_id: str,
        version_id: str,
        version_number: int,
    ):
        """Track individual property changes between versions."""
        # Get previous version snapshot
        prev_version = self.get_version(asset_id, version_number - 1)
        current_version = self.get_version(asset_id, version_number)

        if not prev_version or not current_version:
            return

        prev_snapshot = prev_version.snapshot or {}
        curr_snapshot = current_version.snapshot or {}

        # Find all changed properties
        all_keys = set(prev_snapshot.keys()) | set(curr_snapshot.keys())

        for key in all_keys:
            old_value = prev_snapshot.get(key)
            new_value = curr_snapshot.get(key)

            # Skip if unchanged
            if self._values_equal(old_value, new_value):
                continue

            change = PropertyChange(
                asset_id=asset_id,
                version_id=version_id,
                property_name=key,
                old_value=old_value,
                new_value=new_value,
                changed_by=self.user_id,
            )
            self.db.add(change)

    # ==========================================================================
    # VERSION DIFF
    # ==========================================================================

    def diff_versions(
        self,
        asset_id: str,
        from_version: int,
        to_version: int,
    ) -> VersionDiff | None:
        """
        Compare two versions and return the differences.

        Args:
            asset_id: Asset to compare
            from_version: Earlier version number
            to_version: Later version number

        Returns:
            VersionDiff with all changes, or None if versions not found
        """
        v_from = self.get_version(asset_id, from_version)
        v_to = self.get_version(asset_id, to_version)

        if not v_from or not v_to:
            return None

        from_snapshot = v_from.snapshot or {}
        to_snapshot = v_to.snapshot or {}

        changes = []
        added = []
        removed = []
        modified = []

        all_keys = set(from_snapshot.keys()) | set(to_snapshot.keys())

        for key in all_keys:
            old_value = from_snapshot.get(key)
            new_value = to_snapshot.get(key)

            if key not in from_snapshot:
                # New field
                added.append(key)
                changes.append(
                    {
                        "field": key,
                        "old_value": None,
                        "new_value": new_value,
                        "change_type": "ADDED",
                    }
                )
            elif key not in to_snapshot:
                # Removed field
                removed.append(key)
                changes.append(
                    {
                        "field": key,
                        "old_value": old_value,
                        "new_value": None,
                        "change_type": "REMOVED",
                    }
                )
            elif not self._values_equal(old_value, new_value):
                # Modified field
                modified.append(key)
                changes.append(
                    {
                        "field": key,
                        "old_value": old_value,
                        "new_value": new_value,
                        "change_type": "MODIFIED",
                    }
                )

        return VersionDiff(
            asset_id=asset_id,
            from_version=from_version,
            to_version=to_version,
            changes=changes,
            added=added,
            removed=removed,
            modified=modified,
        )

    # ==========================================================================
    # ROLLBACK OPERATIONS
    # ==========================================================================

    def rollback_asset_to_version(
        self,
        asset_id: str,
        target_version: int,
        reason: str,
    ) -> RollbackResult:
        """
        Rollback an entire asset to a previous version.

        Creates a new version (v+1) with the restored state.

        Args:
            asset_id: Asset to rollback
            target_version: Version to restore
            reason: Reason for rollback

        Returns:
            RollbackResult
        """
        try:
            # Get target version snapshot
            target = self.get_version(asset_id, target_version)
            if not target:
                return RollbackResult(
                    success=False,
                    asset_id=asset_id,
                    error=f"Version {target_version} not found",
                )

            # Get current asset
            asset = self.db.query(Asset).filter(Asset.id == asset_id).first()
            if not asset:
                return RollbackResult(
                    success=False,
                    asset_id=asset_id,
                    error="Asset not found",
                )

            # Apply snapshot to asset
            self._apply_snapshot(asset, target.snapshot)

            # Create new version with restored state
            correlation_id = generate_correlation_id()
            event = self._workflow_logger.log_event(
                source=LogSource.ROLLBACK,
                action_type=WorkflowActionType.ROLLBACK,
                message=f"Asset rolled back to version {target_version}",
                correlation_id=correlation_id,
                entity_type="ASSET",
                entity_id=asset_id,
                entity_tag=asset.tag,
                details={
                    "from_version": self._get_latest_version_number(asset_id),
                    "to_version": target_version,
                    "reason": reason,
                },
            )

            new_version = self.create_version(
                asset=asset,
                change_source=ChangeSource.ROLLBACK,
                change_reason=f"Rollback to v{target_version}: {reason}",
                event_id=event.id,
            )

            self.db.commit()

            return RollbackResult(
                success=True,
                asset_id=asset_id,
                restored_version=target_version,
                new_version=new_version.version_number,
            )

        except Exception as e:
            self.db.rollback()
            return RollbackResult(
                success=False,
                asset_id=asset_id,
                error=str(e),
            )

    def rollback_property(
        self,
        asset_id: str,
        property_name: str,
        target_version: int,
        reason: str,
    ) -> RollbackResult:
        """
        Rollback a single property to its value at a previous version.

        Args:
            asset_id: Asset containing the property
            property_name: Property to rollback
            target_version: Version to get the property value from
            reason: Reason for rollback

        Returns:
            RollbackResult
        """
        try:
            # Get property value at target version
            old_value = self.get_property_at_version(asset_id, property_name, target_version)

            # Get current asset
            asset = self.db.query(Asset).filter(Asset.id == asset_id).first()
            if not asset:
                return RollbackResult(
                    success=False,
                    asset_id=asset_id,
                    error="Asset not found",
                )

            # Update the property
            if hasattr(asset, property_name):
                setattr(asset, property_name, old_value)
            elif asset.properties and property_name in asset.properties:
                asset.properties[property_name] = old_value
            else:
                return RollbackResult(
                    success=False,
                    asset_id=asset_id,
                    error=f"Property {property_name} not found",
                )

            # Create new version
            correlation_id = generate_correlation_id()
            event = self._workflow_logger.log_event(
                source=LogSource.ROLLBACK,
                action_type=WorkflowActionType.ROLLBACK,
                message=f"Property '{property_name}' rolled back to v{target_version}",
                correlation_id=correlation_id,
                entity_type="ASSET",
                entity_id=asset_id,
                entity_tag=asset.tag,
                details={
                    "property": property_name,
                    "target_version": target_version,
                    "reason": reason,
                },
            )

            new_version = self.create_version(
                asset=asset,
                change_source=ChangeSource.ROLLBACK,
                change_reason=f"Property '{property_name}' rolled back to v{target_version}",
                event_id=event.id,
            )

            self.db.commit()

            return RollbackResult(
                success=True,
                asset_id=asset_id,
                property_restored=property_name,
                new_version=new_version.version_number,
            )

        except Exception as e:
            self.db.rollback()
            return RollbackResult(
                success=False,
                asset_id=asset_id,
                error=str(e),
            )

    def rollback_batch(
        self,
        batch_id: str,
        reason: str,
        include_triggered_rules: bool = True,
    ) -> BatchRollbackResult:
        """
        Rollback an entire batch operation.

        Args:
            batch_id: Batch to rollback
            reason: Reason for rollback
            include_triggered_rules: Also rollback assets created by triggered rules

        Returns:
            BatchRollbackResult
        """
        try:
            # Get batch operation
            batch = self.db.query(BatchOperation).filter(BatchOperation.id == batch_id).first()
            if not batch:
                return BatchRollbackResult(
                    success=False,
                    batch_id=batch_id,
                    error="Batch operation not found",
                )

            # Get all versions created by this batch
            affected_versions = (
                self.db.query(AssetVersion)
                .filter(AssetVersion.batch_id == batch_id)
                .all()
            )

            # Group by asset and find pre-batch version
            assets_to_rollback = {}
            for version in affected_versions:
                if version.asset_id not in assets_to_rollback:
                    # Find version before batch
                    pre_batch_version = (
                        self.db.query(AssetVersion)
                        .filter(
                            and_(
                                AssetVersion.asset_id == version.asset_id,
                                AssetVersion.version_number < version.version_number,
                                AssetVersion.batch_id != batch_id,
                            )
                        )
                        .order_by(desc(AssetVersion.version_number))
                        .first()
                    )

                    if pre_batch_version:
                        assets_to_rollback[version.asset_id] = pre_batch_version.version_number
                    else:
                        # Asset was created by this batch - mark for deletion
                        assets_to_rollback[version.asset_id] = None

            # Perform rollbacks
            results = []
            for asset_id, target_version in assets_to_rollback.items():
                if target_version is not None:
                    result = self.rollback_asset_to_version(
                        asset_id=asset_id,
                        target_version=target_version,
                        reason=f"Batch rollback: {reason}",
                    )
                else:
                    # Soft delete the asset (it was created by this batch)
                    asset = self.db.query(Asset).filter(Asset.id == asset_id).first()
                    if asset:
                        asset.deleted_at = datetime.utcnow()
                        result = RollbackResult(
                            success=True,
                            asset_id=asset_id,
                        )
                    else:
                        result = RollbackResult(
                            success=False,
                            asset_id=asset_id,
                            error="Asset not found",
                        )
                results.append(result)

            # Mark batch as rolled back
            batch.is_rolled_back = True
            batch.rolled_back_at = datetime.utcnow()
            batch.rolled_back_by = self.user_id
            batch.rollback_reason = reason

            # Log rollback event
            correlation_id = generate_correlation_id()
            self._workflow_logger.log_event(
                source=LogSource.ROLLBACK,
                action_type=WorkflowActionType.ROLLBACK,
                message=f"Batch operation rolled back: {len(results)} assets",
                correlation_id=correlation_id,
                level=LogLevel.WARN,
                details={
                    "batch_id": batch_id,
                    "assets_restored": len(results),
                    "include_triggered_rules": include_triggered_rules,
                    "reason": reason,
                },
            )

            self.db.commit()

            successful = sum(1 for r in results if r.success)
            return BatchRollbackResult(
                success=True,
                batch_id=batch_id,
                assets_restored=successful,
                results=results,
            )

        except Exception as e:
            self.db.rollback()
            return BatchRollbackResult(
                success=False,
                batch_id=batch_id,
                error=str(e),
            )

    # ==========================================================================
    # HELPERS
    # ==========================================================================

    def _create_snapshot(self, asset: Asset) -> dict:
        """Create a JSON-serializable snapshot of an asset."""
        snapshot = {
            "id": asset.id,
            "tag": asset.tag,
            "description": asset.description,
            "type": asset.type,
            "project_id": asset.project_id,
            "area": asset.area,
            "system": asset.system,
            "io_type": asset.io_type.value if asset.io_type else None,
            "mechanical": asset.mechanical,
            "electrical": asset.electrical,
            "process": asset.process,
            "purchasing": asset.purchasing,
            "manufacturer_part_id": asset.manufacturer_part_id,
            "data_status": asset.data_status.value if asset.data_status else None,
            "confidence_score": asset.confidence_score,
            "data_source_id": asset.data_source_id,
            "discipline": asset.discipline,
            "semantic_type": asset.semantic_type,
            "lod": asset.lod,
            "isa95_level": asset.isa95_level,
            "properties": asset.properties,
            "location_id": asset.location_id,
            "package_id": asset.package_id,
        }

        return snapshot

    def _apply_snapshot(self, asset: Asset, snapshot: dict):
        """Apply a snapshot to an asset."""
        from app.models.models import AssetDataStatus, IOType

        # Apply simple fields
        asset.tag = snapshot.get("tag", asset.tag)
        asset.description = snapshot.get("description")
        asset.type = snapshot.get("type", asset.type)
        asset.area = snapshot.get("area")
        asset.system = snapshot.get("system")
        asset.mechanical = snapshot.get("mechanical")
        asset.electrical = snapshot.get("electrical")
        asset.process = snapshot.get("process")
        asset.purchasing = snapshot.get("purchasing")
        asset.manufacturer_part_id = snapshot.get("manufacturer_part_id")
        asset.confidence_score = snapshot.get("confidence_score", 1.0)
        asset.data_source_id = snapshot.get("data_source_id")
        asset.discipline = snapshot.get("discipline")
        asset.semantic_type = snapshot.get("semantic_type")
        asset.lod = snapshot.get("lod")
        asset.isa95_level = snapshot.get("isa95_level")
        asset.properties = snapshot.get("properties")
        asset.location_id = snapshot.get("location_id")
        asset.package_id = snapshot.get("package_id")

        # Apply enum fields
        io_type_value = snapshot.get("io_type")
        if io_type_value:
            try:
                asset.io_type = IOType(io_type_value)
            except ValueError:
                pass

        data_status_value = snapshot.get("data_status")
        if data_status_value:
            try:
                asset.data_status = AssetDataStatus(data_status_value)
            except ValueError:
                pass

    def _values_equal(self, a: Any, b: Any) -> bool:
        """Compare two values for equality, handling JSON serialization."""
        if a is None and b is None:
            return True
        if a is None or b is None:
            return False

        # Compare as JSON strings for complex objects
        if isinstance(a, (dict, list)) or isinstance(b, (dict, list)):
            return json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)

        return a == b
