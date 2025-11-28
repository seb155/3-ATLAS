"""
Unit Tests for Enhanced Rule Engine

Tests conflict detection and enforcement features.
"""

from unittest.mock import Mock

import pytest

from app.models.rules import RuleActionType, RuleSource
from app.services.enhanced_rule_engine import RuleConflictResolver


class TestRuleConflictDetection:
    """Test conflict detection between rules"""

    def test_no_conflicts_when_different_conditions(self):
        """Rules with different conditions should not conflict"""
        rules = [
            Mock(
                id="rule1",
                name="Pump Motor Rule",
                source=RuleSource.FIRM,
                priority=10,
                is_enforced=False,
                action_type=RuleActionType.CREATE_CHILD,
                condition={"asset_type": "PUMP"},
                action={"create_child": {"type": "MOTOR"}},
            ),
            Mock(
                id="rule2",
                name="Tank Level Transmitter Rule",
                source=RuleSource.FIRM,
                priority=10,
                is_enforced=False,
                action_type=RuleActionType.CREATE_CHILD,
                condition={"asset_type": "TANK"},
                action={"create_child": {"type": "LEVEL_TRANSMITTER"}},
            ),
        ]

        conflicts = RuleConflictResolver.detect_rule_conflicts(rules)

        assert len(conflicts) == 0, "Different asset types should not conflict"

    def test_conflict_detected_same_condition_different_actions(self):
        """Rules with same condition but different actions should conflict"""
        rules = [
            Mock(
                id="rule1",
                name="FIRM Default Voltage",
                source=RuleSource.FIRM,
                priority=10,
                is_enforced=False,
                action_type=RuleActionType.SET_PROPERTY,
                condition={"asset_type": "MOTOR"},
                action={"set_property": {"voltage": "460V"}},
            ),
            Mock(
                id="rule2",
                name="Canada CEC Voltage",
                source=RuleSource.COUNTRY,
                priority=30,
                is_enforced=False,
                action_type=RuleActionType.SET_PROPERTY,
                condition={"asset_type": "MOTOR"},
                action={"set_property": {"voltage": "600V"}},
            ),
        ]

        conflicts = RuleConflictResolver.detect_rule_conflicts(rules)

        assert len(conflicts) == 1, "Same condition, different voltage should conflict"
        assert conflicts[0]["winning_rule"]["id"] == "rule2", "Higher priority should win"
        assert (
            conflicts[0]["overridden_rule"]["id"] == "rule1"
        ), "Lower priority should be overridden"

    def test_higher_priority_wins_conflict(self):
        """Rule with higher priority should win conflicts"""
        rules = [
            Mock(
                id="rule_firm",
                name="FIRM Voltage",
                source=RuleSource.FIRM,
                priority=10,
                is_enforced=False,
                action_type=RuleActionType.SET_PROPERTY,
                condition={"asset_type": "MOTOR"},
                action={"set_property": {"voltage": "460V"}},
            ),
            Mock(
                id="rule_client",
                name="CLIENT Custom Voltage",
                source=RuleSource.CLIENT,
                priority=100,
                is_enforced=False,
                action_type=RuleActionType.SET_PROPERTY,
                condition={"asset_type": "MOTOR"},
                action={"set_property": {"voltage": "690V"}},
            ),
        ]

        conflicts = RuleConflictResolver.detect_rule_conflicts(rules)

        assert conflicts[0]["winning_rule"]["priority"] == 100
        assert conflicts[0]["overridden_rule"]["priority"] == 10


class TestRuleEnforcement:
    """Test enforcement of non-negotiable rules"""

    def test_enforced_rule_cannot_be_overridden(self):
        """Enforced rules should block higher priority rules"""
        rules = [
            Mock(
                id="rule_country",
                name="Greece IEC 60364 (Enforced)",
                source=RuleSource.COUNTRY,
                priority=30,
                is_enforced=True,  # Non-negotiable electrical code
                action_type=RuleActionType.SET_PROPERTY,
                condition={"asset_type": "MOTOR"},
                action={"set_property": {"voltage": "400V"}},
            ),
            Mock(
                id="rule_client",
                name="CLIENT Custom Voltage",
                source=RuleSource.CLIENT,
                priority=100,  # Higher priority but cannot override enforced
                is_enforced=False,
                action_type=RuleActionType.SET_PROPERTY,
                condition={"asset_type": "MOTOR"},
                action={"set_property": {"voltage": "690V"}},
            ),
        ]

        conflicts = RuleConflictResolver.detect_rule_conflicts(rules)
        active_rules, violations = RuleConflictResolver.resolve_conflicts_with_enforcement(
            rules, conflicts
        )

        # The CLIENT rule should be blocked
        active_rule_ids = [r.id for r in active_rules]
        assert "rule_country" in active_rule_ids, "Enforced rule should remain active"
        assert "rule_client" not in active_rule_ids, "Higher priority rule should be blocked"
        assert len(violations) == 1, "Should report one enforcement violation"
        assert violations[0]["blocked_rule_id"] == "rule_client"

    def test_normal_override_allowed_without_enforcement(self):
        """Without enforcement, higher priority should override"""
        rules = [
            Mock(
                id="rule_firm",
                name="FIRM Default",
                source=RuleSource.FIRM,
                priority=10,
                is_enforced=False,  # Not enforced
                action_type=RuleActionType.SET_PROPERTY,
                condition={"asset_type": "MOTOR"},
                action={"set_property": {"voltage": "460V"}},
            ),
            Mock(
                id="rule_project",
                name="PROJECT Custom",
                source=RuleSource.PROJECT,
                priority=50,
                is_enforced=False,
                action_type=RuleActionType.SET_PROPERTY,
                condition={"asset_type": "MOTOR"},
                action={"set_property": {"voltage": "575V"}},
            ),
        ]

        conflicts = RuleConflictResolver.detect_rule_conflicts(rules)
        active_rules, violations = RuleConflictResolver.resolve_conflicts_with_enforcement(
            rules, conflicts
        )

        active_rule_ids = [r.id for r in active_rules]
        assert "rule_project" in active_rule_ids, "Higher priority should win"
        assert "rule_firm" not in active_rule_ids, "Lower priority should be overridden"
        assert len(violations) == 0, "No enforcement violations"


class TestPropertyExtraction:
    """Test extraction of target properties from actions"""

    def test_extract_voltage_from_set_property(self):
        """Should extract 'voltage' as target property"""
        action = {"set_property": {"voltage": "600V", "frequency": "60Hz"}}
        result = RuleConflictResolver.extract_target_property(action, "SET_PROPERTY")

        assert result == "voltage", "Should extract first property key"

    def test_extract_child_type_from_create_child(self):
        """Should extract child type"""
        action = {"create_child": {"type": "MOTOR", "naming": "{parent}-M"}}
        result = RuleConflictResolver.extract_target_property(action, "CREATE_CHILD")

        assert result == "MOTOR"

    def test_extract_cable_type_from_create_cable(self):
        """Should extract cable type"""
        action = {"create_cable": {"cable_type": "POWER", "from": "MCC"}}
        result = RuleConflictResolver.extract_target_property(action, "CREATE_CABLE")

        assert result == "POWER"


class TestHierarchyPriority:
    """Test priority hierarchy CLIENT > PROJECT > COUNTRY > FIRM"""

    def test_client_overrides_all(self):
        """CLIENT (100) should override FIRM (10)"""
        rules = [
            Mock(
                id="firm",
                name="FIRM",
                source=RuleSource.FIRM,
                priority=10,
                is_enforced=False,
                action_type=RuleActionType.SET_PROPERTY,
                condition={"asset_type": "MOTOR"},
                action={"set_property": {"voltage": "460V"}},
            ),
            Mock(
                id="client",
                name="CLIENT",
                source=RuleSource.CLIENT,
                priority=100,
                is_enforced=False,
                action_type=RuleActionType.SET_PROPERTY,
                condition={"asset_type": "MOTOR"},
                action={"set_property": {"voltage": "690V"}},
            ),
        ]

        conflicts = RuleConflictResolver.detect_rule_conflicts(rules)

        assert conflicts[0]["winning_rule"]["source"] == "CLIENT"
        assert conflicts[0]["overridden_rule"]["source"] == "FIRM"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
