import csv
import io
import os
import uuid

from fastapi import APIRouter, Depends, File, Form, Header, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.core.database import get_db
from app.core.exceptions import DatabaseError, FileValidationError, RuleExecutionError
from app.core.exceptions import ValidationError as SynapseValidationError
from app.models.action_log import ActionType
from app.models.models import Asset
from app.models.workflow import BatchOperationType, LogSource, WorkflowActionType
from app.schemas.import_export import CSVRowError, ImportSummaryResponse
from app.services.action_logger import ActionLogger
from app.services.metamodel import MetamodelService
from app.services.versioning_service import VersioningService
from app.services.workflow_logger import BatchOperationManager, WorkflowLogger

router = APIRouter()


def get_user_id(current_user) -> str | None:
    """Helper to extract user_id from User object or dict (for tests)"""
    if current_user is None:
        return None
    if isinstance(current_user, dict):
        return current_user.get("id") or current_user.get("username")
    return getattr(current_user, "id", None)


@router.get("/export", response_class=StreamingResponse)
def export_assets_csv(
    project_id: str = Header(..., alias="X-Project-ID"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    assets = db.query(Asset).filter(Asset.project_id == project_id).all()

    def iter_csv():
        output = io.StringIO()
        writer = csv.writer(output)

        # Define Headers
        headers = [
            "id",
            "tag",
            "description",
            "type",
            "area",
            "system",
            "io_type",
            "manufacturer_part_id",
            "location_id",
            "electrical.voltage",
            "electrical.powerKW",
            "electrical.loadType",
            "process.fluid",
            "process.minRange",
            "process.maxRange",
            "process.units",
            "purchasing.workPackageId",
            "purchasing.status",
        ]
        writer.writerow(headers)
        yield output.getvalue()
        output.seek(0)
        output.truncate(0)

        for asset in assets:
            # Flatten Data
            elec = asset.electrical or {}
            proc = asset.process or {}
            purch = asset.purchasing or {}

            row = [
                asset.id,
                asset.tag,
                asset.description,
                asset.type if asset.type else "",  # Now String, not Enum
                asset.area,
                asset.system,
                asset.io_type.value if asset.io_type else "",
                asset.manufacturer_part_id,
                asset.location_id,
                elec.get("voltage", ""),
                elec.get("powerKW", ""),
                elec.get("loadType", ""),
                proc.get("fluid", ""),
                proc.get("minRange", ""),
                proc.get("maxRange", ""),
                proc.get("units", ""),
                purch.get("workPackageId", ""),
                purch.get("status", ""),
            ]
            writer.writerow(row)
            yield output.getvalue()
            output.seek(0)
            output.truncate(0)

    response = StreamingResponse(iter_csv(), media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=assets_export.csv"
    return response




@router.post("/import", response_model=ImportSummaryResponse, status_code=200)
async def import_assets_csv(
    file: UploadFile = File(...),
    mapping: str = Form(None),  # JSON string of mapping: {"system_field": "csv_header"}
    project_id: str = Header(..., alias="X-Project-ID"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    """
    Import assets from CSV file with optional column mapping.

    **Multi-tenant:** Scoped to project_id from X-Project-ID header.

    **CSV Format:**
    - Required columns: tag, type (or mapped equivalents)
    - Optional columns: description, area, system, io_type, etc.
    - Nested fields: electrical.voltage, process.fluid, purchasing.status

    **Mapping:**
    - Optional JSON string mapping system fields to CSV headers.
    - Example: {"tag": "Equipment Tag", "description": "Desc"}

    **Behavior:**
    - Creates new assets if tag doesn't exist
    - Updates existing assets if tag already exists in project
    - Auto-executes rules if assets are created

    **Returns:**
    - Summary with counts (created, updated, failed)
    - List of errors with row numbers
    """
    if not file.filename.endswith(".csv"):
        raise FileValidationError(file.filename, "Please upload a CSV file")

    # Parse mapping if provided
    column_map = {}
    if mapping:
        try:
            import json
            column_map = json.loads(mapping)
        except Exception as e:
            print(f"Warning: Failed to parse mapping JSON: {e}")

    content = await file.read()
    decoded = content.decode("utf-8-sig")  # Handle BOM
    csv_reader = csv.DictReader(io.StringIO(decoded))

    # Initialize summary with proper types
    summary = {
        "created": 0,
        "updated": 0,
        "failed": 0,
        "errors": [],
        "total_rows": 0,
    }

    # Create parent log for this import (legacy ActionLogger)
    import_log = ActionLogger.log(
        db=db,
        action_type=ActionType.CREATE,
        description=f"CSV Import: {file.filename}",
        project_id=project_id,
        entity_type="IMPORT",
        details={"filename": file.filename, "mapping": column_map},
    )

    # NEW: Initialize WorkflowLogger and BatchOperationManager for MVP traceability
    user_id = get_user_id(current_user)
    workflow_logger = WorkflowLogger(
        db=db,
        project_id=project_id,
        user_id=user_id,
    )
    batch_manager = BatchOperationManager(
        db=db,
        project_id=project_id,
        user_id=user_id,
    )
    versioning_service = VersioningService(db, project_id)

    # Start workflow and batch operation
    correlation_id = workflow_logger.start_workflow(
        source=LogSource.IMPORT,
        action_type=WorkflowActionType.IMPORT,
        message=f"CSV Import: {file.filename}",
        details={"filename": file.filename, "mapping": column_map},
    )
    batch_id = batch_manager.start_batch(
        operation_type=BatchOperationType.IMPORT,
        description=f"CSV Import: {file.filename}",
        correlation_id=correlation_id,
    )

    # Helper to parse nested keys like "electrical.voltage"
    def set_nested(d, keys, value):
        for key in keys[:-1]:
            d = d.setdefault(key, {})
        d[keys[-1]] = value

    # Helper to get value from row using mapping
    def get_mapped_value(row, system_field):
        # 1. Try mapped column
        if system_field in column_map:
            csv_header = column_map[system_field]
            if csv_header in row:
                return row[csv_header]

        # 2. Try direct match
        if system_field in row:
            return row[system_field]

        return None

    for row_idx, row in enumerate(csv_reader):
        summary["total_rows"] += 1
        try:
            # 1. Identify Asset
            asset_id = get_mapped_value(row, "id")
            tag = get_mapped_value(row, "tag")

            if not tag:
                summary["errors"].append(
                    CSVRowError(row=row_idx, tag=None, error="Missing required field: tag").dict()
                )
                summary["failed"] += 1
                continue

            # 2. Prepare Data Structure
            asset_data = {
                "tag": tag,
                "description": get_mapped_value(row, "description"),
                "area": get_mapped_value(row, "area"),
                "system": get_mapped_value(row, "system"),
                "manufacturer_part_id": get_mapped_value(row, "manufacturer_part_id"),
                "location_id": get_mapped_value(row, "location_id") or None,
                "electrical": {},
                "process": {},
                "purchasing": {},
            }

            # Enums
            type_val = get_mapped_value(row, "type")
            if type_val:
                asset_data["type"] = type_val

            io_type_val = get_mapped_value(row, "io_type")
            if io_type_val:
                asset_data["io_type"] = io_type_val

            # Nested Fields & Unmapped fields
            # We iterate through the row to find nested fields that might be mapped OR unmapped
            # But for mapped nested fields (e.g. "electrical.voltage"), the mapping key is "electrical.voltage"

            # Strategy:
            # 1. Check for specific known nested fields via mapping
            known_nested = [
                "electrical.voltage", "electrical.powerKW", "electrical.loadType",
                "process.fluid", "process.minRange", "process.maxRange", "process.units",
                "purchasing.workPackageId", "purchasing.status"
            ]

            for field in known_nested:
                val = get_mapped_value(row, field)
                if val:
                    parts = field.split(".")
                    set_nested(asset_data, parts, val)

            # 2. Also check for direct nested columns in CSV (legacy support)
            for key, value in row.items():
                if key and "." in key and value:
                    # Only if NOT already set by mapping
                    parts = key.split(".")
                    if parts[0] in ["electrical", "process", "purchasing"]:
                        # Check if this specific nested path was already set via mapping
                        # This is a bit complex to check efficiently, so we just overwrite if it wasn't mapped
                        # Or better: only process if key is NOT a value in column_map
                        is_mapped_column = False
                        for map_key, map_val in column_map.items():
                            if map_val == key:
                                is_mapped_column = True
                                break

                        if not is_mapped_column:
                            set_nested(asset_data, parts, value)

            # 3. Find Existing
            existing_asset = None
            if asset_id:
                existing_asset = (
                    db.query(Asset)
                    .filter(Asset.id == asset_id, Asset.project_id == project_id)
                    .first()
                )

            if not existing_asset:
                existing_asset = (
                    db.query(Asset).filter(Asset.tag == tag, Asset.project_id == project_id).first()
                )

            # 4. Update or Create
            if existing_asset:
                # Capture old state for versioning
                old_snapshot = {
                    "tag": existing_asset.tag,
                    "description": existing_asset.description,
                    "type": existing_asset.type,
                    "area": existing_asset.area,
                    "system": existing_asset.system,
                    "electrical": existing_asset.electrical,
                    "process": existing_asset.process,
                    "purchasing": existing_asset.purchasing,
                }

                # Update
                for key, value in asset_data.items():
                    if value is not None:
                        setattr(existing_asset, key, value)
                summary["updated"] += 1
                # Log update (legacy)
                ActionLogger.log(
                    db=db,
                    action_type=ActionType.UPDATE,
                    description=f"Updated asset: {tag}",
                    project_id=project_id,
                    parent_id=import_log.id,
                    entity_type="ASSET",
                    entity_id=uuid.UUID(existing_asset.id),
                    details={"tag": tag, "type": asset_data.get("type")},
                )

                # NEW: Log to WorkflowLogger for real-time traceability
                workflow_logger.log_update(
                    source=LogSource.IMPORT,
                    message=f"Updated asset: {tag}",
                    entity_type="ASSET",
                    entity_id=existing_asset.id,
                    entity_tag=tag,
                    correlation_id=correlation_id,
                    details={"row": row_idx, "changes": asset_data},
                )

                # NEW: Create version for rollback support
                try:
                    versioning_service.create_version(
                        asset=existing_asset,
                        user_id=user_id,
                        change_reason=f"CSV Import: {file.filename}",
                        batch_id=batch_id,
                    )
                except Exception as ve:
                    print(f"Warning: Failed to create version for {tag}: {ve}")

                # Sync to Metamodel
                try:
                    MetamodelService.create_node_from_asset(db, existing_asset)
                except Exception as e:
                    import traceback

                    traceback.print_exc()
                    print(f"Warning: Failed to create MetamodelNode for {tag}: {str(e)}")

            else:
                # Create
                if "type" not in asset_data:
                    summary["errors"].append(
                        CSVRowError(row=row_idx, tag=tag, error="Missing required field: type").dict()
                    )
                    summary["failed"] += 1
                    continue

                new_asset = Asset(**asset_data, project_id=project_id)
                db.add(new_asset)
                db.flush()  # Get the ID
                summary["created"] += 1
                # Log creation (legacy)
                ActionLogger.log(
                    db=db,
                    action_type=ActionType.CREATE,
                    description=f"Created asset: {tag}",
                    project_id=project_id,
                    parent_id=import_log.id,
                    entity_type="ASSET",
                    entity_id=uuid.UUID(new_asset.id),
                    details={"tag": tag, "type": asset_data.get("type")},
                )

                # NEW: Log to WorkflowLogger for real-time traceability
                workflow_logger.log_create(
                    source=LogSource.IMPORT,
                    message=f"Created asset: {tag}",
                    entity_type="ASSET",
                    entity_id=new_asset.id,
                    entity_tag=tag,
                    correlation_id=correlation_id,
                    details={"type": asset_data.get("type"), "row": row_idx},
                )

                # NEW: Create initial version for rollback support
                try:
                    versioning_service.create_initial_version(
                        asset=new_asset,
                        user_id=user_id,
                        batch_id=batch_id,
                    )
                except Exception as ve:
                    print(f"Warning: Failed to create initial version for {tag}: {ve}")

                # Sync to Metamodel
                try:
                    MetamodelService.create_node_from_asset(db, new_asset)
                except Exception as e:
                    import traceback

                    traceback.print_exc()
                    print(f"Warning: Failed to create MetamodelNode for {tag}: {str(e)}")

        except (SynapseValidationError, DatabaseError) as e:
            error_msg = e.message if hasattr(e, 'message') else str(e)
            summary["errors"].append(
                CSVRowError(row=row_idx, tag=tag, error=error_msg).dict()
            )
            summary["failed"] += 1
            ActionLogger.log(
                db=db,
                action_type=ActionType.ERROR,
                description=f"Import error for {tag}: {error_msg}",
                project_id=project_id,
                parent_id=import_log.id,
                entity_type="ASSET",
                details={"row": row_idx, "error": error_msg},
            )
        except Exception as e:
            # Unexpected error - log and continue
            import traceback

            traceback.print_exc()
            error_msg = f"System error: {str(e)}"
            summary["errors"].append(
                CSVRowError(row=row_idx, tag=tag if 'tag' in locals() else None, error=error_msg).dict()
            )
            summary["failed"] += 1
            ActionLogger.log(
                db=db,
                action_type=ActionType.ERROR,
                description=f"Unexpected import error for row {row_idx}: {str(e)}",
                project_id=project_id,
                parent_id=import_log.id,
                entity_type="ASSET",
                details={"row": row_idx, "error": str(e)},
            )

    db.commit()

    # Update parent log with summary
    import_log.details = {
        "filename": file.filename,
        "created": summary["created"],
        "updated": summary["updated"],
        "errors": len(summary["errors"]),
        "mapping": column_map
    }

    # NEW: Complete batch operation and workflow
    affected_count = summary["created"] + summary["updated"]
    batch_manager.complete_batch(batch_id, affected_assets=affected_count)

    if summary["failed"] > 0:
        workflow_logger.fail_workflow(
            correlation_id=correlation_id,
            error=f"{summary['failed']} rows failed to import",
        )
    else:
        workflow_logger.complete_workflow(
            correlation_id=correlation_id,
            details={
                "created": summary["created"],
                "updated": summary["updated"],
                "total_rows": summary["total_rows"],
            },
        )

    db.commit()

    # ✨ Auto-execute rules after import if assets were created
    if summary["created"] > 0:
        try:
            import time

            from app.services.rule_engine import RuleEngine

            rule_start_time = time.time()

            rule_log = ActionLogger.log(
                db=db,
                action_type=ActionType.RULE_EXECUTION,
                description=f"Auto-executing rules after CSV import ({file.filename})",
                project_id=project_id,
                parent_id=import_log.id,
                details={"trigger": "csv_import", "new_assets": summary["created"]},
            )

            # Execute all rules
            rule_result = RuleEngine.apply_rules(db, project_id)

            # Update summary with rule execution results
            summary["rules_executed"] = rule_result.get("total_rules", 0)
            summary["child_assets_created"] = rule_result.get("actions_taken", 0)
            summary["rule_execution_time_ms"] = int((time.time() - rule_start_time) * 1000)

            # Update log with results
            rule_log.details.update(
                {
                    "rules_executed": rule_result.get("total_rules", 0),
                    "assets_created": rule_result.get("actions_taken", 0),
                    "time_ms": summary["rule_execution_time_ms"],
                }
            )
            db.commit()

        except RuleExecutionError as e:
            summary["rule_execution_error"] = e.message
            ActionLogger.log(
                db=db,
                action_type=ActionType.ERROR,
                description=f"Rule auto-execution failed: {e.message}",
                project_id=project_id,
                parent_id=import_log.id,
            )
            db.commit()
        except Exception as e:
            # Unexpected rule execution error
            import traceback

            traceback.print_exc()
            summary["rule_execution_error"] = "Rule execution failed"
            import traceback

            traceback.print_exc()
            summary["rule_execution_error"] = str(e)
            ActionLogger.log(
                db=db,
                action_type=ActionType.ERROR,
                description=f"Rule auto-execution failed: {str(e)}",
                project_id=project_id,
                parent_id=import_log.id,
            )
            db.commit()

    # Calculate success status
    summary["success"] = summary["failed"] == 0

    return ImportSummaryResponse(**summary)


@router.post("/dev-import", response_model=ImportSummaryResponse, status_code=200)
async def import_dev_assets_csv(
    project_id: str = Header(..., alias="X-Project-ID"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    """
    Development endpoint to import a CSV file residing on the server.
    Useful for quick testing without re-uploading files.

    **Note:** This endpoint is for development only. It reads from `/app/mock_data/assets.csv`.
    """
    file_path = "backend/mock_data/assets.csv"
    if not os.path.exists(file_path):
        # Fallback for docker container path
        file_path = "/app/mock_data/assets.csv"

    if not os.path.exists(file_path):
        raise FileValidationError("mock_data/assets.csv", f"File not found at {file_path}")

    with open(file_path, "rb") as f:
        # Create a mock UploadFile object or just reuse logic?
        # Reusing logic is better but requires refactoring.
        # For now, let's just copy the logic or call the function if possible.
        # Since `import_assets_csv` expects UploadFile, let's construct one?
        # Or better, extract the logic.

        # Let's extract logic to a service function in a future refactor.
        # For now, to be safe and quick, I'll read the content and duplicate the parsing logic
        # (or better, wrap it in a helper function right here).

        content = f.read()
        decoded = content.decode("utf-8-sig")
        csv_reader = csv.DictReader(io.StringIO(decoded))

        summary = {
            "created": 0,
            "updated": 0,
            "failed": 0,
            "errors": [],
            "total_rows": 0,
        }

        # Create parent log for this dev import
        import_log = ActionLogger.log(
            db=db,
            action_type=ActionType.CREATE,
            description="Dev CSV Import: mock_data/assets.csv",
            project_id=project_id,
            entity_type="IMPORT",
            details={"filename": "mock_data/assets.csv", "source": "dev-import"},
        )

        # Helper to parse nested keys like "electrical.voltage"
        def set_nested(d, keys, value):
            for key in keys[:-1]:
                d = d.setdefault(key, {})
            d[keys[-1]] = value

        for row_idx, row in enumerate(csv_reader):
            summary["total_rows"] += 1
            try:
                # 1. Identify Asset
                asset_id = row.get("id")
                tag = row.get("tag")

                if not tag:
                    summary["errors"].append(
                        CSVRowError(row=row_idx, tag=None, error="Missing required field: tag").dict()
                    )
                    summary["failed"] += 1
                    continue

                # 2. Prepare Data Structure
                asset_data = {
                    "tag": tag,
                    "description": row.get("description"),
                    "area": row.get("area"),
                    "system": row.get("system"),
                    "manufacturer_part_id": row.get("manufacturer_part_id"),
                    "location_id": row.get("location_id") or None,
                    "electrical": {},
                    "process": {},
                    "purchasing": {},
                }

                # Enums
                if row.get("type"):
                    asset_data["type"] = row.get("type")
                if row.get("io_type"):
                    asset_data["io_type"] = row.get("io_type")

                # Nested Fields
                for key, value in row.items():
                    if key and "." in key and value:
                        parts = key.split(".")
                        if parts[0] in ["electrical", "process", "purchasing"]:
                            set_nested(asset_data, parts, value)

                # 3. Find Existing
                existing_asset = None
                if asset_id:
                    existing_asset = (
                        db.query(Asset)
                        .filter(Asset.id == asset_id, Asset.project_id == project_id)
                        .first()
                    )

                if not existing_asset:
                    existing_asset = (
                        db.query(Asset)
                        .filter(Asset.tag == tag, Asset.project_id == project_id)
                        .first()
                    )

                # 4. Update or Create
                if existing_asset:
                    for key, value in asset_data.items():
                        if value is not None:
                            setattr(existing_asset, key, value)
                    summary["updated"] += 1
                    # Log update
                    ActionLogger.log(
                        db=db,
                        action_type=ActionType.UPDATE,
                        description=f"Updated asset: {tag}",
                        project_id=project_id,
                        parent_id=import_log.id,
                        entity_type="ASSET",
                        entity_id=uuid.UUID(existing_asset.id),
                        details={"tag": tag, "type": asset_data.get("type")},
                    )

                    # Sync to Metamodel
                    try:
                        MetamodelService.create_node_from_asset(db, existing_asset)
                    except Exception as e:
                        import traceback

                        traceback.print_exc()
                        print(f"Warning: Failed to create MetamodelNode for {tag}: {str(e)}")

                else:
                    if "type" not in asset_data:
                        summary["errors"].append(
                            CSVRowError(row=row_idx, tag=tag, error="Missing required field: type").dict()
                        )
                        summary["failed"] += 1
                        continue

                    new_asset = Asset(**asset_data, project_id=project_id)
                    db.add(new_asset)
                    db.flush()  # Get the ID
                    summary["created"] += 1
                    # Log creation
                    ActionLogger.log(
                        db=db,
                        action_type=ActionType.CREATE,
                        description=f"Created asset: {tag}",
                        project_id=project_id,
                        parent_id=import_log.id,
                        entity_type="ASSET",
                        entity_id=uuid.UUID(new_asset.id),
                        details={"tag": tag, "type": asset_data.get("type")},
                    )

                    # Sync to Metamodel
                    try:
                        MetamodelService.create_node_from_asset(db, new_asset)
                    except Exception as e:
                        import traceback

                        traceback.print_exc()
                        print(f"Warning: Failed to create MetamodelNode for {tag}: {str(e)}")

            except (SynapseValidationError, DatabaseError) as e:
                import traceback

                traceback.print_exc()
                error_msg = e.message if hasattr(e, 'message') else str(e)
                summary["errors"].append(
                    CSVRowError(row=row_idx, tag=tag, error=error_msg).dict()
                )
                summary["failed"] += 1
                ActionLogger.log(
                    db=db,
                    action_type=ActionType.ERROR,
                    description=f"Dev import error for {tag}: {error_msg}",
                    project_id=project_id,
                    parent_id=import_log.id,
                    entity_type="ASSET",
                    details={"row": row_idx, "error": error_msg},
                )
            except Exception as e:
                # Unexpected error
                import traceback

                traceback.print_exc()
                error_msg = f"System error: {str(e)}"
                summary["errors"].append(
                    CSVRowError(row=row_idx, tag=tag if 'tag' in locals() else None, error=error_msg).dict()
                )
                summary["failed"] += 1
                ActionLogger.log(
                    db=db,
                    action_type=ActionType.ERROR,
                    description=f"Dev import error for {tag}: {error_msg}",
                    project_id=project_id,
                    parent_id=import_log.id,
                    entity_type="ASSET",
                    details={"row": row_idx, "error": error_msg},
                )

        db.commit()

        # Update parent log with summary
        import_log.details = {
            "filename": "mock_data/assets.csv",
            "source": "dev-import",
            "created": summary["created"],
            "updated": summary["updated"],
            "errors": len(summary["errors"]),
        }
        db.commit()

        # ✨ NEW: Auto-execute rules after import if assets were created
        if summary["created"] > 0:
            try:
                import time

                from app.services.rule_engine import RuleEngine

                rule_start_time = time.time()

                rule_log = ActionLogger.log(
                    db=db,
                    action_type=ActionType.RULE_EXECUTION,
                    description="Auto-executing rules after dev-import",
                    project_id=project_id,
                    parent_id=import_log.id,
                    details={"trigger": "dev_import", "new_assets": summary["created"]},
                )

                # Execute all rules
                rule_result = RuleEngine.apply_rules(db, project_id)

                # Update summary with rule execution results
                summary["rules_executed"] = rule_result.get("total_rules", 0)
                summary["child_assets_created"] = rule_result.get("actions_taken", 0)
                summary["rule_execution_time_ms"] = int((time.time() - rule_start_time) * 1000)

                # Update log with results
                rule_log.details.update(
                    {
                        "rules_executed": rule_result.get("total_rules", 0),
                        "assets_created": rule_result.get("actions_taken", 0),
                        "time_ms": summary["rule_execution_time_ms"],
                    }
                )
                db.commit()

            except RuleExecutionError as e:
                summary["rule_execution_error"] = e.message
                ActionLogger.log(
                    db=db,
                    action_type=ActionType.ERROR,
                    description=f"Rule auto-execution failed: {e.message}",
                    project_id=project_id,
                    parent_id=import_log.id,
                )
                db.commit()
            except Exception as e:
                # Unexpected rule execution error
                import traceback

                traceback.print_exc()
                summary["rule_execution_error"] = "Rule execution failed"
                import traceback

                traceback.print_exc()
                summary["rule_execution_error"] = str(e)
                ActionLogger.log(
                    db=db,
                    action_type=ActionType.ERROR,
                    description=f"Rule auto-execution failed: {str(e)}",
                    project_id=project_id,
                    parent_id=import_log.id,
                )
                db.commit()

        # Calculate success status
        summary["success"] = summary["failed"] == 0

        return ImportSummaryResponse(**summary)
