"""
Enhanced Rule Engine with Database-Driven Rules

Uses RuleLoader to fetch rules by priority and RuleExecutor to apply them.
Maintains backward compatibility with existing mock import workflow.
"""

import time

from sqlalchemy.orm import Session

from app.models.action_log import ActionStatus, ActionType
from app.models.models import Asset  # Use unified Asset model
from app.services.action_logger import ActionLogger
from app.services.logger import SystemLog
from app.services.rule_executor import RuleExecutor


class RuleEngine:
    """
    Database-driven rule engine with hierarchical rule support.

    Replaces hardcoded rules with dynamic database-loaded rules.
    Supports FIRM → COUNTRY → PROJECT → CLIENT priority hierarchy.
    """

    @staticmethod
    def apply_rules(db: Session, project_id: str) -> dict:
        """
        Apply all active rules for a project to its assets.

        Args:
            db: Database session
            project_id: Project ID to apply rules for

        Returns:
            Execution summary with statistics
        """
        start_time = time.time()
        # 0. Start Root Log
        root_log = ActionLogger.log(
            db,
            ActionType.RULE_EXECUTION,
            f"Starting Database-Driven Rule Engine for project {project_id}",
            project_id=project_id,
        )
        # Capture root_log_id early to avoid issues after potential rollbacks
        root_log_id = root_log.id
        SystemLog.log("INFO", f"Starting Database-Driven Rule Engine for project {project_id}...")

        # 1. Load all applicable rules (FIRM + COUNTRY + PROJECT + CLIENT)
        # Use EnhancedRuleEngine to resolve conflicts
        from app.services.enhanced_rule_engine import EnhancedRuleEngine

        resolution_result = EnhancedRuleEngine.load_and_resolve_rules(db, project_id)
        rules = resolution_result["rules"]
        violations = resolution_result["enforcement_violations"]

        if violations:
            ActionLogger.log(
                db,
                ActionType.RULE_EXECUTION,
                f"Skipped {len(violations)} rules due to enforcement violations.",
                project_id=project_id,
                parent_id=root_log_id,
                status=ActionStatus.WARNING,
                details={"violations": violations},
            )

        ActionLogger.log(
            db,
            ActionType.RULE_EXECUTION,
            f"Loaded {len(rules)} active rules after conflict resolution.",
            project_id=project_id,
            parent_id=root_log_id,
        )

        # 2. Get all assets to apply rules to (from unified Asset table)
        assets = db.query(Asset).filter(Asset.project_id == project_id).all()
        ActionLogger.log(
            db,
            ActionType.RULE_EXECUTION,
            f"Found {len(assets)} assets to process.",
            project_id=project_id,
            parent_id=root_log_id,
        )

        # 3. Initialize executor
        executor = RuleExecutor(db, project_id)

        # 4. Apply each rule to each asset
        total_executions = 0
        actions_taken = 0
        skipped = 0
        errors = 0

        for rule in rules:
            rule_log = ActionLogger.log(
                db,
                ActionType.RULE_EXECUTION,
                f"Applying rule: {rule.name}",
                project_id=project_id,
                parent_id=root_log_id,
                details={"priority": rule.priority, "source": rule.source.value},
            )
            # Capture IDs before any potential rollback in executor
            rule_log_id = rule_log.id
            rule_id = rule.id

            for asset in assets:
                # Capture asset info BEFORE execute_rule (which may rollback)
                asset_id = asset.id
                asset_discipline = getattr(asset, 'discipline', None)

                execution = executor.execute_rule(rule, asset)
                total_executions += 1

                if execution.action_type == "CREATE":
                    actions_taken += 1
                    ActionLogger.log(
                        db,
                        ActionType.CREATE,
                        execution.action_taken,
                        project_id=project_id,
                        parent_id=rule_log_id,
                        entity_type="NODE",
                        entity_id=execution.created_entity_id,
                        discipline=asset_discipline,
                        details={"rule_id": rule_id, "asset_id": asset_id},
                    )
                elif execution.action_type == "UPDATE":
                    actions_taken += 1
                    ActionLogger.log(
                        db,
                        ActionType.UPDATE,
                        execution.action_taken,
                        project_id=project_id,
                        parent_id=rule_log_id,
                        entity_type="NODE",
                        entity_id=asset_id,
                        discipline=asset_discipline,
                        details={"rule_id": rule_id, "asset_id": asset_id},
                    )

                elif execution.action_type == "LINK":
                    actions_taken += 1
                    ActionLogger.log(
                        db,
                        ActionType.LINK,
                        execution.action_taken,
                        project_id=project_id,
                        parent_id=rule_log_id,
                        entity_type="EDGE",
                        discipline=asset_discipline,
                        details={"rule_id": rule_id, "asset_id": asset_id},
                    )
                elif execution.action_type == "SKIP":
                    skipped += 1
                elif execution.action_type == "ERROR":
                    errors += 1
                    # Note: Error is already logged in RuleExecution record
                    # ActionLogger.log() skipped to avoid FK issues after rollback

        elapsed_ms = int((time.time() - start_time) * 1000)

        # Try to log completion - may fail if rollback removed parent log
        try:
            ActionLogger.log(
                db,
                ActionType.RULE_EXECUTION,
                (
                    f"Rule Engine completed in {elapsed_ms}ms. "
                    f"Summary: {actions_taken} actions, {errors} errors"
                ),
                project_id=project_id,
                parent_id=root_log_id if errors == 0 else None,  # Don't use parent if errors (may be rolled back)
                status=ActionStatus.COMPLETED if errors == 0 else ActionStatus.FAILED,
            )
        except Exception:
            # If logging fails due to rollback, just skip
            pass

        return {
            "total_rules": len(rules),
            "total_assets": len(assets),
            "total_executions": total_executions,
            "actions_taken": actions_taken,
            "skipped": skipped,
            "errors": errors,
            "time_elapsed_ms": elapsed_ms,
        }

    @staticmethod
    def apply_rules_legacy(db: Session):
        """
        Legacy method for backward compatibility.

        Calls new database-driven engine but without project_id.
        Will use only FIRM-level rules if no project specified.

        DEPRECATED: Use apply_rules(db, project_id) instead.
        """
        SystemLog.log(
            "WARN",
            "Using legacy apply_rules() without project_id. "
            "Consider using apply_rules(db, project_id).",
        )

        # Get first project as fallback (for development)
        from app.models.project import Project

        project = db.query(Project).first()

        if not project:
            SystemLog.log("ERROR", "No project found. Cannot apply rules without project context.")
            return {
                "total_rules": 0,
                "total_assets": 0,
                "total_executions": 0,
                "actions_taken": 0,
                "skipped": 0,
                "errors": 1,
                "time_elapsed_ms": 0,
            }

        return RuleEngine.apply_rules(db, project.id)
