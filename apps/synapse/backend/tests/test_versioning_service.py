"""
Tests for VersioningService - Asset version control.

Tests cover:
- Version creation and queries
- Property history tracking
- Version diff comparison
- Rollback operations (asset, property, batch)
"""

import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock

from app.models.models import Asset, AssetDataStatus, IOType
from app.models.auth import Client, Project
from app.models.workflow import (
    AssetVersion,
    BatchOperation,
    BatchOperationType,
    ChangeSource,
    PropertyChange,
)
from app.services.versioning_service import (
    VersioningService,
    RollbackResult,
    BatchRollbackResult,
    VersionDiff,
)


@pytest.fixture
def test_client(db_session):
    """Create a test client."""
    client = Client(
        id="test-client-versioning",
        name="Test Client Versioning",
    )
    db_session.add(client)
    db_session.commit()
    return client


@pytest.fixture
def test_project(db_session, test_client):
    """Create a test project."""
    project = Project(
        id="test-project-versioning",
        name="Test Project Versioning",
        client_id=test_client.id,
    )
    db_session.add(project)
    db_session.commit()
    return project


@pytest.fixture
def test_asset(db_session, test_project):
    """Create a test asset."""
    asset = Asset(
        id="test-asset-versioning",
        tag="TEST-001",
        description="Test Asset",
        type="INSTRUMENT",
        project_id=test_project.id,
        area="AREA-1",
        system="SYS-1",
        discipline="INST",
        properties={"custom_field": "value1"},
    )
    db_session.add(asset)
    db_session.commit()
    return asset


@pytest.fixture
def versioning_service(db_session, test_project, client):
    """Create a VersioningService instance."""
    # The client fixture from conftest.py creates dev-user
    # We need to depend on it to ensure the user exists
    return VersioningService(
        db=db_session,
        project_id=test_project.id,
        user_id="dev-user",
    )


class TestVersionCreation:
    """Tests for version creation."""

    def test_create_initial_version(self, versioning_service, test_asset, db_session):
        """Test creating the initial version of an asset."""
        version = versioning_service.create_initial_version(
            asset=test_asset,
            change_source=ChangeSource.IMPORT,
        )

        assert version is not None
        assert version.version_number == 1
        assert version.asset_id == test_asset.id
        assert version.change_source == ChangeSource.IMPORT
        assert version.change_reason == "Initial creation"
        assert version.snapshot is not None
        assert version.snapshot["tag"] == "TEST-001"

    def test_create_subsequent_version(self, versioning_service, test_asset, db_session):
        """Test creating subsequent versions."""
        # Create initial version
        v1 = versioning_service.create_initial_version(test_asset)
        assert v1.version_number == 1

        # Modify asset
        test_asset.description = "Modified description"
        db_session.commit()

        # Create new version
        v2 = versioning_service.create_version(
            asset=test_asset,
            change_source=ChangeSource.USER,
            change_reason="Updated description",
        )

        assert v2.version_number == 2
        assert v2.snapshot["description"] == "Modified description"

    def test_create_version_with_batch_id(self, versioning_service, test_asset, db_session):
        """Test creating version with batch reference."""
        batch = BatchOperation(
            id="test-batch-123",
            operation_type=BatchOperationType.IMPORT,
            project_id=test_asset.project_id,
            correlation_id="test-correlation-123",
        )
        db_session.add(batch)
        db_session.commit()

        version = versioning_service.create_initial_version(
            asset=test_asset,
            change_source=ChangeSource.IMPORT,
            batch_id=batch.id,
        )

        assert version.batch_id == batch.id


class TestVersionQueries:
    """Tests for version queries."""

    def test_get_asset_versions(self, versioning_service, test_asset, db_session):
        """Test getting all versions of an asset."""
        # Create multiple versions
        versioning_service.create_initial_version(test_asset)

        test_asset.description = "V2"
        db_session.commit()
        versioning_service.create_version(test_asset, ChangeSource.USER)

        test_asset.description = "V3"
        db_session.commit()
        versioning_service.create_version(test_asset, ChangeSource.USER)

        versions = versioning_service.get_asset_versions(test_asset.id)

        assert len(versions) == 3
        # Should be ordered newest first
        assert versions[0].version_number == 3
        assert versions[1].version_number == 2
        assert versions[2].version_number == 1

    def test_get_asset_versions_with_limit(self, versioning_service, test_asset, db_session):
        """Test limiting version results."""
        versioning_service.create_initial_version(test_asset)

        for i in range(5):
            test_asset.description = f"V{i+2}"
            db_session.commit()
            versioning_service.create_version(test_asset, ChangeSource.USER)

        versions = versioning_service.get_asset_versions(test_asset.id, limit=3)
        assert len(versions) == 3

    def test_get_version(self, versioning_service, test_asset, db_session):
        """Test getting a specific version."""
        versioning_service.create_initial_version(test_asset)

        test_asset.description = "V2"
        db_session.commit()
        versioning_service.create_version(test_asset, ChangeSource.USER)

        v1 = versioning_service.get_version(test_asset.id, 1)
        v2 = versioning_service.get_version(test_asset.id, 2)

        assert v1.snapshot["description"] == "Test Asset"
        assert v2.snapshot["description"] == "V2"

    def test_get_version_not_found(self, versioning_service, test_asset):
        """Test getting non-existent version."""
        result = versioning_service.get_version(test_asset.id, 999)
        assert result is None

    def test_get_latest_version(self, versioning_service, test_asset, db_session):
        """Test getting the latest version."""
        versioning_service.create_initial_version(test_asset)

        test_asset.description = "Latest"
        db_session.commit()
        versioning_service.create_version(test_asset, ChangeSource.USER)

        latest = versioning_service.get_latest_version(test_asset.id)
        assert latest.version_number == 2
        assert latest.snapshot["description"] == "Latest"


class TestPropertyHistory:
    """Tests for property history tracking."""

    def test_get_property_at_version(self, versioning_service, test_asset, db_session):
        """Test getting property value at specific version."""
        versioning_service.create_initial_version(test_asset)

        test_asset.description = "Updated"
        db_session.commit()
        versioning_service.create_version(test_asset, ChangeSource.USER)

        v1_desc = versioning_service.get_property_at_version(
            test_asset.id, "description", 1
        )
        v2_desc = versioning_service.get_property_at_version(
            test_asset.id, "description", 2
        )

        assert v1_desc == "Test Asset"
        assert v2_desc == "Updated"

    def test_get_property_at_version_not_found(self, versioning_service, test_asset):
        """Test getting property from non-existent version."""
        result = versioning_service.get_property_at_version(
            test_asset.id, "description", 999
        )
        assert result is None

    def test_get_nested_property_at_version(self, versioning_service, test_asset, db_session):
        """Test getting nested property value."""
        test_asset.properties = {"nested": {"field": "value"}}
        db_session.commit()
        versioning_service.create_initial_version(test_asset)

        # The snapshot stores properties directly
        value = versioning_service.get_property_at_version(
            test_asset.id, "properties", 1
        )
        assert value == {"nested": {"field": "value"}}


class TestVersionDiff:
    """Tests for version comparison."""

    def test_diff_versions(self, versioning_service, test_asset, db_session):
        """Test comparing two versions."""
        versioning_service.create_initial_version(test_asset)

        test_asset.description = "Modified"
        test_asset.area = "AREA-2"
        db_session.commit()
        versioning_service.create_version(test_asset, ChangeSource.USER)

        diff = versioning_service.diff_versions(test_asset.id, 1, 2)

        assert diff is not None
        assert diff.asset_id == test_asset.id
        assert diff.from_version == 1
        assert diff.to_version == 2
        assert "description" in diff.modified
        assert "area" in diff.modified
        assert len(diff.changes) >= 2

    def test_diff_versions_with_added_fields(self, versioning_service, test_asset, db_session):
        """Test diff detecting added fields."""
        test_asset.system = None
        db_session.commit()
        versioning_service.create_initial_version(test_asset)

        test_asset.system = "NEW-SYSTEM"
        db_session.commit()
        versioning_service.create_version(test_asset, ChangeSource.USER)

        diff = versioning_service.diff_versions(test_asset.id, 1, 2)

        # system changed from None to value
        assert any(c["field"] == "system" for c in diff.changes)

    def test_diff_versions_not_found(self, versioning_service, test_asset):
        """Test diff with non-existent versions."""
        diff = versioning_service.diff_versions(test_asset.id, 1, 999)
        assert diff is None


class TestRollbackOperations:
    """Tests for rollback functionality."""

    def test_rollback_asset_to_version(self, versioning_service, test_asset, db_session):
        """Test rolling back an asset to a previous version."""
        versioning_service.create_initial_version(test_asset)

        # Modify asset
        test_asset.description = "Modified"
        test_asset.area = "NEW-AREA"
        db_session.commit()
        versioning_service.create_version(test_asset, ChangeSource.USER)

        # Rollback to v1
        result = versioning_service.rollback_asset_to_version(
            asset_id=test_asset.id,
            target_version=1,
            reason="Testing rollback",
        )

        assert result.success is True
        assert result.restored_version == 1
        assert result.new_version == 3  # Creates new version

        # Verify asset was restored
        db_session.refresh(test_asset)
        assert test_asset.description == "Test Asset"
        assert test_asset.area == "AREA-1"

    def test_rollback_to_nonexistent_version(self, versioning_service, test_asset):
        """Test rollback to non-existent version."""
        versioning_service.create_initial_version(test_asset)

        result = versioning_service.rollback_asset_to_version(
            asset_id=test_asset.id,
            target_version=999,
            reason="Testing",
        )

        assert result.success is False
        assert "not found" in result.error.lower()

    def test_rollback_nonexistent_asset(self, versioning_service):
        """Test rollback of non-existent asset."""
        result = versioning_service.rollback_asset_to_version(
            asset_id="nonexistent-id",
            target_version=1,
            reason="Testing",
        )

        assert result.success is False

    def test_rollback_property(self, versioning_service, test_asset, db_session):
        """Test rolling back a single property."""
        versioning_service.create_initial_version(test_asset)

        # Modify multiple properties
        original_area = test_asset.area
        test_asset.description = "New Description"
        test_asset.area = "NEW-AREA"
        db_session.commit()
        versioning_service.create_version(test_asset, ChangeSource.USER)

        # Rollback only area
        result = versioning_service.rollback_property(
            asset_id=test_asset.id,
            property_name="area",
            target_version=1,
            reason="Restore area only",
        )

        assert result.success is True
        assert result.property_restored == "area"

        db_session.refresh(test_asset)
        assert test_asset.area == original_area
        # Description should still be modified
        assert test_asset.description == "New Description"

    def test_rollback_property_not_found(self, versioning_service, test_asset, db_session):
        """Test rollback of non-existent property."""
        versioning_service.create_initial_version(test_asset)

        result = versioning_service.rollback_property(
            asset_id=test_asset.id,
            property_name="nonexistent_property",
            target_version=1,
            reason="Testing",
        )

        assert result.success is False
        assert "not found" in result.error.lower()


class TestBatchRollback:
    """Tests for batch rollback operations."""

    def test_rollback_batch(self, versioning_service, test_asset, db_session, test_project):
        """Test rolling back an entire batch operation."""
        # Create batch
        batch = BatchOperation(
            id="test-batch-rollback",
            operation_type=BatchOperationType.IMPORT,
            project_id=test_project.id,
            correlation_id="test-correlation-rollback",
        )
        db_session.add(batch)
        db_session.commit()

        # Create initial version (before batch)
        versioning_service.create_initial_version(test_asset)

        # Simulate batch modification
        test_asset.description = "Batch Modified"
        db_session.commit()
        versioning_service.create_version(
            test_asset,
            ChangeSource.IMPORT,
            batch_id=batch.id,
        )

        # Rollback batch
        result = versioning_service.rollback_batch(
            batch_id=batch.id,
            reason="Undo batch import",
        )

        assert result.success is True
        assert result.batch_id == batch.id

    def test_rollback_batch_not_found(self, versioning_service):
        """Test rollback of non-existent batch."""
        result = versioning_service.rollback_batch(
            batch_id="nonexistent-batch",
            reason="Testing",
        )

        assert result.success is False
        assert "not found" in result.error.lower()


class TestHelperMethods:
    """Tests for helper methods."""

    def test_values_equal_none(self, versioning_service):
        """Test _values_equal with None values."""
        assert versioning_service._values_equal(None, None) is True
        assert versioning_service._values_equal(None, "value") is False
        assert versioning_service._values_equal("value", None) is False

    def test_values_equal_simple(self, versioning_service):
        """Test _values_equal with simple values."""
        assert versioning_service._values_equal("a", "a") is True
        assert versioning_service._values_equal("a", "b") is False
        assert versioning_service._values_equal(1, 1) is True
        assert versioning_service._values_equal(1, 2) is False

    def test_values_equal_complex(self, versioning_service):
        """Test _values_equal with complex values."""
        dict1 = {"a": 1, "b": 2}
        dict2 = {"b": 2, "a": 1}  # Same content, different order
        dict3 = {"a": 1, "b": 3}

        assert versioning_service._values_equal(dict1, dict2) is True
        assert versioning_service._values_equal(dict1, dict3) is False

        list1 = [1, 2, 3]
        list2 = [1, 2, 3]
        list3 = [1, 2, 4]

        assert versioning_service._values_equal(list1, list2) is True
        assert versioning_service._values_equal(list1, list3) is False

    def test_create_snapshot(self, versioning_service, test_asset):
        """Test snapshot creation."""
        snapshot = versioning_service._create_snapshot(test_asset)

        assert snapshot["id"] == test_asset.id
        assert snapshot["tag"] == test_asset.tag
        assert snapshot["description"] == test_asset.description
        assert snapshot["type"] == test_asset.type
        assert snapshot["project_id"] == test_asset.project_id
        assert snapshot["properties"] == test_asset.properties

    def test_apply_snapshot(self, versioning_service, test_asset, db_session):
        """Test applying a snapshot to an asset."""
        snapshot = {
            "tag": "RESTORED-001",
            "description": "Restored Description",
            "area": "RESTORED-AREA",
            "system": "RESTORED-SYS",
            "io_type": "DI",
            "data_status": "VALIDATED",
        }

        versioning_service._apply_snapshot(test_asset, snapshot)

        assert test_asset.tag == "RESTORED-001"
        assert test_asset.description == "Restored Description"
        assert test_asset.area == "RESTORED-AREA"
        assert test_asset.system == "RESTORED-SYS"
        assert test_asset.io_type == IOType.DI
        assert test_asset.data_status == AssetDataStatus.VALIDATED
