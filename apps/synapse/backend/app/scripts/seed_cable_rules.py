from app.core.database import SessionLocal
from app.models.rules import RuleActionType, RuleDefinition, RuleSource


def seed_cable_rules():
    db = SessionLocal()
    try:
        print("Seeding Cable Rules...")

        # 1. FIRM: Power Cable for Motors
        # Creates a power cable for every motor
        rule_motor_pwr = RuleDefinition(
            name="FIRM: Create Power Cable for Motors",
            description="Automatically generate power cables for all motors",
            source=RuleSource.FIRM,
            priority=10,
            discipline="ELECTRICAL",
            category="CABLE_GENERATION",
            action_type=RuleActionType.CREATE_CABLE,
            is_active=True,
            is_enforced=True,
            condition={"asset_type": "MOTOR"},
            action={
                "create_cable": {
                    "cable_tag": "{tag}-PWR",
                    "cable_type": "POWER",
                    "sizing_method": "Auto",
                    "voltage": "600V",
                    "length_meters": 75.0,  # Default length
                    "insulation": "RW90 XLPE 600V",
                    "voltage_drop_limit": 3.0,
                }
            },
        )

        # 2. FIRM: Signal Cable for Instruments
        # Creates a signal cable for every instrument
        rule_instr_sig = RuleDefinition(
            name="FIRM: Create Signal Cable for Instruments",
            description="Automatically generate signal cables for all instruments",
            source=RuleSource.FIRM,
            priority=10,
            discipline="AUTOMATION",
            category="CABLE_GENERATION",
            action_type=RuleActionType.CREATE_CABLE,
            is_active=True,
            is_enforced=True,
            condition={"asset_type": "INSTRUMENT"},
            action={
                "create_cable": {
                    "cable_tag": "{tag}-SIG",
                    "cable_type": "SIGNAL",
                    "sizing_method": "Manual",  # No auto-sizing for signal yet
                    "voltage": "24VDC",
                    "length_meters": 100.0,
                    "insulation": "PVC/PVC 300V",
                    "properties": {"conductor_size": "16 AWG", "construction": "1 Pair Shielded"},
                }
            },
        )

        # Upsert rules
        for rule in [rule_motor_pwr, rule_instr_sig]:
            existing = db.query(RuleDefinition).filter(RuleDefinition.name == rule.name).first()
            if existing:
                print(f"Updating rule: {rule.name}")
                existing.action = rule.action
                existing.condition = rule.condition
                existing.action_type = rule.action_type
            else:
                print(f"Creating rule: {rule.name}")
                db.add(rule)

        db.commit()
        print("Cable rules seeded successfully.")

    except Exception as e:
        print(f"Error seeding cable rules: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_cable_rules()
