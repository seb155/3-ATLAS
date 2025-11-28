"""
SYNAPSE - Complete Database Seeding Script
==========================================
Seeds the database with:
1. Admin user
2. Two clients (Goldmine Corp, Sandbox Inc)
3. Two projects:
   - GoldMine Demo: Pre-populated with assets, rules applied
   - Sandbox Project: Empty, for testing imports
4. Baseline rules (FIRM + COUNTRY)
5. Sample assets for demo project

Run: python -m app.scripts.seed_all
"""

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models.auth import Client, Project, User, UserRole
from app.models.models import Asset
from app.models.rules import RuleActionType, RuleDefinition, RuleSource


def seed_users(db: Session) -> User:
    """Create admin user"""
    print("\n[1/5] Seeding users...")

    user = db.query(User).filter(User.email == "admin@aurumax.com").first()
    if not user:
        user = User(
            email="admin@aurumax.com",
            hashed_password=get_password_hash("admin123!"),
            full_name="Admin User",
            role=UserRole.ADMIN,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print("  ✓ Created admin user: admin@aurumax.com / admin123!")
    else:
        print("  ✓ Admin user already exists")

    return user


def seed_clients(db: Session) -> tuple:
    """Create demo clients"""
    print("\n[2/5] Seeding clients...")

    # Client 1: Goldmine Corp (for demo)
    goldmine = db.query(Client).filter(Client.name == "Goldmine Corp").first()
    if not goldmine:
        goldmine = Client(name="Goldmine Corp", contact_email="engineering@goldmine.com")
        db.add(goldmine)
        db.commit()
        db.refresh(goldmine)
        print("  ✓ Created client: Goldmine Corp")
    else:
        print("  ✓ Client 'Goldmine Corp' already exists")

    # Client 2: Sandbox Inc (for testing)
    sandbox = db.query(Client).filter(Client.name == "Sandbox Inc").first()
    if not sandbox:
        sandbox = Client(name="Sandbox Inc", contact_email="dev@sandbox.com")
        db.add(sandbox)
        db.commit()
        db.refresh(sandbox)
        print("  ✓ Created client: Sandbox Inc")
    else:
        print("  ✓ Client 'Sandbox Inc' already exists")

    return goldmine, sandbox


def seed_projects(db: Session, goldmine: Client, sandbox: Client) -> tuple:
    """Create demo projects"""
    print("\n[3/5] Seeding projects...")

    # Project 1: GoldMine Demo (pre-populated)
    demo_project = db.query(Project).filter(Project.name == "GoldMine Phase 1 - Crushing").first()
    if not demo_project:
        demo_project = Project(
            name="GoldMine Phase 1 - Crushing",
            client_id=goldmine.id,
            description=(
                "Demo project with pre-populated assets and applied rules. "
                "Use this to explore SYNAPSE features."
            ),
            status="ACTIVE",
        )
        db.add(demo_project)
        db.commit()
        db.refresh(demo_project)
        print("  ✓ Created project: GoldMine Phase 1 - Crushing")
    else:
        print("  ✓ Project 'GoldMine Phase 1' already exists")

    # Project 2: Sandbox Project (empty for testing)
    sandbox_project = db.query(Project).filter(Project.name == "Test Import Project").first()
    if not sandbox_project:
        sandbox_project = Project(
            name="Test Import Project",
            client_id=sandbox.id,
            description=(
                "Empty project for testing P&ID imports and rule execution. Start fresh here!"
            ),
            status="ACTIVE",
        )
        db.add(sandbox_project)
        db.commit()
        db.refresh(sandbox_project)
        print("  ✓ Created project: Test Import Project (empty)")
    else:
        print("  ✓ Project 'Test Import Project' already exists")

    return demo_project, sandbox_project


def seed_baseline_rules(db: Session) -> None:
    """Seed baseline FIRM and COUNTRY rules"""
    print("\n[4/5] Seeding baseline rules...")

    # Check if rules already exist
    existing = db.query(RuleDefinition).filter(RuleDefinition.source == RuleSource.FIRM).count()
    if existing >= 10:
        print(f"  ✓ Baseline rules already exist ({existing} FIRM rules)")
        return

    rules = [
        # FIRM Rules (Priority 10) - Company defaults
        {
            "name": "FIRM: Pumps require Motors",
            "description": "Every pump needs a motor to drive it",
            "source": RuleSource.FIRM,
            "discipline": "ELECTRICAL",
            "priority": 10,
            "condition": {"asset_type": "PUMP"},
            "action_type": RuleActionType.CREATE_CHILD,
            "action": {
                "create_child": {
                    "type": "MOTOR",
                    "naming": "{parent_tag}-M",
                    "relation": "powers",
                    "properties": {"driven_equipment": "{parent_tag}"},
                }
            },
        },
        {
            "name": "FIRM: Tanks require Level Transmitters",
            "description": "Every tank needs level measurement",
            "source": RuleSource.FIRM,
            "discipline": "INSTRUMENTATION",
            "priority": 10,
            "condition": {"asset_type": "TANK"},
            "action_type": RuleActionType.CREATE_CHILD,
            "action": {
                "create_child": {
                    "type": "LEVEL_TRANSMITTER",
                    "naming": "{parent_tag}-LT",
                    "relation": "measures",
                    "properties": {"measured_variable": "level"},
                }
            },
        },
        {
            "name": "FIRM: Agitators require Motors",
            "description": "Every agitator needs a motor",
            "source": RuleSource.FIRM,
            "discipline": "ELECTRICAL",
            "priority": 10,
            "condition": {"asset_type": "AGITATOR"},
            "action_type": RuleActionType.CREATE_CHILD,
            "action": {
                "create_child": {
                    "type": "MOTOR",
                    "naming": "{parent_tag}-M",
                    "relation": "powers",
                    "properties": {"driven_equipment": "{parent_tag}"},
                }
            },
        },
        {
            "name": "FIRM: Ball Mills require Motors",
            "description": "Ball mills need large drive motors",
            "source": RuleSource.FIRM,
            "discipline": "ELECTRICAL",
            "priority": 10,
            "condition": {"asset_type": "BALL_MILL"},
            "action_type": RuleActionType.CREATE_CHILD,
            "action": {
                "create_child": {
                    "type": "MOTOR",
                    "naming": "{parent_tag}-M",
                    "relation": "powers",
                    "properties": {"driven_equipment": "{parent_tag}", "hp_min": 500},
                }
            },
        },
        {
            "name": "FIRM: Conveyors require Motors",
            "description": "Conveyors need drive motors",
            "source": RuleSource.FIRM,
            "discipline": "ELECTRICAL",
            "priority": 10,
            "condition": {"asset_type": "CONVEYOR"},
            "action_type": RuleActionType.CREATE_CHILD,
            "action": {
                "create_child": {
                    "type": "MOTOR",
                    "naming": "{parent_tag}-M",
                    "relation": "powers",
                    "properties": {"driven_equipment": "{parent_tag}"},
                }
            },
        },
        {
            "name": "FIRM: Motors require Power Cables",
            "description": "Every motor needs a power cable from MCC",
            "source": RuleSource.FIRM,
            "discipline": "ELECTRICAL",
            "priority": 10,
            "condition": {"asset_type": "MOTOR"},
            "action_type": RuleActionType.CREATE_CABLE,
            "action": {
                "create_cable": {
                    "type": "POWER",
                    "naming": "{asset_tag}-PWR",
                    "from": "{nearest_mcc}",
                    "to": "{asset_tag}",
                }
            },
        },
        {
            "name": "FIRM: Transmitters require Signal Cables",
            "description": "4-20mA signal cables to marshalling",
            "source": RuleSource.FIRM,
            "discipline": "INSTRUMENTATION",
            "priority": 10,
            "condition": {
                "asset_type": {
                    "$in": ["LEVEL_TRANSMITTER", "FLOW_TRANSMITTER", "PRESSURE_TRANSMITTER"]
                }
            },
            "action_type": RuleActionType.CREATE_CABLE,
            "action": {
                "create_cable": {
                    "type": "INSTRUMENT",
                    "naming": "{asset_tag}-SIG",
                    "from": "{asset_tag}",
                    "to": "{nearest_marshalling}",
                }
            },
        },
        {
            "name": "FIRM: VFDs require Control Cables",
            "description": "VFDs need control cables to PLC",
            "source": RuleSource.FIRM,
            "discipline": "AUTOMATION",
            "priority": 10,
            "condition": {"asset_type": "VFD"},
            "action_type": RuleActionType.CREATE_CABLE,
            "action": {
                "create_cable": {
                    "type": "CONTROL",
                    "naming": "{asset_tag}-CTL",
                    "from": "{asset_tag}",
                    "to": "{nearest_plc}",
                }
            },
        },
        {
            "name": "FIRM: Default IO Allocation",
            "description": "Allocate IO for all field devices",
            "source": RuleSource.FIRM,
            "discipline": "AUTOMATION",
            "priority": 10,
            "condition": {"semantic_type": "FIELD_DEVICE"},
            "action_type": RuleActionType.ALLOCATE_IO,
            "action": {"allocate_io": {"io_type": "auto", "plc": "{nearest_plc}"}},
        },
        # COUNTRY Rules (Priority 30) - Regional standards
        {
            "name": "COUNTRY-CA: 600V Motor Standard",
            "description": "Canadian electrical code - 600V for motors",
            "source": RuleSource.COUNTRY,
            "discipline": "ELECTRICAL",
            "priority": 30,
            "condition": {"asset_type": "MOTOR"},
            "action_type": RuleActionType.SET_PROPERTY,
            "action": {"set_property": {"property": "voltage_rating", "value": "600V"}},
        },
        {
            "name": "COUNTRY-CA: CEC Cable Sizing",
            "description": "Use Canadian Electrical Code for cable sizing",
            "source": RuleSource.COUNTRY,
            "discipline": "ELECTRICAL",
            "priority": 30,
            "condition": {"asset_type": "CABLE"},
            "action_type": RuleActionType.SET_PROPERTY,
            "action": {"set_property": {"property": "sizing_standard", "value": "CEC-2021"}},
        },
        {
            "name": "COUNTRY-US: 480V Motor Standard",
            "description": "US electrical code - 480V for motors",
            "source": RuleSource.COUNTRY,
            "discipline": "ELECTRICAL",
            "priority": 30,
            "condition": {"asset_type": "MOTOR"},
            "action_type": RuleActionType.SET_PROPERTY,
            "action": {"set_property": {"property": "voltage_rating", "value": "480V"}},
        },
        {
            "name": "COUNTRY-US: NEC Cable Sizing",
            "description": "Use National Electrical Code for cable sizing",
            "source": RuleSource.COUNTRY,
            "discipline": "ELECTRICAL",
            "priority": 30,
            "condition": {"asset_type": "CABLE"},
            "action_type": RuleActionType.SET_PROPERTY,
            "action": {"set_property": {"property": "sizing_standard", "value": "NEC-2023"}},
        },
    ]

    created = 0
    for rule_data in rules:
        existing = db.query(RuleDefinition).filter(RuleDefinition.name == rule_data["name"]).first()
        if not existing:
            rule = RuleDefinition(**rule_data)
            db.add(rule)
            created += 1

    db.commit()
    print(f"  ✓ Created {created} baseline rules ({len(rules) - created} already existed)")


def seed_demo_assets(db: Session, project: Project) -> None:
    """Seed demo assets for GoldMine project"""
    print("\n[5/5] Seeding demo assets...")

    # Check if assets already exist
    existing = db.query(Asset).filter(Asset.project_id == project.id).count()
    if existing >= 10:
        print(f"  ✓ Demo assets already exist ({existing} assets)")
        return

    assets_data = [
        # Pumps
        {
            "tag": "100-PP-001",
            "type": "PUMP",
            "description": "Primary Slurry Pump",
            "area": "100",
            "system": "CRUSHING",
        },
        {
            "tag": "100-PP-002",
            "type": "PUMP",
            "description": "Secondary Slurry Pump",
            "area": "100",
            "system": "CRUSHING",
        },
        {
            "tag": "100-PP-003",
            "type": "PUMP",
            "description": "Water Pump",
            "area": "100",
            "system": "UTILITIES",
        },
        {
            "tag": "200-PP-001",
            "type": "PUMP",
            "description": "Mill Feed Pump",
            "area": "200",
            "system": "GRINDING",
        },
        {
            "tag": "200-PP-002",
            "type": "PUMP",
            "description": "Cyclone Feed Pump",
            "area": "200",
            "system": "GRINDING",
        },
        # Tanks
        {
            "tag": "100-TK-001",
            "type": "TANK",
            "description": "Surge Tank",
            "area": "100",
            "system": "CRUSHING",
        },
        {
            "tag": "200-TK-001",
            "type": "TANK",
            "description": "Mill Sump",
            "area": "200",
            "system": "GRINDING",
        },
        {
            "tag": "200-TK-002",
            "type": "TANK",
            "description": "Process Water Tank",
            "area": "200",
            "system": "UTILITIES",
        },
        # Conveyors
        {
            "tag": "100-CV-001",
            "type": "CONVEYOR",
            "description": "Primary Conveyor",
            "area": "100",
            "system": "CRUSHING",
        },
        {
            "tag": "100-CV-002",
            "type": "CONVEYOR",
            "description": "Secondary Conveyor",
            "area": "100",
            "system": "CRUSHING",
        },
        # Ball Mill
        {
            "tag": "200-ML-001",
            "type": "BALL_MILL",
            "description": "Primary Ball Mill",
            "area": "200",
            "system": "GRINDING",
        },
        # Agitators
        {
            "tag": "200-AG-001",
            "type": "AGITATOR",
            "description": "Tank Agitator",
            "area": "200",
            "system": "GRINDING",
        },
    ]

    created = 0
    for asset_data in assets_data:
        existing = (
            db.query(Asset)
            .filter(Asset.project_id == project.id, Asset.tag == asset_data["tag"])
            .first()
        )

        if not existing:
            asset = Asset(
                project_id=project.id,
                tag=asset_data["tag"],
                type=asset_data["type"],
                description=asset_data["description"],
                area=asset_data["area"],
                system=asset_data["system"],
                data_status="FRESH_IMPORT",
            )
            db.add(asset)
            created += 1

    db.commit()
    print(f"  ✓ Created {created} demo assets ({len(assets_data) - created} already existed)")


def main():
    """Main seeding function"""
    print("=" * 60)
    print("SYNAPSE - Database Seeding")
    print("=" * 60)

    db = SessionLocal()

    try:
        # Seed in order
        seed_users(db)
        goldmine, sandbox = seed_clients(db)
        demo_project, sandbox_project = seed_projects(db, goldmine, sandbox)
        seed_baseline_rules(db)
        seed_demo_assets(db, demo_project)

        print("\n" + "=" * 60)
        print("✓ Seeding complete!")
        print("=" * 60)
        print(
            f"""
Summary:
  - Admin user: admin@aurumax.com / admin123!
  - Clients: Goldmine Corp, Sandbox Inc
  - Projects:
    1. GoldMine Phase 1 - Crushing (with {
        db.query(Asset).filter(Asset.project_id == demo_project.id).count()
    } assets)
    2. Test Import Project (empty, for testing)
  - Baseline rules: {db.query(RuleDefinition).count()} total
        """
        )

    except Exception as e:
        print(f"\n❌ Error during seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
