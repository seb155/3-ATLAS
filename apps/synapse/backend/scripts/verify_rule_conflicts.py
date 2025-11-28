import os
import sys

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.core.database import SessionLocal
from app.models.auth import Client, Project
from app.models.models import Asset
from app.models.rules import RuleActionType, RuleDefinition, RuleSource
from app.services.enhanced_rule_engine import EnhancedRuleEngine


def verify_conflicts():
    db = SessionLocal()
    try:
        print("1. Setting up test data...")
        import uuid
        unique_suffix = str(uuid.uuid4())[:8]

        # Create a test client with unique name
        client = Client(name=f"Test Client {unique_suffix}", contact_email="test@example.com")
        db.add(client)
        db.commit()

        # Create a test project with country
        project = Project(
            name=f"Conflict Test {unique_suffix}",
            description="Testing Rule Priorities",
            client_id=client.id
        )
        # Add country attribute for COUNTRY rule filtering
        project.country = "CA"  # Canada
        db.add(project)
        db.commit()

        # Create a test asset
        asset = Asset(
            tag="P-101",
            type="PUMP",
            project_id=project.id,
            properties={"type": "centrifugal"}
        )
        db.add(asset)
        db.commit()

        print(f"Created Project: {project.name} (ID: {project.id})")
        print(f"Created Asset: {asset.tag} (ID: {asset.id})")

        # Create conflicting rules
        # Rule 1: FIRM (Priority 10) - Sets voltage to 480V
        rule_firm = RuleDefinition(
            name="FIRM: Default Voltage",
            description="Firm standard",
            source=RuleSource.FIRM,
            priority=10,
            discipline="ELECTRICAL",
            condition={"type": "PUMP"},
            action_type=RuleActionType.SET_PROPERTY,
            action={"set_property": {"voltage": "480V"}},
            is_active=True
        )
        db.add(rule_firm)

        # Rule 2: COUNTRY (Priority 30) - Sets voltage to 600V
        rule_country = RuleDefinition(
            name="COUNTRY-CA: Standard Voltage",
            description="Canadian standard",
            source=RuleSource.COUNTRY,
            source_id="CA",
            priority=30,
            discipline="ELECTRICAL",
            condition={"type": "PUMP"},
            action_type=RuleActionType.SET_PROPERTY,
            action={"set_property": {"voltage": "600V"}},
            is_active=True
        )
        db.add(rule_country)

        db.commit()
        print("Created conflicting rules (FIRM vs COUNTRY)")

        # Test 1: Basic Priority (COUNTRY should win)
        print("\n2. Testing Basic Priority (COUNTRY > FIRM)...")
        resolution = EnhancedRuleEngine.load_and_resolve_rules(db, project.id)
        active_rules = resolution["rules"]
        violations = resolution["enforcement_violations"]

        print(f"Active Rules: {len(active_rules)}")
        print(f"Violations: {len(violations)}")

        winner = next((r for r in active_rules if r.id == rule_country.id), None)
        loser = next((r for r in active_rules if r.id == rule_firm.id), None)

        if winner and not loser:
            print("✅ SUCCESS: COUNTRY rule is active, FIRM rule is filtered out.")
        else:
            print("❌ FAILURE: Priority resolution failed.")
            print(f"Country Active: {winner is not None}")
            print(f"Firm Active: {loser is not None}")

        # Test 2: Explicit Override
        print("\n3. Testing Explicit Override...")
        # Rule 3: PROJECT (Priority 50) - Sets voltage to 4160V, overrides COUNTRY
        rule_project = RuleDefinition(
            name="PROJECT: High Voltage Pump",
            description="Project specific",
            source=RuleSource.PROJECT,
            source_id=project.id,  # Use actual project ID
            priority=50,
            discipline="ELECTRICAL",
            condition={"type": "PUMP"},
            action_type=RuleActionType.SET_PROPERTY,
            action={"set_property": {"voltage": "4160V"}},
            is_active=True,
            overrides_rule_id=rule_country.id
        )
        db.add(rule_project)
        db.commit()

        resolution = EnhancedRuleEngine.load_and_resolve_rules(db, project.id)
        active_rules = resolution["rules"]

        winner = next((r for r in active_rules if r.id == rule_project.id), None)
        loser_country = next((r for r in active_rules if r.id == rule_country.id), None)

        if winner and not loser_country:
            print("✅ SUCCESS: PROJECT rule overrides COUNTRY rule.")
        else:
            print("❌ FAILURE: Override logic failed.")

        # Test 3: Enforcement Violation
        print("\n4. Testing Enforcement Violation...")
        # Make FIRM rule enforced
        rule_firm.is_enforced = True
        db.commit()

        resolution = EnhancedRuleEngine.load_and_resolve_rules(db, project.id)
        violations = resolution["enforcement_violations"]

        # PROJECT rule (50) tries to override FIRM (10), but FIRM is enforced.
        # Wait, the logic in detect_rule_conflicts says:
        # "conflict_status = 'enforced_violation' if loser.is_enforced else 'valid_override'"
        # Here PROJECT (50) is winner, FIRM (10) is loser.
        # If FIRM is enforced, it should be a violation.

        violation = next((v for v in violations if v["overridden_rule"]["id"] == rule_firm.id), None)

        if violation:
            print("✅ SUCCESS: Detected enforcement violation for FIRM rule.")
            print(f"Violation: {violation['message']}")
        else:
            print("❌ FAILURE: Failed to detect enforcement violation.")

        # Cleanup
        print("\n5. Cleaning up...")
        db.delete(rule_project)
        db.delete(rule_country)
        db.delete(rule_firm)
        db.delete(asset)
        db.delete(project)
        db.delete(client)
        db.commit()
        print("Cleanup complete.")

    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    verify_conflicts()
