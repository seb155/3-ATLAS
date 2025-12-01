"""
Test ValidationService

Verifies that validation rules work correctly.
"""
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.core.database import SessionLocal
from app.models.auth import Client, Project
from app.models.models import Asset
from app.models.rules import RuleActionType, RuleDefinition, RuleSource
from app.services.validation_service import ValidationService, ValidationStatus


def test_validation_service():
    db = SessionLocal()
    try:
        print("\n=== ValidationService Test ===\n")

        # Setup: Create client and project
        client = Client(name="TEST Validation Client", contact_email="test@example.com")
        db.add(client)
        db.flush()

        project = Project(
            name="TEST Validation Project", description="Testing validation", client_id=client.id
        )
        db.add(project)
        db.flush()

        # Create test pump with low efficiency
        pump = Asset(
            tag="TEST-P-001",
            type="PUMP",
            project_id=project.id,
            properties={
                "efficiency": "75",  # Below minimum
                "pump_type": "centrifugal",
            },
        )
        db.add(pump)
        db.commit()

        print(f"Created test project: {project.id}")
        print(f"Created test pump: {pump.tag} (efficiency: 75%)")

        # Test 1: property_in_range validation
        print("\n--- Test 1: Property In Range Validation ---")

        rule_efficiency = RuleDefinition(
            name="TEST: Pump Efficiency Check",
            source=RuleSource.FIRM,
            priority=10,
            condition={"type": "PUMP"},
            action_type=RuleActionType.VALIDATE,
            action={
                "validate": {
                    "assertion": "property_in_range",
                    "property": "efficiency",
                    "min": 80,
                    "max": 95,
                }
            },
            is_active=True,
        )

        db.add(rule_efficiency)
        db.commit()

        # Validate asset
        results = ValidationService.validate_asset(db, pump.id, project.id)

        if results:
            result = results[0]
            print(f"Status: {result.status.value}")
            print(f"Message: {result.message}")

            if result.status == ValidationStatus.WARNING and "75" in result.message:
                print("✅ PASS: Correctly detected low efficiency")
            else:
                print("❌ FAIL: Expected WARNING with 75% in message")
        else:
            print("❌ FAIL: No validation results returned")

        # Test 2: property_equals validation
        print("\n--- Test 2: Property Equals Validation ---")

        rule_type = RuleDefinition(
            name="TEST: Pump Type Check",
            source=RuleSource.FIRM,
            priority=10,
            condition={"type": "PUMP"},
            action_type=RuleActionType.VALIDATE,
            action={
                "validate": {
                    "assertion": "property_equals",
                    "property": "pump_type",
                    "value": "centrifugal",
                }
            },
            is_active=True,
        )

        db.add(rule_type)
        db.commit()

        results = ValidationService.validate_asset(db, pump.id, project.id)

        pass_count = sum(1 for r in results if r.status == ValidationStatus.PASS)
        warning_count = sum(1 for r in results if r.status == ValidationStatus.WARNING)

        print(f"Total validations: {len(results)}")
        print(f"Pass: {pass_count}, Warning: {warning_count}")

        if pass_count >= 1 and warning_count >= 1:
            print("✅ PASS: property_equals validation working")
        else:
            print("❌ FAIL: Expected at least 1 PASS and 1 WARNING")

        # Test 3: Project-wide validation
        print("\n--- Test 3: Project-Wide Validation ---")

        # Create another pump
        pump2 = Asset(
            tag="TEST-P-002",
            type="PUMP",
            project_id=project.id,
            properties={
                "efficiency": "92",  # Good
                "pump_type": "centrifugal",
            },
        )
        db.add(pump2)
        db.commit()

        results = ValidationService.validate_project(db, project.id)
        summary = ValidationService.get_validation_summary(results)

        print(f"Assets validated: {summary['assets_validated']}")
        print(f"Total validations: {summary['total']}")
        print(f"Pass: {summary['pass']}, Warning: {summary['warning']}, Error: {summary['error']}")

        if summary["assets_validated"] == 2:
            print("✅ PASS: Project-wide validation working")
        else:
            print("❌ FAIL: Expected 2 assets validated")

        # Cleanup
        print("\n--- Cleanup ---")
        db.delete(rule_type)
        db.delete(rule_efficiency)
        db.delete(pump2)
        db.delete(pump)
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
    test_validation_service()
