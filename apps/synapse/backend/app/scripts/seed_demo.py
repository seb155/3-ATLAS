"""
Enhanced Database Seeding Script
=================================
Seeds complete demo data for SYNAPSE platform:

1. Admin user (admin@aurumax.com / admin123!)
2. Two clients (Goldmine Corp, Sandbox Inc)
3. Two projects (GoldMine Demo + Test Project)
4. 5 baseline rules (FIRM + COUNTRY)
5. 12 sample assets for GoldMine project
6. 2 WBS packages with asset assignments (PKG-IN-001, PKG-EL-001)
7. Version history for assets (HISTORY tab testing)

Run: python -m app.scripts.seed_demo

AI Agents: Use this when database is empty and you need test data.
"""

from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models.auth import Client, Project, User, UserRole
from app.models.models import Asset
from app.models.rules import ActionType, RuleDefinition, RuleSource
from app.models.workflow import AssetVersion, ChangeSource


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

    goldmine = db.query(Client).filter(Client.name == "Goldmine Corp").first()
    if not goldmine:
        goldmine = Client(name="Goldmine Corp", contact_email="engineering@goldmine.com")
        db.add(goldmine)
        db.commit()
        db.refresh(goldmine)
        print("  ✓ Created client: Goldmine Corp")
    else:
        print("  ✓ Client 'Goldmine Corp' already exists")

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

    demo_project = db.query(Project).filter(Project.name == "GoldMine Phase 1 - Crushing").first()
    if not demo_project:
        demo_project = Project(
            name="GoldMine Phase 1 - Crushing",
            client_id=goldmine.id,
            description="Demo project with pre-populated assets and applied rules.",
            status="ACTIVE",
        )
        db.add(demo_project)
        db.commit()
        db.refresh(demo_project)
        print("  ✓ Created project: GoldMine Phase 1 - Crushing")
    else:
        print("  ✓ Project 'GoldMine Phase 1' already exists")

    test_project = db.query(Project).filter(Project.name == "Test Project").first()
    if not test_project:
        test_project = Project(
            name="Test Project",
            client_id=sandbox.id,
            description="Empty project for testing imports.",
            status="ACTIVE",
        )
        db.add(test_project)
        db.commit()
        db.refresh(test_project)
        print("  ✓ Created project: Test Project")
    else:
        print("  ✓ Project 'Test Project' already exists")

    return demo_project, test_project


def seed_baseline_rules(db: Session) -> None:
    """Seed simplified baseline rules"""
    print("\n[4/5] Seeding baseline rules...")

    existing = db.query(RuleDefinition).count()
    if existing >= 5:
        print(f"  ✓ Rules already exist ({existing} rules)")
        return

    rules = [
        # FIRM Rule 1: Pumps require Motors
        {
            "name": "FIRM: Pumps require Motors",
            "description": "Every pump needs a motor to drive it",
            "source": RuleSource.FIRM,
            "discipline": "ELECTRICAL",
            "priority": 10,
            "action_type": ActionType.CREATE_CHILD,
            "condition": {"asset_type": "PUMP"},
            "action": {
                "create_child": {
                    "type": "MOTOR",
                    "naming": "{parent_tag}-M",
                    "relation": "powers",
                    "discipline": "ELECTRICAL",
                    "properties": {"motor_type": "Electric", "enclosure": "TEFC"},
                }
            },
        },
        # FIRM Rule 2: Tanks require Level Transmitters
        {
            "name": "FIRM: Tanks require Level Transmitters",
            "description": "Every tank needs level measurement",
            "source": RuleSource.FIRM,
            "discipline": "AUTOMATION",
            "priority": 10,
            "action_type": ActionType.CREATE_CHILD,
            "condition": {"asset_type": "TANK"},
            "action": {
                "create_child": {
                    "type": "LEVEL_TRANSMITTER",
                    "naming": "{parent_tag}-LT",
                    "relation": "measures",
                    "discipline": "INSTRUMENTATION",
                    "properties": {"measured_variable": "level", "signal_type": "4-20mA"},
                }
            },
        },
        # FIRM Rule 3: Motors require Power Cables
        {
            "name": "FIRM: Motors require Power Cables",
            "description": "Every motor needs a power cable from MCC",
            "source": RuleSource.FIRM,
            "discipline": "ELECTRICAL",
            "priority": 10,
            "action_type": ActionType.CREATE_CABLE,
            "condition": {"asset_type": "MOTOR"},
            "action": {
                "create_cable": {
                    "cable_type": "POWER",
                    "from_type": "MCC",
                    "naming": "{asset_tag}-PWR",
                }
            },
        },
        # COUNTRY Rule: 600V Standard
        {
            "name": "COUNTRY-CA: 600V Motor Standard",
            "description": "Canadian electrical code - 600V for motors",
            "source": RuleSource.COUNTRY,
            "discipline": "ELECTRICAL",
            "priority": 30,
            "action_type": ActionType.SET_PROPERTY,
            "condition": {"asset_type": "MOTOR"},
            "action": {"set_property": {"voltage": "600V", "frequency": "60Hz"}},
        },
        # PROJECT Rule: Custom example
        {
            "name": "PROJECT: Valve Automation",
            "description": "All valves in this project are automated",
            "source": RuleSource.PROJECT,
            "discipline": "AUTOMATION",
            "priority": 50,
            "action_type": ActionType.SET_PROPERTY,
            "condition": {"asset_type": "VALVE"},
            "action": {"set_property": {"actuated": True, "control_type": "pneumatic"}},
        },
    ]

    created = 0
    for rule_data in rules:
        existing_rule = (
            db.query(RuleDefinition).filter(RuleDefinition.name == rule_data["name"]).first()
        )
        if not existing_rule:
            rule = RuleDefinition(**rule_data)
            db.add(rule)
            created += 1

    db.commit()
    print(f"  ✓ Created {created} baseline rules")


def seed_demo_assets(db: Session, project: Project) -> list:
    """Seed demo assets for GoldMine project"""
    print("\n[5/6] Seeding demo assets...")

    existing = db.query(Asset).filter(Asset.project_id == project.id).count()
    if existing >= 10:
        print(f"  ✓ Assets already exist ({existing} assets)")
        # Return all assets for package assignment
        all_assets = db.query(Asset).filter(Asset.project_id == project.id).all()
        return all_assets

    assets = [
        # Process Equipment
        {
            "tag": "310-PP-001",
            "description": "Slurry Feed Pump",
            "type": "PUMP",
            "area": "310",
            "system": "SLURRY",
            "discipline": "MECHANICAL",
            "semantic_type": "EQUIPMENT",
            "properties": {"pump_type": "CENTRIFUGAL", "flow_rate": "100 m3/h", "head": "50m"},
        },
        {
            "tag": "310-TK-001",
            "description": "Holding Tank",
            "type": "TANK",
            "area": "310",
            "system": "SLURRY",
            "discipline": "MECHANICAL",
            "semantic_type": "EQUIPMENT",
            "properties": {"capacity": "50 m3", "material": "Carbon Steel"},
        },
        {
            "tag": "310-AG-001",
            "description": "Mixing Agitator",
            "type": "AGITATOR",
            "area": "310",
            "system": "SLURRY",
            "discipline": "MECHANICAL",
            "semantic_type": "EQUIPMENT",
            "properties": {"power": "15 kW", "speed": "60 RPM"},
        },
        # Electrical Equipment
        {
            "tag": "310-PP-001-M",
            "description": "Slurry Pump Motor",
            "type": "MOTOR",
            "area": "310",
            "system": "SLURRY",
            "discipline": "ELECTRICAL",
            "semantic_type": "EQUIPMENT",
            "properties": {
                "power": "75 HP",
                "voltage": "600V",
                "motor_type": "Electric",
                "enclosure": "TEFC",
            },
        },
        {
            "tag": "310-AG-001-M",
            "description": "Agitator Motor",
            "type": "MOTOR",
            "area": "310",
            "system": "SLURRY",
            "discipline": "ELECTRICAL",
            "semantic_type": "EQUIPMENT",
            "properties": {"power": "20 HP", "voltage": "600V", "motor_type": "Electric"},
        },
        {
            "tag": "310-MCC-01",
            "description": "Motor Control Center",
            "type": "MCC",
            "area": "310",
            "system": "POWER",
            "discipline": "ELECTRICAL",
            "semantic_type": "DISTRIBUTION",
            "properties": {"voltage": "600V", "sections": "6"},
        },
        # Instrumentation
        {
            "tag": "310-TK-001-LT",
            "description": "Tank Level Transmitter",
            "type": "LEVEL_TRANSMITTER",
            "area": "310",
            "system": "SLURRY",
            "discipline": "INSTRUMENTATION",
            "semantic_type": "FIELD_DEVICE",
            "properties": {"range": "0-10m", "signal": "4-20mA", "manufacturer": "Endress+Hauser"},
        },
        {
            "tag": "310-PP-001-PT",
            "description": "Pump Discharge Pressure",
            "type": "PRESSURE_TRANSMITTER",
            "area": "310",
            "system": "SLURRY",
            "discipline": "INSTRUMENTATION",
            "semantic_type": "FIELD_DEVICE",
            "properties": {"range": "0-10 bar", "signal": "4-20mA"},
        },
        # Cables
        {
            "tag": "310-PP-001-PWR",
            "description": "Pump Power Cable",
            "type": "CABLE",
            "area": "310",
            "system": "POWER",
            "discipline": "ELECTRICAL",
            "semantic_type": "CONNECTION",
            "properties": {
                "cable_type": "POWER",
                "from": "310-MCC-01",
                "to": "310-PP-001-M",
                "size": "3C 50mm2",
            },
        },
        {
            "tag": "310-TK-001-SIG",
            "description": "Tank Level Signal Cable",
            "type": "CABLE",
            "area": "310",
            "system": "CONTROL",
            "discipline": "INSTRUMENTATION",
            "semantic_type": "CONNECTION",
            "properties": {
                "cable_type": "INSTRUMENT",
                "from": "310-TK-001-LT",
                "to": "310-PLC-01",
                "pairs": "1",
            },
        },
        # Control System
        {
            "tag": "310-PLC-01",
            "description": "Process PLC",
            "type": "PLC",
            "area": "310",
            "system": "CONTROL",
            "discipline": "AUTOMATION",
            "semantic_type": "CONTROLLER",
            "properties": {"manufacturer": "Rockwell", "series": "ControlLogix", "io_count": "128"},
        },
        # Valves
        {
            "tag": "310-XV-001",
            "description": "Tank Outlet Valve",
            "type": "VALVE",
            "area": "310",
            "system": "SLURRY",
            "discipline": "MECHANICAL",
            "semantic_type": "EQUIPMENT",
            "properties": {"size": "4 inch", "actuated": True, "control_type": "pneumatic"},
        },
    ]

    created = 0
    for asset_data in assets:
        existing_asset = (
            db.query(Asset)
            .filter(Asset.tag == asset_data["tag"], Asset.project_id == project.id)
            .first()
        )

        if not existing_asset:
            asset = Asset(project_id=project.id, **asset_data)
            db.add(asset)
            created += 1

    db.commit()
    print(f"  ✓ Created {created} demo assets")

    # Return all assets for package assignment
    all_assets = db.query(Asset).filter(Asset.project_id == project.id).all()
    return all_assets


def seed_packages(db: Session, project_id: str, assets: list) -> list:
    """Create demo packages and assign assets"""
    from app.models.packages import Package, PackageStatus

    print("\n[6/6] Seeding packages...")

    # Package 1: Instrumentation (IN-P040)
    pkg_inst = db.query(Package).filter(
        Package.name == "PKG-IN-001 - Area 310 Instrumentation",
        Package.project_id == project_id
    ).first()

    if not pkg_inst:
        pkg_inst = Package(
            name="PKG-IN-001 - Area 310 Instrumentation",
            description="Instrumentation package for Process Area 310",
            package_type="IN-P040",
            package_metadata={
                "discipline": "Instrumentation",
                "area": "310",
                "revision": "A",
                "engineer": "J. Smith"
            },
            project_id=project_id,
            status=PackageStatus.OPEN
        )
        db.add(pkg_inst)
        db.commit()
        db.refresh(pkg_inst)
        print(f"  ✓ Created package: {pkg_inst.name}")
    else:
        print(f"  ✓ Package '{pkg_inst.name}' already exists")

    # Package 2: Electrical (CA-P040)
    pkg_elec = db.query(Package).filter(
        Package.name == "PKG-EL-001 - Area 310 Electrical",
        Package.project_id == project_id
    ).first()

    if not pkg_elec:
        pkg_elec = Package(
            name="PKG-EL-001 - Area 310 Electrical",
            description="Electrical power distribution for Area 310",
            package_type="CA-P040",
            package_metadata={
                "discipline": "Electrical",
                "area": "310",
                "revision": "B",
                "engineer": "M. Johnson"
            },
            project_id=project_id,
            status=PackageStatus.OPEN
        )
        db.add(pkg_elec)
        db.commit()
        db.refresh(pkg_elec)
        print(f"  ✓ Created package: {pkg_elec.name}")
    else:
        print(f"  ✓ Package '{pkg_elec.name}' already exists")

    # Assign assets to packages based on type
    # Instrumentation: transmitters, control instruments
    inst_types = ['LEVEL_TRANSMITTER', 'INSTRUMENT', 'CONTROL_SYSTEM']
    inst_assets = [a for a in assets if a.type in inst_types]

    # Electrical: motors, pumps, conveyors, agitators, mills
    elec_types = ['MOTOR', 'PUMP', 'AGITATOR', 'BALL_MILL']
    elec_tags = ['CV-', 'M-', 'P-']  # Conveyors, Motors, Pumps by tag
    elec_assets = [a for a in assets if (a.type in elec_types or any(tag in a.tag.upper() for tag in elec_tags)) and a not in inst_assets]

    assigned_inst = 0
    for asset in inst_assets:
        if not asset.package_id:
            asset.package_id = pkg_inst.id
            assigned_inst += 1

    assigned_elec = 0
    for asset in elec_assets:
        if not asset.package_id:
            asset.package_id = pkg_elec.id
            assigned_elec += 1

    db.commit()

    print(f"  ✓ Assigned {assigned_inst} assets to {pkg_inst.name}")
    print(f"  ✓ Assigned {assigned_elec} assets to {pkg_elec.name}")

    return [pkg_inst, pkg_elec]


def seed_asset_versions(db: Session, assets: list, user: User) -> int:
    """
    Seed version history for demo assets.

    Creates realistic version history showing:
    - Initial creation (IMPORT)
    - Rule-based modifications (RULE)
    - Manual user edits (USER)
    - System updates (SYSTEM)
    """
    print("\n[7/7] Seeding asset version history...")

    # Check if versions already exist
    existing_count = db.query(AssetVersion).count()
    if existing_count > 10:
        print(f"  ✓ Version history already exists ({existing_count} versions)")
        return existing_count

    base_time = datetime.utcnow() - timedelta(days=7)  # Start 7 days ago
    versions_created = 0

    # Version history scenarios for different asset types
    version_scenarios = {
        "PUMP": [
            {
                "version": 1,
                "source": ChangeSource.IMPORT,
                "reason": "Initial import from CSV",
                "days_offset": 0,
                "changes": {"status": "DRAFT", "flow_rate": "80 m3/h"}
            },
            {
                "version": 2,
                "source": ChangeSource.RULE,
                "reason": "Rule 'FIRM: Pumps require Motors' executed",
                "days_offset": 1,
                "changes": {"status": "ACTIVE", "has_motor": True}
            },
            {
                "version": 3,
                "source": ChangeSource.USER,
                "reason": "Manual update: increased flow capacity",
                "days_offset": 3,
                "changes": {"flow_rate": "100 m3/h", "head": "55m"}
            },
        ],
        "MOTOR": [
            {
                "version": 1,
                "source": ChangeSource.RULE,
                "reason": "Created by rule 'FIRM: Pumps require Motors'",
                "days_offset": 1,
                "changes": {"power": "50 HP", "voltage": "480V"}
            },
            {
                "version": 2,
                "source": ChangeSource.RULE,
                "reason": "Rule 'COUNTRY-CA: 600V Motor Standard' applied",
                "days_offset": 2,
                "changes": {"voltage": "600V", "frequency": "60Hz"}
            },
            {
                "version": 3,
                "source": ChangeSource.USER,
                "reason": "Engineering review: upgraded motor size",
                "days_offset": 4,
                "changes": {"power": "75 HP"}
            },
        ],
        "TANK": [
            {
                "version": 1,
                "source": ChangeSource.IMPORT,
                "reason": "Initial import from CSV",
                "days_offset": 0,
                "changes": {"capacity": "40 m3", "material": "Carbon Steel"}
            },
            {
                "version": 2,
                "source": ChangeSource.RULE,
                "reason": "Rule 'FIRM: Tanks require Level Transmitters' executed",
                "days_offset": 1,
                "changes": {"has_level_tx": True}
            },
            {
                "version": 3,
                "source": ChangeSource.USER,
                "reason": "Design change: increased tank capacity",
                "days_offset": 5,
                "changes": {"capacity": "50 m3"}
            },
        ],
        "LEVEL_TRANSMITTER": [
            {
                "version": 1,
                "source": ChangeSource.RULE,
                "reason": "Created by rule 'FIRM: Tanks require Level Transmitters'",
                "days_offset": 1,
                "changes": {"range": "0-8m", "signal": "4-20mA"}
            },
            {
                "version": 2,
                "source": ChangeSource.USER,
                "reason": "Calibration update: adjusted range",
                "days_offset": 4,
                "changes": {"range": "0-10m", "manufacturer": "Endress+Hauser"}
            },
        ],
        "CABLE": [
            {
                "version": 1,
                "source": ChangeSource.RULE,
                "reason": "Created by rule 'FIRM: Motors require Power Cables'",
                "days_offset": 2,
                "changes": {"size": "3C 35mm2", "cable_type": "POWER"}
            },
            {
                "version": 2,
                "source": ChangeSource.USER,
                "reason": "Cable sizing calculation: upgraded size",
                "days_offset": 5,
                "changes": {"size": "3C 50mm2", "length": "45m"}
            },
        ],
        "VALVE": [
            {
                "version": 1,
                "source": ChangeSource.IMPORT,
                "reason": "Initial import from CSV",
                "days_offset": 0,
                "changes": {"size": "4 inch", "actuated": False}
            },
            {
                "version": 2,
                "source": ChangeSource.RULE,
                "reason": "Rule 'PROJECT: Valve Automation' applied",
                "days_offset": 3,
                "changes": {"actuated": True, "control_type": "pneumatic"}
            },
        ],
        "DEFAULT": [
            {
                "version": 1,
                "source": ChangeSource.IMPORT,
                "reason": "Initial import",
                "days_offset": 0,
                "changes": {}
            },
            {
                "version": 2,
                "source": ChangeSource.SYSTEM,
                "reason": "System validation passed",
                "days_offset": 2,
                "changes": {"validated": True}
            },
        ],
    }

    for asset in assets:
        # Get scenario for this asset type, or use default
        scenarios = version_scenarios.get(asset.type, version_scenarios["DEFAULT"])

        for scenario in scenarios:
            # Build snapshot from current asset + scenario changes
            snapshot = {
                "id": asset.id,
                "tag": asset.tag,
                "description": asset.description,
                "type": asset.type,
                "area": asset.area,
                "system": asset.system,
                "discipline": asset.discipline,
                "properties": {**(asset.properties or {}), **scenario["changes"]}
            }

            version = AssetVersion(
                asset_id=asset.id,
                version_number=scenario["version"],
                snapshot=snapshot,
                created_at=base_time + timedelta(days=scenario["days_offset"]),
                created_by=user.id,
                change_reason=scenario["reason"],
                change_source=scenario["source"],
            )
            db.add(version)
            versions_created += 1

    db.commit()
    print(f"  ✓ Created {versions_created} version history entries")
    return versions_created


def main():
    db = SessionLocal()

    try:
        print("=" * 60)
        print("SYNAPSE - Enhanced Database Seeding")
        print("=" * 60)

        user = seed_users(db)
        goldmine, sandbox = seed_clients(db)
        demo_project, test_project = seed_projects(db, goldmine, sandbox)
        seed_baseline_rules(db)
        assets = seed_demo_assets(db, demo_project)
        packages = seed_packages(db, demo_project.id, assets)
        versions_count = seed_asset_versions(db, assets, user)

        print("\n" + "=" * 60)
        print("✓ Seeding complete!")
        print("=" * 60)
        print("\n📊 Summary:")
        print("  - Users: 1")
        print("  - Clients: 2")
        print("  - Projects: 2")
        print(f"  - Rules: {db.query(RuleDefinition).count()}")
        print(f"  - Assets: {db.query(Asset).count()}")
        print(f"  - Packages: {len(packages)}")
        print(f"  - Asset Versions: {versions_count}")
        print("\n🚀 Access the app: http://localhost:4000")
        print("   Login: admin@aurumax.com / admin123!")
        print("\n💡 Test HISTORY tab: Select asset → HISTORY tab")

    except Exception as e:
        print(f"\n❌ Error during seeding: {e}")
        import traceback

        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
