"""
Rule Execution Service

Enhanced rule engine with complete traceability:
- Workflow event logging for all rule executions
- Asset versioning for changes
- Batch operation tracking for rollback
- Priority-based rule ordering

Actions supported:
- CREATE_CHILD: Create related child asset (e.g., motor for pump)
- CREATE_CABLE: Create power/signal cable with auto-sizing
- CREATE_PACKAGE: Group assets into deliverable package
- SET_PROPERTY: Update asset properties
- CREATE_RELATIONSHIP: Create edge between assets
- ALLOCATE_IO: Allocate IO points to assets
- VALIDATE: Run validation checks

Design based on: .dev/design/2025-11-28-whiteboard-session.md
"""

import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from sqlalchemy import and_, desc
from sqlalchemy.orm import Session

from app.models.cables import Cable
from app.models.metamodel import MetamodelEdge
from app.models.models import Asset
from app.models.packages import Package, PackageStatus
from app.models.rules import RuleActionType, RuleDefinition, RuleExecution
from app.models.workflow import (
    BatchOperationType,
    ChangeSource,
    LogSource,
    WorkflowActionType,
)
from app.services.versioning_service import VersioningService
from app.services.workflow_logger import (
    BatchOperationManager,
    WorkflowLogger,
)


@dataclass
class ExecutionContext:
    """Context for rule execution."""

    project_id: str
    user_id: str | None
    correlation_id: str
    batch_id: str | None
    session_id: str | None = None


@dataclass
class ActionResult:
    """Result of a single action execution."""

    success: bool
    action_type: str
    message: str
    entity_id: str | None = None
    entity_tag: str | None = None
    entity_type: str | None = None
    error: str | None = None
    duration_ms: int = 0
    details: dict | None = None


@dataclass
class RuleExecutionResult:
    """Result of executing a single rule on multiple assets."""

    rule_id: str
    rule_name: str
    total_assets: int
    actions_taken: int
    skipped: int
    errors: int
    duration_ms: int
    action_results: list[ActionResult]


@dataclass
class ExecutionSummary:
    """Summary of a full rule execution run."""

    total_rules: int
    total_assets: int
    total_executions: int
    actions_taken: int
    skipped: int
    errors: int
    duration_ms: int
    rule_results: list[RuleExecutionResult]


class RuleExecutionService:
    """
    Enhanced rule execution service with full traceability.

    Features:
    - Workflow event logging for every action
    - Asset versioning for all changes
    - Batch operation tracking for rollback
    - Priority queue for rule ordering
    - Idempotent actions (won't duplicate assets)
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

        # Initialize services
        self._workflow_logger = WorkflowLogger(db, project_id, user_id)
        self._versioning = VersioningService(db, project_id, user_id)
        self._batch_manager = BatchOperationManager(db, project_id, user_id)

    # ==========================================================================
    # MAIN EXECUTION
    # ==========================================================================

    def execute_rules(
        self,
        rule_ids: list[str] | None = None,
        asset_ids: list[str] | None = None,
    ) -> ExecutionSummary:
        """
        Execute rules on assets with full traceability.

        Args:
            rule_ids: Specific rules to execute (None = all active rules)
            asset_ids: Specific assets to process (None = all project assets)

        Returns:
            ExecutionSummary with detailed results
        """
        start_time = time.time()

        # Start workflow
        correlation_id = self._workflow_logger.start_workflow(
            source=LogSource.RULE,
            action_type=WorkflowActionType.EXECUTE,
            message="Starting Rule Engine execution",
            details={"rule_count": len(rule_ids) if rule_ids else "all"},
        )

        # Create batch operation for rollback tracking
        batch = self._batch_manager.start_batch(
            operation_type=BatchOperationType.RULE_EXECUTION,
            description=f"Rule execution for project {self.project_id}",
            correlation_id=correlation_id,
        )

        # Create execution context
        context = ExecutionContext(
            project_id=self.project_id,
            user_id=self.user_id,
            correlation_id=correlation_id,
            batch_id=batch.id,
        )

        try:
            # Load rules (priority order)
            rules = self._load_rules(rule_ids)

            self._workflow_logger.log_info(
                f"Loaded {len(rules)} rules for execution",
                correlation_id=correlation_id,
                source=LogSource.RULE,
            )

            # Load assets
            assets = self._load_assets(asset_ids)

            self._workflow_logger.log_info(
                f"Processing {len(assets)} assets",
                correlation_id=correlation_id,
                source=LogSource.RULE,
            )

            # Execute each rule
            rule_results = []
            total_actions = 0
            total_skipped = 0
            total_errors = 0

            for rule in rules:
                result = self._execute_rule(rule, assets, context)
                rule_results.append(result)
                total_actions += result.actions_taken
                total_skipped += result.skipped
                total_errors += result.errors

            # Complete batch
            self._batch_manager.complete_batch(batch.id, affected_assets=total_actions)

            # Complete workflow
            duration_ms = int((time.time() - start_time) * 1000)
            self._workflow_logger.complete_workflow(
                correlation_id=correlation_id,
                duration_ms=duration_ms,
                stats={
                    "rules_executed": len(rules),
                    "assets_processed": len(assets),
                    "actions_taken": total_actions,
                    "skipped": total_skipped,
                    "errors": total_errors,
                },
            )

            return ExecutionSummary(
                total_rules=len(rules),
                total_assets=len(assets),
                total_executions=len(rules) * len(assets),
                actions_taken=total_actions,
                skipped=total_skipped,
                errors=total_errors,
                duration_ms=duration_ms,
                rule_results=rule_results,
            )

        except Exception as e:
            # Fail workflow
            self._workflow_logger.fail_workflow(
                correlation_id=correlation_id,
                error=str(e),
            )
            raise

    def _execute_rule(
        self,
        rule: RuleDefinition,
        assets: list[Asset],
        context: ExecutionContext,
    ) -> RuleExecutionResult:
        """Execute a single rule on all assets."""
        start_time = time.time()

        # Log rule start
        self._workflow_logger.log_event(
            source=LogSource.RULE,
            action_type=WorkflowActionType.EXECUTE,
            message=f"Executing rule: {rule.name}",
            correlation_id=context.correlation_id,
            details={
                "rule_id": rule.id,
                "priority": rule.priority,
                "action_type": rule.action_type.value,
            },
        )

        action_results = []
        actions_taken = 0
        skipped = 0
        errors = 0

        for asset in assets:
            # Evaluate condition
            if not self._evaluate_condition(rule.condition, asset):
                skipped += 1
                continue

            # Execute action
            result = self._execute_action(rule, asset, context)
            action_results.append(result)

            if result.success:
                if result.action_type != "SKIP":
                    actions_taken += 1

                    # Log execution audit
                    self._log_rule_execution(rule, asset, result, context)
                else:
                    skipped += 1
            else:
                errors += 1

        # Update rule stats
        rule.execution_count += 1
        rule.last_executed_at = datetime.utcnow()
        rule.success_count += actions_taken
        rule.failure_count += errors
        self.db.commit()

        duration_ms = int((time.time() - start_time) * 1000)

        return RuleExecutionResult(
            rule_id=rule.id,
            rule_name=rule.name,
            total_assets=len(assets),
            actions_taken=actions_taken,
            skipped=skipped,
            errors=errors,
            duration_ms=duration_ms,
            action_results=action_results,
        )

    # ==========================================================================
    # CONDITION EVALUATION
    # ==========================================================================

    def _evaluate_condition(self, condition: dict, asset: Asset) -> bool:
        """Evaluate if a condition matches an asset."""
        # Check asset_type
        if "asset_type" in condition:
            if asset.type != condition["asset_type"]:
                return False

        # Check node_type (alias)
        if "node_type" in condition:
            if asset.type != condition["node_type"]:
                return False

        # Check property filters
        if "property_filters" in condition and condition["property_filters"]:
            for filter_item in condition["property_filters"]:
                key = filter_item["key"]
                op = filter_item["op"]
                value = filter_item["value"]

                # Get property value
                asset_value = None
                if hasattr(asset, key):
                    asset_value = getattr(asset, key)
                elif asset.properties and key in asset.properties:
                    asset_value = asset.properties[key]

                if not self._evaluate_operator(asset_value, op, value):
                    return False

        return True

    def _evaluate_operator(self, asset_value: Any, op: str, expected: Any) -> bool:
        """Evaluate a comparison operator."""
        if op == "==":
            return asset_value == expected
        elif op == "!=":
            return asset_value != expected
        elif op == ">":
            return asset_value is not None and asset_value > expected
        elif op == "<":
            return asset_value is not None and asset_value < expected
        elif op == ">=":
            return asset_value is not None and asset_value >= expected
        elif op == "<=":
            return asset_value is not None and asset_value <= expected
        elif op in ("in", "IN"):
            return asset_value in expected if isinstance(expected, list) else False
        elif op == "contains":
            return expected in asset_value if isinstance(asset_value, (str, list)) else False
        elif op in ("exists", "EXISTS"):
            return asset_value is not None
        elif op in ("not_exists", "NOT_EXISTS"):
            return asset_value is None
        return False

    # ==========================================================================
    # ACTION EXECUTION
    # ==========================================================================

    def _execute_action(
        self,
        rule: RuleDefinition,
        asset: Asset,
        context: ExecutionContext,
    ) -> ActionResult:
        """Execute the action defined in a rule."""
        start_time = time.time()

        try:
            action_type = rule.action_type

            if action_type == RuleActionType.CREATE_CHILD:
                result = self._action_create_child(rule, asset, context)
            elif action_type == RuleActionType.CREATE_CABLE:
                result = self._action_create_cable(rule, asset, context)
            elif action_type == RuleActionType.CREATE_PACKAGE:
                result = self._action_create_package(rule, asset, context)
            elif action_type == RuleActionType.SET_PROPERTY:
                result = self._action_set_property(rule, asset, context)
            elif action_type == RuleActionType.CREATE_RELATIONSHIP:
                result = self._action_create_relationship(rule, asset, context)
            elif action_type == RuleActionType.ALLOCATE_IO:
                result = self._action_allocate_io(rule, asset, context)
            elif action_type == RuleActionType.VALIDATE:
                result = self._action_validate(rule, asset, context)
            else:
                result = ActionResult(
                    success=True,
                    action_type="SKIP",
                    message=f"Action type {action_type.value} not implemented",
                )

            result.duration_ms = int((time.time() - start_time) * 1000)
            return result

        except Exception as e:
            self.db.rollback()
            return ActionResult(
                success=False,
                action_type="ERROR",
                message=f"Error executing action: {str(e)}",
                error=str(e),
                duration_ms=int((time.time() - start_time) * 1000),
            )

    # ==========================================================================
    # ACTION: CREATE_CHILD
    # ==========================================================================

    def _action_create_child(
        self,
        rule: RuleDefinition,
        asset: Asset,
        context: ExecutionContext,
    ) -> ActionResult:
        """Create a child asset related to the parent."""
        action = rule.action.get("create_child", {})

        child_type = action.get("type")
        if not child_type:
            return ActionResult(
                success=False,
                action_type="ERROR",
                message="Missing child type in rule action",
                error="Missing 'type' in create_child action",
            )

        relation = action.get("relation", "related_to")
        naming = action.get("naming", "{parent_tag}-{type}")
        semantic_type = action.get("semantic_type", "ASSET")

        # Generate child tag
        parent_tag = asset.tag or "UNKNOWN"
        child_tag = (
            naming.replace("{parent_tag}", parent_tag)
            .replace("{type}", child_type[:1])
            .replace("{area}", asset.area or "")
        )

        # Check idempotency
        existing = (
            self.db.query(Asset)
            .filter(
                and_(
                    Asset.tag == child_tag,
                    Asset.project_id == context.project_id,
                    Asset.deleted_at.is_(None),
                )
            )
            .first()
        )

        if existing:
            return ActionResult(
                success=True,
                action_type="SKIP",
                message=f"Child {child_tag} already exists",
                entity_id=existing.id,
                entity_tag=existing.tag,
            )

        # Build child properties
        child_properties = action.get("properties", {}).copy()

        # Inherit properties from parent
        if "inherit_properties" in action and asset.properties:
            for key in action["inherit_properties"]:
                if key in asset.properties:
                    child_properties[key] = asset.properties[key]

        # Get discipline
        discipline = action.get("discipline")
        if not discipline and rule.discipline:
            discipline = rule.discipline

        # Create child asset
        child = Asset(
            tag=child_tag,
            type=child_type,
            project_id=context.project_id,
            semantic_type=semantic_type,
            discipline=discipline,
            area=asset.area,
            system=asset.system,
            location_id=asset.location_id,
            properties=child_properties,
        )

        self.db.add(child)
        self.db.flush()

        # Create version for new asset
        self._versioning.create_initial_version(
            asset=child,
            change_source=ChangeSource.RULE,
            batch_id=context.batch_id,
        )

        # Create relationship edge
        edge = MetamodelEdge(
            source_node_id=child.id,
            target_node_id=asset.id,
            relation_type=relation,
            discipline=discipline,
        )
        self.db.add(edge)
        self.db.commit()

        # Log the creation
        self._workflow_logger.log_create(
            entity_type="ASSET",
            entity_id=child.id,
            entity_tag=child.tag,
            correlation_id=context.correlation_id,
            source=LogSource.RULE,
            discipline=discipline,
            details={
                "parent_tag": asset.tag,
                "rule_id": rule.id,
                "rule_name": rule.name,
                "child_type": child_type,
            },
        )

        return ActionResult(
            success=True,
            action_type="CREATE",
            message=f"Created {child_type} {child_tag} for {asset.tag}",
            entity_id=child.id,
            entity_tag=child.tag,
            entity_type=child_type,
            details={"parent_id": asset.id, "relation": relation},
        )

    # ==========================================================================
    # ACTION: CREATE_CABLE
    # ==========================================================================

    def _action_create_cable(
        self,
        rule: RuleDefinition,
        asset: Asset,
        context: ExecutionContext,
    ) -> ActionResult:
        """Create a cable for the asset."""
        from app.services.cable_sizing import CableSizingService

        action = rule.action.get("create_cable", {})

        cable_tag_pattern = action.get("cable_tag", "{tag}-CBL")
        cable_type = action.get("cable_type", "POWER")
        sizing_method = action.get("sizing_method", "Manual")
        length_meters = action.get("length_meters", 50.0)
        voltage_str = action.get("voltage", "600V")

        # Generate cable tag
        cable_tag = cable_tag_pattern.replace("{tag}", asset.tag or "UNKNOWN")

        # Check idempotency
        existing = (
            self.db.query(Cable)
            .filter(
                and_(
                    Cable.tag == cable_tag,
                    Cable.project_id == context.project_id,
                )
            )
            .first()
        )

        if existing:
            return ActionResult(
                success=True,
                action_type="SKIP",
                message=f"Cable {cable_tag} already exists",
                entity_id=str(existing.id),
                entity_tag=existing.tag,
            )

        # Auto-size if configured
        sizing_result = {}
        if sizing_method == "Auto" and asset.type == "MOTOR":
            hp = None
            if asset.properties:
                hp = asset.properties.get("hp") or asset.properties.get("power")
            if hp:
                try:
                    sizing_result = CableSizingService.size_cable(
                        hp=float(hp),
                        length_meters=length_meters,
                        voltage_str=voltage_str,
                    )
                except Exception:
                    pass

        # Create cable
        cable = Cable(
            tag=cable_tag,
            project_id=context.project_id,
            cable_type=cable_type,
            description=f"{cable_type} cable for {asset.tag}",
            to_asset_id=asset.id,
            length_meters=length_meters,
            conductor_size=sizing_result.get("cable_size"),
            voltage_drop_percent=sizing_result.get("voltage_drop_percent"),
            voltage_drop_volts=sizing_result.get("voltage_drop_volts"),
            code_standard="CEC-2021",
            created_by_rule_id=rule.id,
            properties={
                "sizing_method": sizing_method,
                "insulation": action.get("insulation", "RW90 XLPE"),
                **sizing_result,
            },
        )

        self.db.add(cable)
        self.db.commit()

        # Log creation
        self._workflow_logger.log_create(
            entity_type="CABLE",
            entity_id=str(cable.id),
            entity_tag=cable.tag,
            correlation_id=context.correlation_id,
            source=LogSource.RULE,
            details={
                "asset_tag": asset.tag,
                "cable_type": cable_type,
                "size": sizing_result.get("cable_size"),
                "rule_id": rule.id,
            },
        )

        # Warn if cable exceeds length limit
        length_limit = action.get("max_length", 100)
        if length_meters > length_limit:
            self._workflow_logger.log_warning(
                f"Cable {cable_tag} length {length_meters}m exceeds {length_limit}m limit",
                correlation_id=context.correlation_id,
                source=LogSource.RULE,
                entity_type="CABLE",
                entity_id=str(cable.id),
                entity_tag=cable.tag,
            )

        return ActionResult(
            success=True,
            action_type="CREATE",
            message=f"Created cable {cable_tag} for {asset.tag}",
            entity_id=str(cable.id),
            entity_tag=cable.tag,
            entity_type="CABLE",
            details={"size": sizing_result.get("cable_size")},
        )

    # ==========================================================================
    # ACTION: CREATE_PACKAGE
    # ==========================================================================

    def _action_create_package(
        self,
        rule: RuleDefinition,
        asset: Asset,
        context: ExecutionContext,
    ) -> ActionResult:
        """Group assets into a deliverable package."""
        action = rule.action.get("create_package", {})

        package_type = action.get("package_type", "GENERAL")
        code_template = action.get("code_template", "PKG-{area}")
        include_filter = action.get("include_filter", {})

        # Generate package code
        package_code = (
            code_template.replace("{area}", asset.area or "UNKNOWN")
            .replace("{system}", asset.system or "")
            .replace("{discipline}", asset.discipline or "")
        )

        # Check if package already exists
        existing = (
            self.db.query(Package)
            .filter(
                and_(
                    Package.name == package_code,
                    Package.project_id == context.project_id,
                )
            )
            .first()
        )

        if existing:
            return ActionResult(
                success=True,
                action_type="SKIP",
                message=f"Package {package_code} already exists",
                entity_id=existing.id,
                entity_tag=package_code,
            )

        # Find assets to include in package
        query = self.db.query(Asset).filter(
            and_(
                Asset.project_id == context.project_id,
                Asset.deleted_at.is_(None),
            )
        )

        # Apply include filters
        if "type_in" in include_filter:
            query = query.filter(Asset.type.in_(include_filter["type_in"]))
        if "area" in include_filter:
            area_value = include_filter["area"]
            if area_value == "{trigger.area}":
                area_value = asset.area
            query = query.filter(Asset.area == area_value)
        if "discipline" in include_filter:
            query = query.filter(Asset.discipline == include_filter["discipline"])

        assets_to_include = query.all()

        if not assets_to_include:
            return ActionResult(
                success=True,
                action_type="SKIP",
                message=f"No assets found for package {package_code}",
            )

        # Create package
        package = Package(
            name=package_code,
            description=f"{package_type} package for {asset.area or 'project'}",
            project_id=context.project_id,
            status=PackageStatus.OPEN,
        )

        self.db.add(package)
        self.db.flush()

        # Link assets to package
        for pkg_asset in assets_to_include:
            pkg_asset.package_id = package.id

        self.db.commit()

        # Log creation
        self._workflow_logger.log_create(
            entity_type="PACKAGE",
            entity_id=package.id,
            entity_tag=package_code,
            correlation_id=context.correlation_id,
            source=LogSource.RULE,
            details={
                "package_type": package_type,
                "asset_count": len(assets_to_include),
                "assets": [a.tag for a in assets_to_include[:10]],
                "rule_id": rule.id,
            },
        )

        return ActionResult(
            success=True,
            action_type="CREATE",
            message=f"Created package {package_code} with {len(assets_to_include)} assets",
            entity_id=package.id,
            entity_tag=package_code,
            entity_type="PACKAGE",
            details={"asset_count": len(assets_to_include)},
        )

    # ==========================================================================
    # ACTION: SET_PROPERTY
    # ==========================================================================

    def _action_set_property(
        self,
        rule: RuleDefinition,
        asset: Asset,
        context: ExecutionContext,
    ) -> ActionResult:
        """Set/update properties on an asset."""
        action = rule.action.get("set_property", {})

        if not action:
            return ActionResult(
                success=False,
                action_type="ERROR",
                message="No properties to set",
                error="Empty set_property action",
            )

        # Track changes for logging
        old_values = {}
        new_values = {}

        if asset.properties is None:
            asset.properties = {}

        for key, value in action.items():
            old_values[key] = asset.properties.get(key)
            asset.properties[key] = value
            new_values[key] = value

        # Create new version
        self._versioning.create_version(
            asset=asset,
            change_source=ChangeSource.RULE,
            change_reason=f"Properties updated by rule: {rule.name}",
            batch_id=context.batch_id,
        )

        self.db.commit()

        # Log update
        self._workflow_logger.log_update(
            entity_type="ASSET",
            entity_id=asset.id,
            entity_tag=asset.tag,
            correlation_id=context.correlation_id,
            source=LogSource.RULE,
            details={
                "old_values": old_values,
                "new_values": new_values,
                "rule_id": rule.id,
            },
        )

        return ActionResult(
            success=True,
            action_type="UPDATE",
            message=f"Updated properties on {asset.tag}: {list(action.keys())}",
            entity_id=asset.id,
            entity_tag=asset.tag,
            entity_type="ASSET",
            details={"properties_updated": list(action.keys())},
        )

    # ==========================================================================
    # ACTION: CREATE_RELATIONSHIP
    # ==========================================================================

    def _action_create_relationship(
        self,
        rule: RuleDefinition,
        asset: Asset,
        context: ExecutionContext,
    ) -> ActionResult:
        """Create a relationship edge between assets."""
        action = rule.action.get("create_relationship", {})

        relation_type = action.get("relation", "related_to")
        target_tag_pattern = action.get("target_tag")
        direction = action.get("direction", "outgoing")

        if not target_tag_pattern:
            return ActionResult(
                success=False,
                action_type="ERROR",
                message="Missing target_tag in action",
                error="No target_tag specified",
            )

        # Resolve target tag
        target_tag = target_tag_pattern.replace("{tag}", asset.tag or "")

        # Find target asset
        target = (
            self.db.query(Asset)
            .filter(
                and_(
                    Asset.tag == target_tag,
                    Asset.project_id == context.project_id,
                    Asset.deleted_at.is_(None),
                )
            )
            .first()
        )

        if not target:
            return ActionResult(
                success=True,
                action_type="SKIP",
                message=f"Target asset {target_tag} not found",
            )

        # Determine direction
        if direction == "outgoing":
            source_id = asset.id
            target_id = target.id
        else:
            source_id = target.id
            target_id = asset.id

        # Check if edge exists
        existing = (
            self.db.query(MetamodelEdge)
            .filter(
                and_(
                    MetamodelEdge.source_node_id == source_id,
                    MetamodelEdge.target_node_id == target_id,
                    MetamodelEdge.relation_type == relation_type,
                )
            )
            .first()
        )

        if existing:
            return ActionResult(
                success=True,
                action_type="SKIP",
                message=f"Relationship {relation_type} already exists",
            )

        # Create edge
        edge = MetamodelEdge(
            source_node_id=source_id,
            target_node_id=target_id,
            relation_type=relation_type,
            discipline=rule.discipline,
        )

        self.db.add(edge)
        self.db.commit()

        # Log
        self._workflow_logger.log_event(
            source=LogSource.RULE,
            action_type=WorkflowActionType.LINK,
            message=f"Created {relation_type} relationship to {target_tag}",
            correlation_id=context.correlation_id,
            entity_type="EDGE",
            entity_id=edge.id,
            details={
                "source_tag": asset.tag,
                "target_tag": target_tag,
                "relation": relation_type,
            },
        )

        return ActionResult(
            success=True,
            action_type="LINK",
            message=f"Created {relation_type} to {target_tag}",
            entity_id=edge.id,
            entity_type="EDGE",
            details={"relation": relation_type, "target": target_tag},
        )

    # ==========================================================================
    # ACTION: ALLOCATE_IO
    # ==========================================================================

    def _action_allocate_io(
        self,
        rule: RuleDefinition,
        asset: Asset,
        context: ExecutionContext,
    ) -> ActionResult:
        """Allocate IO points to an asset."""
        action = rule.action.get("allocate_io", {})

        io_type = action.get("io_type")  # AI, AO, DI, DO
        channel_count = action.get("channel_count", 1)

        if not io_type:
            return ActionResult(
                success=False,
                action_type="ERROR",
                message="Missing io_type in action",
                error="No io_type specified",
            )

        # Update asset IO allocation
        if asset.properties is None:
            asset.properties = {}

        io_allocation = asset.properties.get("io_allocation", {})
        current_count = io_allocation.get(io_type, 0)
        io_allocation[io_type] = current_count + channel_count
        asset.properties["io_allocation"] = io_allocation

        # Create version
        self._versioning.create_version(
            asset=asset,
            change_source=ChangeSource.RULE,
            change_reason=f"IO allocated by rule: {rule.name}",
            batch_id=context.batch_id,
        )

        self.db.commit()

        # Log
        self._workflow_logger.log_update(
            entity_type="ASSET",
            entity_id=asset.id,
            entity_tag=asset.tag,
            correlation_id=context.correlation_id,
            source=LogSource.RULE,
            details={
                "io_type": io_type,
                "channels": channel_count,
                "rule_id": rule.id,
            },
        )

        return ActionResult(
            success=True,
            action_type="UPDATE",
            message=f"Allocated {channel_count} {io_type} channel(s) to {asset.tag}",
            entity_id=asset.id,
            entity_tag=asset.tag,
            entity_type="ASSET",
            details={"io_type": io_type, "channels": channel_count},
        )

    # ==========================================================================
    # ACTION: VALIDATE
    # ==========================================================================

    def _action_validate(
        self,
        rule: RuleDefinition,
        asset: Asset,
        context: ExecutionContext,
    ) -> ActionResult:
        """Run validation check on asset."""
        action = rule.action.get("validate", {})

        severity = action.get("severity", "WARNING")
        message_template = action.get("message", "Validation failed")

        # Resolve message template
        message = message_template.replace("{tag}", asset.tag or "")
        if asset.properties:
            for key, value in asset.properties.items():
                message = message.replace(f"{{{key}}}", str(value))

        # Log validation result
        if severity == "ERROR":
            self._workflow_logger.log_error(
                message=f"Validation error: {message}",
                correlation_id=context.correlation_id,
                error=message,
                source=LogSource.RULE,
                entity_type="ASSET",
                entity_id=asset.id,
                entity_tag=asset.tag,
            )
        else:
            self._workflow_logger.log_warning(
                message=f"Validation warning: {message}",
                correlation_id=context.correlation_id,
                source=LogSource.RULE,
                entity_type="ASSET",
                entity_id=asset.id,
                entity_tag=asset.tag,
            )

        return ActionResult(
            success=True,
            action_type="VALIDATE",
            message=f"Validation {severity}: {message}",
            entity_id=asset.id,
            entity_tag=asset.tag,
            entity_type="ASSET",
            details={"severity": severity, "message": message},
        )

    # ==========================================================================
    # HELPERS
    # ==========================================================================

    def _load_rules(self, rule_ids: list[str] | None = None) -> list[RuleDefinition]:
        """Load rules in priority order."""
        query = self.db.query(RuleDefinition).filter(RuleDefinition.is_active == True)

        if rule_ids:
            query = query.filter(RuleDefinition.id.in_(rule_ids))

        return query.order_by(desc(RuleDefinition.priority)).all()

    def _load_assets(self, asset_ids: list[str] | None = None) -> list[Asset]:
        """Load assets for processing."""
        query = self.db.query(Asset).filter(
            and_(
                Asset.project_id == self.project_id,
                Asset.deleted_at.is_(None),
            )
        )

        if asset_ids:
            query = query.filter(Asset.id.in_(asset_ids))

        return query.all()

    def _log_rule_execution(
        self,
        rule: RuleDefinition,
        asset: Asset,
        result: ActionResult,
        context: ExecutionContext,
    ):
        """Create audit log entry for rule execution."""
        execution = RuleExecution(
            rule_id=rule.id,
            project_id=context.project_id,
            asset_id=asset.id,
            action_type=result.action_type,
            action_taken=result.message,
            condition_matched=True,
            created_entity_id=result.entity_id,
            created_entity_type=result.entity_type,
            error_message=result.error,
            execution_time_ms=result.duration_ms,
        )

        self.db.add(execution)
        self.db.commit()
