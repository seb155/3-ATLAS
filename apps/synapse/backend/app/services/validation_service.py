"""
Validation Service

Aggregates validation results from rule executions.
Provides summary statistics and detailed reports on data quality issues.
"""

from typing import Any

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.models import Asset
from app.models.rules import RuleExecution


class ValidationService:
    """
    Service for querying and aggregating validation results.
    """

    @staticmethod
    def get_validation_summary(db: Session, project_id: str) -> dict[str, Any]:
        """
        Get summary of validation issues for a project.
        """
        # Count errors and warnings
        stats = (
            db.query(RuleExecution.action_type, func.count(RuleExecution.id))
            .filter(
                RuleExecution.project_id == project_id,
                RuleExecution.action_type.in_(["VALIDATION_FAIL", "VALIDATION_WARN"]),
            )
            .group_by(RuleExecution.action_type)
            .all()
        )

        result = {"errors": 0, "warnings": 0, "total_issues": 0}

        for action_type, count in stats:
            if action_type == "VALIDATION_FAIL":
                result["errors"] = count
            elif action_type == "VALIDATION_WARN":
                result["warnings"] = count

        result["total_issues"] = result["errors"] + result["warnings"]
        return result

    @staticmethod
    def get_validation_details(db: Session, project_id: str) -> list[dict[str, Any]]:
        """
        Get detailed list of validation issues.
        """
        issues = (
            db.query(RuleExecution)
            .filter(
                RuleExecution.project_id == project_id,
                RuleExecution.action_type.in_(["VALIDATION_FAIL", "VALIDATION_WARN"]),
            )
            .order_by(RuleExecution.timestamp.desc())
            .all()
        )

        results = []
        for issue in issues:
            # Fetch related asset tag if possible (optimization: join in query)
            asset_tag = "Unknown"
            if issue.asset_id:
                asset = db.query(Asset).filter(Asset.id == issue.asset_id).first()
                if asset:
                    asset_tag = asset.tag

            # Fetch rule name
            rule_name = "Unknown Rule"
            if issue.rule:
                rule_name = issue.rule.name

            results.append(
                {
                    "id": issue.id,
                    "severity": "ERROR" if issue.action_type == "VALIDATION_FAIL" else "WARNING",
                    "message": issue.error_message or issue.action_taken,
                    "asset_id": issue.asset_id,
                    "asset_tag": asset_tag,
                    "rule_id": issue.rule_id,
                    "rule_name": rule_name,
                    "timestamp": issue.timestamp,
                }
            )

        return results
