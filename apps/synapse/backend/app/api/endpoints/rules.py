"""
Rule Management API Endpoints

Provides CRUD operations for database-driven engineering rules.
Supports rule testing, execution logs, and bulk operations.
"""

from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.core.database import get_db
from app.core.exceptions import NotFoundError
from app.core.exceptions import ValidationError as SynapseValidationError
from app.models.action_log import ActionType  # Import ActionType from model
from app.models.auth import User
from app.models.models import Asset  # Unified model!
from app.models.rules import RuleDefinition, RuleExecution
from app.schemas.rule import (
    RuleCreate,
    RuleExecuteRequest,
    RuleExecutionResponse,
    RuleExecutionSummary,
    RuleListResponse,
    RuleResponse,
    RuleTestRequest,
    RuleTestResponse,
    RuleTestResult,
    RuleUpdate,
)
from app.services.rule_executor import RuleExecutor

router = APIRouter(prefix="/api/v1/rules", tags=["rules"])


# ============================================================================
# Rule CRUD Operations
# ============================================================================


@router.get("", response_model=RuleListResponse)
def list_rules(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    source: str | None = None,
    discipline: str | None = None,
    action_type: str | None = None,
    is_active: bool | None = None,
    search: str | None = None,
):
    """
    List all rules with pagination and filters.

    Query parameters:
    - page: Page number (default 1)
    - page_size: Items per page (default 50, max 100)
    - source: Filter by FIRM, COUNTRY, PROJECT, CLIENT
    - discipline: Filter by discipline (ELECTRICAL, AUTOMATION, etc.)
    - action_type: Filter by action type
    - is_active: Filter by active status
    - search: Search in rule name/description
    """
    query = db.query(RuleDefinition)

    # Apply filters
    if source:
        query = query.filter(RuleDefinition.source == source)
    if discipline:
        query = query.filter(RuleDefinition.discipline == discipline)
    if action_type:
        query = query.filter(RuleDefinition.action_type == action_type)
    if is_active is not None:
        query = query.filter(RuleDefinition.is_active == is_active)
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                RuleDefinition.name.ilike(search_pattern),
                RuleDefinition.description.ilike(search_pattern),
            )
        )

    # Get total count
    total = query.count()

    # Apply pagination and sorting (highest priority first)
    rules = (
        query.order_by(RuleDefinition.priority.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return RuleListResponse(total=total, page=page, page_size=page_size, rules=rules)


@router.get("/{rule_id}", response_model=RuleResponse)
def get_rule(
    rule_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a single rule by ID"""
    rule = db.query(RuleDefinition).filter(RuleDefinition.id == rule_id).first()

    if not rule:
        raise NotFoundError("Rule", rule_id)

    return rule


@router.post("", response_model=RuleResponse, status_code=201)
def create_rule(
    rule_data: RuleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new rule.

    Auto-assigns priority based on source if not provided:
    - FIRM: 10
    - COUNTRY: 30
    - PROJECT: 50
    - CLIENT: 100
    """
    # Create rule instance
    rule = RuleDefinition(
        name=rule_data.name,
        description=rule_data.description,
        source=rule_data.source,
        source_id=rule_data.source_id,
        priority=rule_data.priority,
        discipline=rule_data.discipline,
        action_type=rule_data.action_type,
        condition=rule_data.condition,
        action=rule_data.action,
        is_active=rule_data.is_active,
        created_by=current_user.id,
    )

    db.add(rule)
    db.commit()
    db.refresh(rule)

    return rule


@router.put("/{rule_id}", response_model=RuleResponse)
def update_rule(
    rule_id: str,
    rule_data: RuleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update an existing rule.

    Only provided fields will be updated.
    Version is incremented on each update.
    """
    rule = db.query(RuleDefinition).filter(RuleDefinition.id == rule_id).first()

    if not rule:
        raise NotFoundError("Rule", rule_id)

    # Update only provided fields
    update_data = rule_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(rule, key, value)

    # Increment version
    rule.version += 1
    rule.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(rule)

    return rule


@router.delete("/{rule_id}", status_code=204)
def delete_rule(
    rule_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a rule.

    Warning: This will cascade delete all execution logs for this rule.
    Consider deactivating instead by setting is_active=false.
    """
    rule = db.query(RuleDefinition).filter(RuleDefinition.id == rule_id).first()

    if not rule:
        raise NotFoundError("Rule", rule_id)

    db.delete(rule)
    db.commit()

    return None


@router.post("/{rule_id}/toggle", response_model=RuleResponse)
def toggle_rule(
    rule_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Toggle rule active status (activate/deactivate)"""
    rule = db.query(RuleDefinition).filter(RuleDefinition.id == rule_id).first()

    if not rule:
        raise NotFoundError("Rule", rule_id)

    rule.is_active = not rule.is_active
    db.commit()
    db.refresh(rule)

    return rule


# ============================================================================
# Rule Testing
# ============================================================================


@router.post("/{rule_id}/test", response_model=RuleTestResponse)
def test_rule(
    rule_id: str,
    test_request: RuleTestRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Test a rule against sample assets without persisting changes.

    Useful for validating rule logic before activation.

    Example request:
    {
      "sample_assets": [
        {"tag": "310-PP-001", "type": "PUMP", "properties": {"pump_type": "CENTRIFUGAL"}},
        {"tag": "310-TK-001", "type": "TANK"}
      ]
    }
    """
    rule = db.query(RuleDefinition).filter(RuleDefinition.id == rule_id).first()

    if not rule:
        raise NotFoundError("Rule", rule_id)

    executor = RuleExecutor(db, "test-project")
    test_results: list[RuleTestResult] = []

    for sample_asset in test_request.sample_assets:
        # Create temporary Asset (not persisted)
        temp_asset = Asset(
            tag=sample_asset.get("tag", "UNNAMED"),
            type=sample_asset.get("type", "UNKNOWN"),
            project_id="test-project",
            properties=sample_asset.get("properties", {}),
        )

        # Evaluate condition
        condition_matched = executor._evaluate_condition(rule.condition, temp_asset)

        result = RuleTestResult(
            asset_tag=temp_asset.tag,
            condition_matched=condition_matched,
        )

        if condition_matched:
            # Determine what would be created/set
            if rule.action_type.value == "CREATE_CHILD":
                action = rule.action.get("create_child", {})
                child_type = action.get("type", "UNKNOWN")
                naming = action.get("naming", "{parent_tag}-{type}")
                child_name = naming.replace("{parent_tag}", temp_asset.tag).replace(
                    "{type}", child_type[:1]
                )
                result.would_create = f"{child_name} ({child_type})"
                result.reason = f"Condition matched: asset type '{temp_asset.type}'"
            elif rule.action_type.value == "SET_PROPERTY":
                action = rule.action.get("set_property", {})
                result.would_set = action
                result.reason = f"Would set properties: {', '.join(action.keys())}"
            else:
                result.reason = f"Action type {rule.action_type.value}"
        else:
            # Explain why it didn't match
            if "asset_type" in rule.condition:
                expected_type = rule.condition["asset_type"]
                if temp_asset.type != expected_type:
                    result.reason = (
                        f"Asset type '{temp_asset.type}' does not match '{expected_type}'"
                    )
            else:
                result.reason = "Property filters did not match"

        test_results.append(result)

    return RuleTestResponse(rule_id=rule.id, rule_name=rule.name, test_results=test_results)


# ============================================================================
# Rule Execution Logs
# ============================================================================


@router.get("/executions/logs", response_model=list[RuleExecutionResponse])
def get_execution_logs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    project_id: str | None = None,
    rule_id: str | None = None,
    action_type: str | None = None,
    limit: int = Query(100, ge=1, le=500),
):
    """
    Get rule execution audit logs.

    Query parameters:
    - project_id: Filter by project
    - rule_id: Filter by specific rule
    - action_type: Filter by action type (CREATE, UPDATE, SKIP, ERROR)
    - limit: Max results (default 100, max 500)
    """
    query = db.query(RuleExecution)

    if project_id:
        query = query.filter(RuleExecution.project_id == project_id)
    if rule_id:
        query = query.filter(RuleExecution.rule_id == rule_id)
    if action_type:
        query = query.filter(RuleExecution.action_type == action_type)

    executions = query.order_by(RuleExecution.timestamp.desc()).limit(limit).all()

    # Enrich with rule names
    results = []
    for execution in executions:
        rule = db.query(RuleDefinition).filter(RuleDefinition.id == execution.rule_id).first()
        result = RuleExecutionResponse.from_orm(execution)
        if rule:
            result.rule_name = rule.name
        results.append(result)

    return results


@router.get("/executions/summary", response_model=RuleExecutionSummary)
def get_execution_summary(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get execution summary statistics for a project.

    Returns aggregate stats: total executions, actions taken, skipped, errors.
    """
    executions = db.query(RuleExecution).filter(RuleExecution.project_id == project_id).all()

    total_executions = len(executions)
    actions_taken = len([e for e in executions if e.action_type in ["CREATE", "UPDATE", "LINK"]])
    skipped = len([e for e in executions if e.action_type == "SKIP"])
    errors = len([e for e in executions if e.action_type == "ERROR"])

    # Get unique rules and assets
    total_rules = len({e.rule_id for e in executions})
    total_assets = len({e.asset_id for e in executions if e.asset_id})

    # Sum execution time
    time_elapsed_ms = sum(e.execution_time_ms or 0 for e in executions)

    return RuleExecutionSummary(
        total_rules=total_rules,
        total_assets=total_assets,
        total_executions=total_executions,
        actions_taken=actions_taken,
        skipped=skipped,
        errors=errors,
        time_elapsed_ms=time_elapsed_ms,
    )


# ============================================================================
# Bulk Operations
# ============================================================================


@router.post("/bulk/toggle", response_model=dict)
def bulk_toggle_rules(
    rule_ids: list[str],
    activate: bool,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Bulk activate or deactivate multiple rules.

    Body:
    - rule_ids: List of rule IDs
    - activate: true to activate, false to deactivate
    """
    rules = db.query(RuleDefinition).filter(RuleDefinition.id.in_(rule_ids)).all()

    if not rules:
        raise SynapseValidationError("rule_ids", "No rules found with provided IDs")

    for rule in rules:
        rule.is_active = activate

    db.commit()

    return {"updated": len(rules), "is_active": activate}


@router.delete("/bulk/delete", status_code=204)
def bulk_delete_rules(
    rule_ids: list[str],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Bulk delete multiple rules.

    Warning: This will cascade delete all execution logs for these rules.
    """
    rules = db.query(RuleDefinition).filter(RuleDefinition.id.in_(rule_ids)).all()

    if not rules:
        raise SynapseValidationError("rule_ids", "No rules found with provided IDs")

    for rule in rules:
        db.delete(rule)

    db.commit()

    return None


# ============================================================================
# Conflict Detection
# ============================================================================


@router.get("/conflicts/{project_id}", response_model=dict)
def detect_rule_conflicts(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Detect rule conflicts for a project.

    Returns conflicts where multiple rules target same asset property,
    including enforcement violations.
    """
    from app.services.enhanced_rule_engine import EnhancedRuleEngine

    result = EnhancedRuleEngine.load_and_resolve_rules(db, project_id)

    return {
        "project_id": project_id,
        "total_rules": len(result["rules"]),
        "conflicts_count": len(result["conflicts_detected"]),
        "enforcement_violations_count": len(result["enforcement_violations"]),
        "conflicts": result["conflicts_detected"],
        "enforcement_violations": result["enforcement_violations"],
    }


# ============================================================================
# Rule Execution (Manual Triggers)
# ============================================================================


@router.post("/execute", response_model=RuleExecutionSummary)
def execute_all_rules(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Execute all active rules for a project.

    Workflow:
    1. Load all active rules sorted by priority
    2. Get all assets in project
    3. For each rule × asset: evaluate condition and execute action
    4. Log all executions to action_log table
    5. Return summary statistics

    Returns:
        - total_rules: Number of rules processed
        - total_assets: Number of assets evaluated
        - total_executions: Total condition checks
        - actions_taken: Successful creates/updates
        - skipped: Assets that didn't match conditions
        - errors: Failed executions
        - time_elapsed_ms: Execution time
    """
    import time

    from app.services.action_logger import ActionLogger

    start_time = time.time()

    # Create root action log
    root_log = ActionLogger.log(
        db,
        ActionType.RULE_EXECUTION,
        f"Manual execution of all rules for project {project_id}",
        project_id=project_id,
    )

    # Execute via RuleEngine
    from app.services.rule_engine import RuleEngine

    result = RuleEngine.apply_rules(db, project_id)

    # Update root log with results
    root_log.details = {
        "execution_mode": "execute_all",
        "total_rules": result["total_rules"],
        "actions_taken": result["actions_taken"],
        "time_ms": int((time.time() - start_time) * 1000),
    }
    db.commit()

    return RuleExecutionSummary(**result)


@router.post("/{rule_id}/execute", response_model=dict)
def execute_single_rule(
    rule_id: str,
    request: RuleExecuteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Execute a single rule on all assets or selected assets.

    Use Cases:
    - Test new CLIENT rule on 5 sample pumps
    - Re-apply voltage rule after country code change
    - Apply custom rule to specific equipment type

    Args:
        rule_id: UUID of rule to execute
        asset_ids: Optional list of asset IDs (if omitted, applies to all)
        project_id: Required if asset_ids not provided

    Returns:
        - rule_id, rule_name
        - assets_processed: Number of assets evaluated
        - actions_taken: Successful creates/updates
        - skipped: Assets that didn't match conditions
        - executions: List of detailed results per asset
    """
    from app.services.action_logger import ActionLogger

    # Validate rule exists
    rule = (
        db.query(RuleDefinition)
        .filter(RuleDefinition.id == rule_id, RuleDefinition.is_active.is_(True))
        .first()
    )

    if not rule:
        raise NotFoundError("Rule", rule_id)

    # Get target assets from unified table
    if request.asset_ids:
        assets = db.query(Asset).filter(Asset.id.in_(request.asset_ids)).all()
        project_id = assets[0].project_id if assets else request.project_id
    else:
        if not request.project_id:
            raise SynapseValidationError("project_id", "Required when asset_ids not provided")
        project_id = request.project_id

        # Query all assets for project
        assets = db.query(Asset).filter(Asset.project_id == project_id).all()

    # Create parent log
    parent_log = ActionLogger.log(
        db,
        ActionType.RULE_EXECUTION,
        f"Executing rule '{rule.name}' on {len(assets)} assets",
        project_id=project_id,
        details={
            "rule_id": rule_id,
            "execution_mode": "single_rule_selective" if request.asset_ids else "single_rule_all",
            "asset_count": len(assets),
        },
    )

    # Execute rule on each asset
    executor = RuleExecutor(db, project_id)
    executions = []
    actions_taken = 0
    skipped = 0

    for asset in assets:
        execution = executor.execute_rule(rule, asset)
        executions.append(
            {
                "asset_id": str(asset.id),
                "asset_tag": asset.tag,
                "matched": execution.condition_matched,
                "action_type": execution.action_type,
                "action_taken": execution.action_taken,
                "created_entity_id": str(execution.created_entity_id)
                if execution.created_entity_id
                else None,
            }
        )

        if execution.action_type == "CREATE":
            actions_taken += 1
            # Log child action
            ActionLogger.log(
                db,
                ActionType.CREATE,
                execution.action_taken,
                project_id=project_id,
                parent_id=parent_log.id,
                entity_type="NODE",
                entity_id=execution.created_entity_id,
                discipline=asset.discipline,
            )
        elif execution.action_type == "SKIP":
            skipped += 1

    db.commit()

    return {
        "rule_id": rule_id,
        "rule_name": rule.name,
        "assets_processed": len(assets),
        "actions_taken": actions_taken,
        "skipped": skipped,
        "executions": executions[:100],  # Limit response size
    }


@router.post("/{rule_id}/debug", tags=["debugging"])
def debug_rule_evaluation(
    rule_id: str,
    asset_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Debug why a rule did or didn't match an asset.

    Returns detailed decision tree showing:
    - Each condition check (pass/fail)
    - Asset properties vs expected values
    - Explanation of why rule matched/failed
    """
    # Get rule
    rule = db.query(RuleDefinition).filter(RuleDefinition.id == rule_id).first()
    if not rule:
        raise NotFoundError("Rule", rule_id)

    # Get asset
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise NotFoundError("Asset", asset_id)

    # Evaluate condition step by step
    condition = rule.condition
    decision_tree = []
    overall_match = True

    # Check asset_type
    if "asset_type" in condition:
        asset_type_match = asset.type == condition["asset_type"]
        decision_tree.append(
            {
                "check": "asset_type",
                "expected": condition["asset_type"],
                "actual": asset.type,
                "passed": asset_type_match,
                "explanation": (
                f"Asset type '{asset.type}' "
                f"{'matches' if asset_type_match else 'does not match'} "
                f"expected '{condition['asset_type']}'"
            ),
            }
        )
        if not asset_type_match:
            overall_match = False

    # Check node_type (alternative to asset_type)
    if "node_type" in condition:
        node_type_match = asset.type == condition["node_type"]
        decision_tree.append(
            {
                "check": "node_type",
                "expected": condition["node_type"],
                "actual": asset.type,
                "passed": node_type_match,
                "explanation": (
                    f"Node type '{asset.type}' "
                    f"{'matches' if node_type_match else 'does not match'} "
                    f"expected '{condition['node_type']}'"
                ),
            }
        )
        if not node_type_match:
            overall_match = False

    # Check property filters
    if "property_filters" in condition and condition["property_filters"]:
        for i, filter_item in enumerate(condition["property_filters"]):
            key = filter_item["key"]
            op = filter_item["op"]
            expected_value = filter_item["value"]

            # Get actual value from asset
            asset_value = asset.properties.get(key) if asset.properties else None

            # Evaluate operator
            if op == "==":
                passed = asset_value == expected_value
                explanation = (
                    f"Property '{key}' = '{asset_value}' "
                    f"{'==' if passed else '!='} '{expected_value}'"
                )
            elif op == "!=":
                passed = asset_value != expected_value
                explanation = (
                    f"Property '{key}' = '{asset_value}' "
                    f"{'!=' if passed else '=='} '{expected_value}'"
                )
            elif op == ">":
                passed = asset_value is not None and asset_value > expected_value
                explanation = (
                    f"Property '{key}' = '{asset_value}' "
                    f"{'>' if passed else '<='} '{expected_value}'"
                )
            elif op == "<":
                passed = asset_value is not None and asset_value < expected_value
                explanation = (
                    f"Property '{key}' = '{asset_value}' "
                    f"{'<' if passed else '>='} '{expected_value}'"
                )
            elif op == "in":
                passed = (
                    asset_value in expected_value if isinstance(expected_value, list) else False
                )
                explanation = (
                    f"Property '{key}' = '{asset_value}' "
                    f"{'in' if passed else 'not in'} {expected_value}"
                )
            elif op == "contains":
                passed = (
                    expected_value in asset_value if isinstance(asset_value, str | list) else False
                )
                explanation = (
                    f"Property '{key}' = '{asset_value}' "
                    f"{'contains' if passed else 'does not contain'} '{expected_value}'"
                )
            else:
                passed = False
                explanation = f"Unknown operator '{op}'"

            decision_tree.append(
                {
                    "check": f"property_filter[{i}]",
                    "property": key,
                    "operator": op,
                    "expected": expected_value,
                    "actual": asset_value,
                    "passed": passed,
                    "explanation": explanation,
                }
            )

            if not passed:
                overall_match = False

    # Build recommendation
    recommendation = ""
    if not overall_match:
        failed_checks = [check for check in decision_tree if not check["passed"]]
        if failed_checks:
            recommendation = "To make this rule match, you need to:\n"
            for check in failed_checks:
                if check["check"] in ["asset_type", "node_type"]:
                    recommendation += (
                        f"- Change asset type from '{check['actual']}' to '{check['expected']}'\n"
                    )
                elif "property" in check:
                    if check["actual"] is None:
                        recommendation += (
                            f"- Add property '{check['property']}' "
                            f"with value '{check['expected']}'\n"
                        )
                    else:
                        recommendation += (
                            f"- Change property '{check['property']}' "
                            f"from '{check['actual']}' to '{check['expected']}'\n"
                        )

    return {
        "rule_id": rule_id,
        "rule_name": rule.name,
        "asset_id": asset_id,
        "asset_tag": asset.tag,
        "asset_type": asset.type,
        "overall_match": overall_match,
        "decision_tree": decision_tree,
        "asset_properties": asset.properties or {},
        "recommendation": recommendation,
        "action_would_take": rule.action if overall_match else None,
    }
