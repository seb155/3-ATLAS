"""
Enhanced Rule Engine - Conflict Detection and Enforcement

Adds conflict detection and enforcement checking to the existing rule engine.
"""

import json

from sqlalchemy.orm import Session

from app.models.rules import RuleDefinition
from app.services.logger import SystemLog


class RuleConflictResolver:
    """Handles conflict detection and enforcement rules"""

    @staticmethod
    def detect_rule_conflicts(rules: list[RuleDefinition]) -> list[dict]:
        """
        Detect when multiple rules target same asset property.

        Returns conflicts with winning rule and overridden rules.
        """
        conflicts = []

        # Group by (condition, target_property)
        rule_groups = {}
        for rule in rules:
            key = (
                json.dumps(rule.condition, sort_keys=True),
                RuleConflictResolver.extract_target_property(rule.action, rule.action_type.value),
            )
            if key not in rule_groups:
                rule_groups[key] = []
            rule_groups[key].append(rule)

        # Check for conflicts in each group
        for key, group_rules in rule_groups.items():
            if len(group_rules) > 1:
                # Sort by priority to determine winner
                sorted_rules = sorted(group_rules, key=lambda r: r.priority, reverse=True)
                winner = sorted_rules[0]
                losers = sorted_rules[1:]

                for loser in losers:
                    conflict_status = (
                        "enforced_violation" if loser.is_enforced else "valid_override"
                    )

                    conflicts.append(
                        {
                            "winning_rule": {
                                "id": winner.id,
                                "name": winner.name,
                                "source": winner.source.value,
                                "priority": winner.priority,
                                "is_enforced": winner.is_enforced,
                            },
                            "overridden_rule": {
                                "id": loser.id,
                                "name": loser.name,
                                "source": loser.source.value,
                                "priority": loser.priority,
                                "is_enforced": loser.is_enforced,
                            },
                            "conflict_type": "priority_override",
                            "status": conflict_status,
                            "condition": key[0],
                            "target_property": key[1],
                        }
                    )

        return conflicts

    @staticmethod
    def resolve_conflicts_with_enforcement(
        rules: list[RuleDefinition], conflicts: list[dict]
    ) -> list[RuleDefinition]:
        """
        Remove rules that are overridden, unless they are enforced.

        Enforced rules cannot be overridden - the higher priority rule gets blocked instead!
        """
        blocked_rule_ids = set()
        enforcement_violations = []

        for conflict in conflicts:
            loser_id = conflict["overridden_rule"]["id"]
            loser_enforced = conflict["overridden_rule"]["is_enforced"]
            winner_id = conflict["winning_rule"]["id"]

            if loser_enforced:
                # Enforced rule cannot be overridden - block the winner instead!
                blocked_rule_ids.add(winner_id)
                enforcement_violations.append(
                    {
                        "blocked_rule_id": winner_id,
                        "blocked_rule_name": conflict["winning_rule"]["name"],
                        "reason": (
                            f"Cannot override enforced rule: {conflict['overridden_rule']['name']}"
                        ),
                        "enforced_rule_id": loser_id,
                    }
                )

                SystemLog.log(
                    "WARN",
                    f"⚠️ Enforcement violation: Rule '{conflict['winning_rule']['name']}' "
                    f"cannot override enforced rule '{conflict['overridden_rule']['name']}'",
                )
            else:
                # Normal case: lower priority rule is blocked
                blocked_rule_ids.add(loser_id)

                SystemLog.log(
                    "INFO",
                    f"✓ Valid override: Rule '{conflict['winning_rule']['name']}' "
                    f"overrides '{conflict['overridden_rule']['name']}'",
                )

        # Filter out blocked rules
        active_rules = [r for r in rules if r.id not in blocked_rule_ids]

        if enforcement_violations:
            SystemLog.log("WARN", f"Detected {len(enforcement_violations)} enforcement violations")

        return active_rules, enforcement_violations

    @staticmethod
    def extract_target_property(action: dict, action_type: str) -> str:
        """Extract the target property from an action"""
        if action_type == "SET_PROPERTY":
            if "set_property" in action:
                props = action["set_property"]
                if isinstance(props, dict):
                    # Return first property key as target
                    return list(props.keys())[0] if props else "unknown"
            return "properties"

        elif action_type == "CREATE_CHILD":
            if "create_child" in action:
                return action["create_child"].get("type", "unknown_child")
            return "child"

        elif action_type == "CREATE_CABLE":
            if "create_cable" in action:
                return action["create_cable"].get("cable_type", "unknown_cable")
            return "cable"

        return "unknown"


class EnhancedRuleEngine:
    """Enhanced rule engine with conflict detection and enforcement"""

    @staticmethod
    def load_and_resolve_rules(db: Session, project_id: str) -> dict:
        """
        Load rules for project and resolve conflicts with enforcement.

        Returns:
            {
                "rules": [RuleDefinition],
                "conflicts_detected": [Dict],
                "enforcement_violations": [Dict]
            }
        """
        from app.services.rule_loader import RuleLoader

        # 1. Load all applicable rules
        all_rules = RuleLoader.load_rules_for_project(db, project_id)

        SystemLog.log("INFO", f"Loaded {len(all_rules)} rules for project {project_id}")

        # 2. Detect conflicts
        conflicts = RuleConflictResolver.detect_rule_conflicts(all_rules)

        if conflicts:
            SystemLog.log("INFO", f"Detected {len(conflicts)} rule conflicts")

        # 3. Resolve conflicts respecting enforcement
        (
            active_rules,
            enforcement_violations,
        ) = RuleConflictResolver.resolve_conflicts_with_enforcement(all_rules, conflicts)

        SystemLog.log(
            "INFO", f"After conflict resolution: {len(active_rules)}/{len(all_rules)} rules active"
        )

        return {
            "rules": active_rules,
            "conflicts_detected": conflicts,
            "enforcement_violations": enforcement_violations,
        }
