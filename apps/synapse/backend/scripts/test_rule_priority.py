"""
Simple Rule Conflict Verification

Tests the core rule priority system:
- FIRM (10) < COUNTRY (30) < PROJECT (50) < CLIENT (100)
"""
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.core.database import SessionLocal


def cleanup_test_data(db):
    """Remove all test data from previous runs"""
    from app.models.auth import Client, Project
    from app.models.models import Asset
    from app.models.rules import RuleDefinition

    # Delete test rules
    test_rule_names = [
        "TEST_FIRM: Voltage",
        "TEST_COUNTRY: Voltage",
        "TEST_PROJECT: Voltage"
    ]
    for name in test_rule_names:
        db.query(RuleDefinition).filter(RuleDefinition.name.like(f"{name}%")).delete(synchronize_session=False)

    # Delete test assets
    db.query(Asset).filter(Asset.tag.like("TEST-%")).delete(synchronize_session=False)

    # Delete test projects
    test_projects = db.query(Project).filter(Project.name.like("TEST Conflict%")).all()
    for proj in test_projects:
        # Delete assets first (foreign key)
        db.query(Asset).filter(Asset.project_id == proj.id).delete(synchronize_session=False)
        db.delete(proj)

    # Delete test clients
    db.query(Client).filter(Client.name.like("TEST Client%")).delete(synchronize_session=False)

    db.commit()
    print("✓ Cleaned up previous test data")


def test_rule_priority():
    from app.models.auth import Client, Project
    from app.models.models import Asset
    from app.models.rules import RuleActionType, RuleDefinition, RuleSource
    from app.services.enhanced_rule_engine import EnhancedRuleEngine

    db = SessionLocal()
    try:
        # Cleanup first
        cleanup_test_data(db)

        print("\n=== Rule Priority System Test ===\n")

        # Setup: Create client and project
        client = Client(name="TEST Client Priority", contact_email="test@example.com")
        db.add(client)
        db.flush()

        project = Project(
            name="TEST Conflict Priority",
            description="Priority test",
            client_id=client.id
        )
        project.country = "CA"  # Enable COUNTRY rules
        db.add(project)
        db.flush()

        asset = Asset(
            tag="TEST-P-001",
            type="PUMP",
            project_id=project.id,
            properties={"pump_type": "centrifugal"}
        )
        db.add(asset)
        db.commit()

        print(f"Created test project: {project.id}")
        print(f"Created test asset: {asset.tag}")

        # Test 1: COUNTRY should override FIRM
        print("\n--- Test 1: COUNTRY (30) > FIRM (10) ---")

        rule_firm = RuleDefinition(
            name="TEST_FIRM: Voltage 480V",
            source=RuleSource.FIRM,
            priority=10,
            condition={"type": "PUMP"},
            action_type=RuleActionType.SET_PROPERTY,
            action={"set_property": {"voltage": "480V"}},
            is_active=True
        )

        rule_country = RuleDefinition(
            name="TEST_COUNTRY: Voltage 600V",
            source=RuleSource.COUNTRY,
            source_id="CA",
            priority=30,
            condition={"type": "PUMP"},
            action_type=RuleActionType.SET_PROPERTY,
            action={"set_property": {"voltage": "600V"}},
            is_active=True
        )

        db.add_all([rule_firm, rule_country])
        db.commit()

        # Load and resolve
        result = EnhancedRuleEngine.load_and_resolve_rules(db, project.id)
        active_rules = result["rules"]

        active_rule_names = {r.name for r in active_rules}

        if rule_country.name in active_rule_names and rule_firm.name not in active_rule_names:
            print("✅ PASS: COUNTRY rule active, FIRM rule filtered out")
        else:
            print("❌ FAIL: Expected COUNTRY active, FIRM inactive")
            print(f"   Active: {active_rule_names}")

        # Test 2: PROJECT should override COUNTRY
        print("\n--- Test 2: PROJECT (50) > COUNTRY (30) ---")

        rule_project = RuleDefinition(
            name="TEST_PROJECT: Voltage 4160V",
            source=RuleSource.PROJECT,
            source_id=project.id,
            priority=50,
            condition={"type": "PUMP"},
            action_type=RuleActionType.SET_PROPERTY,
            action={"set_property": {"voltage": "4160V"}},
            is_active=True
        )

        db.add(rule_project)
        db.commit()

        result = EnhancedRuleEngine.load_and_resolve_rules(db, project.id)
        active_rules = result["rules"]
        active_rule_names = {r.name for r in active_rules}

        if (rule_project.name in active_rule_names and
            rule_country.name not in active_rule_names and
            rule_firm.name not in active_rule_names):
            print("✅ PASS: PROJECT rule active, COUNTRY and FIRM filtered out")
        else:
            print("❌ FAIL: Expected only PROJECT active")
            print(f"   Active: {active_rule_names}")

        # Test 3: Enforced rules cannot be overridden
        print("\n--- Test 3: Enforced Rule Violation ---")

        rule_firm.is_enforced = True
        db.commit()

        result = EnhancedRuleEngine.load_and_resolve_rules(db, project.id)
        violations = result["enforcement_violations"]

        if len(violations) > 0:
            print(f"✅ PASS: Detected {len(violations)} enforcement violation(s)")
            for v in violations:
                print(f"   - {v['message']}")
        else:
            print("❌ FAIL: No enforcement violations detected")

        # Cleanup
        print("\n--- Cleanup ---")
        db.delete(rule_project)
        db.delete(rule_country)
        db.delete(rule_firm)
        db.delete(asset)
        db.delete(project)
        db.delete(client)
        db.commit()
        print("✓ Test data cleaned up")

        print("\n=== Test Complete ===\n")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    test_rule_priority()
