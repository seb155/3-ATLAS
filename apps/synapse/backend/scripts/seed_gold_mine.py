import logging
import os
import sys

# Add the parent directory to sys.path to allow imports from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models.auth import Client, Project, User, UserRole
from app.models.models import Asset, AssetType, IOType, LBSNode, LocationType

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def seed_data():
    db = SessionLocal()
    try:
        logger.info("Starting Gold Mine data seeding...")

        # 1. Create Client
        client = db.query(Client).filter(Client.name == "Gold Mine Corp").first()
        if not client:
            client = Client(name="Gold Mine Corp", contact_email="contact@goldmine.com")
            db.add(client)
            db.commit()
            db.refresh(client)
            logger.info(f"Created Client: {client.name}")
        else:
            logger.info(f"Client {client.name} already exists")

        # 2. Create Project
        project = db.query(Project).filter(Project.name == "Gold Mine Expansion").first()
        if not project:
            project = Project(
                name="Gold Mine Expansion",
                client_id=client.id,
                description="Expansion of the crushing plant and conveyor systems.",
                status="ACTIVE",
            )
            db.add(project)
            db.commit()
            db.refresh(project)
            logger.info(f"Created Project: {project.name}")
        else:
            logger.info(f"Project {project.name} already exists")

        # 3. Create User
        user_email = "goldmine_admin@example.com"
        user = db.query(User).filter(User.email == user_email).first()
        if not user:
            user = User(
                email=user_email,
                hashed_password=get_password_hash("secret"),
                full_name="Gold Mine Admin",
                role=UserRole.CLIENT,
                is_active=True,
            )
            db.add(user)
            db.commit()
            logger.info(f"Created User: {user.email}")
        else:
            logger.info(f"User {user.email} already exists")

        # 4. Create Locations (LBS)
        # Site
        site = LBSNode(name="Gold Mine Site", type=LocationType.SITE, project_id=project.id)
        db.add(site)
        db.commit()
        db.refresh(site)

        # Area
        area = LBSNode(
            name="Crushing Plant", type=LocationType.AREA, project_id=project.id, parent_id=site.id
        )
        db.add(area)
        db.commit()
        db.refresh(area)

        # Room
        mcc_room = LBSNode(
            name="MCC Room 1", type=LocationType.ROOM, project_id=project.id, parent_id=area.id
        )
        db.add(mcc_room)
        db.commit()
        db.refresh(mcc_room)

        # Cabinets
        plc_cabinet = LBSNode(
            name="PLC-01",
            type=LocationType.CABINET,
            project_id=project.id,
            parent_id=mcc_room.id,
            ip_rating="IP54",
        )
        rio_cabinet = LBSNode(
            name="RIO-01",
            type=LocationType.CABINET,
            project_id=project.id,
            parent_id=area.id,
            ip_rating="IP65",
        )  # RIO might be in the field
        db.add_all([plc_cabinet, rio_cabinet])
        db.commit()
        db.refresh(plc_cabinet)
        db.refresh(rio_cabinet)

        logger.info("Created Locations hierarchy")

        # 5. Create Assets
        assets = []

        # PLC
        plc = Asset(
            tag="PLC-01-CPU",
            description="PlantPAx Process Controller",
            type=AssetType.CONTROL_SYSTEM,
            project_id=project.id,
            area="310",
            system="Control",
            io_type=IOType.ETHERNET_IP,
            manufacturer_part_id="1756-L83E",
            location_id=plc_cabinet.id,
            purchasing={"status": "Ordered", "poNumber": "PO-998877"},
        )
        assets.append(plc)

        # IO Modules (in PLC Cabinet)
        io_modules = [
            ("DI-01", "1756-IB16", IOType.DI),
            ("DO-01", "1756-OB16", IOType.DO),
            ("AI-01", "1756-IF8", IOType.AI),
            ("AO-01", "1756-OF8", IOType.AO),
        ]

        for tag_suffix, part, io_type in io_modules:
            assets.append(
                Asset(
                    tag=f"PLC-01-{tag_suffix}",
                    description=f"IO Module {io_type}",
                    type=AssetType.CONTROL_SYSTEM,
                    project_id=project.id,
                    area="310",
                    system="Control",
                    io_type=io_type,
                    manufacturer_part_id=part,
                    location_id=plc_cabinet.id,
                )
            )

        # Instruments (Field)
        # Flow
        fit_101 = Asset(
            tag="310-FIT-101",
            description="Crusher Feed Flow",
            type=AssetType.INSTRUMENT,
            project_id=project.id,
            area="310",
            system="Crushing",
            io_type=IOType.ETHERNET_IP,
            manufacturer_part_id="Promass 83F",
            process={"fluid": "Slurry", "minRange": 0, "maxRange": 500, "units": "t/h"},
            location_id=area.id,  # Physically in the area
        )
        assets.append(fit_101)

        # Level
        lit_102 = Asset(
            tag="310-LIT-102",
            description="Crusher Hopper Level",
            type=AssetType.INSTRUMENT,
            project_id=project.id,
            area="310",
            system="Crushing",
            io_type=IOType.AI,  # 4-20mA
            manufacturer_part_id="Levelflex FMP51",
            process={"minRange": 0, "maxRange": 100, "units": "%"},
            location_id=area.id,
        )
        assets.append(lit_102)

        # Pressure
        pit_103 = Asset(
            tag="310-PIT-103",
            description="Hydraulic Pressure",
            type=AssetType.INSTRUMENT,
            project_id=project.id,
            area="310",
            system="Crushing",
            io_type=IOType.AI,
            manufacturer_part_id="Cerabar M PMC51",
            process={"minRange": 0, "maxRange": 250, "units": "bar"},
            location_id=area.id,
        )
        assets.append(pit_103)

        # Motors
        # Crusher Motor
        m_101 = Asset(
            tag="310-M-101",
            description="Primary Crusher Motor",
            type=AssetType.MOTOR,
            project_id=project.id,
            area="310",
            system="Crushing",
            io_type=IOType.ETHERNET_IP,  # E300
            manufacturer_part_id="E300 Overload",
            electrical={"voltage": "4160V", "powerKW": 150, "loadType": "Constant"},
            location_id=area.id,
        )
        assets.append(m_101)

        # Conveyor Motor
        m_102 = Asset(
            tag="310-M-102",
            description="Discharge Conveyor Motor",
            type=AssetType.MOTOR,
            project_id=project.id,
            area="310",
            system="Conveying",
            io_type=IOType.ETHERNET_IP,  # VFD
            manufacturer_part_id="PowerFlex 755",
            electrical={"voltage": "600V", "powerKW": 75, "loadType": "Variable"},
            location_id=area.id,
        )
        assets.append(m_102)

        # --- NEW AREAS & ASSETS ---

        # 320 - Grinding
        grinding_area = LBSNode(
            name="Grinding Plant", type=LocationType.AREA, project_id=project.id, parent_id=site.id
        )
        db.add(grinding_area)
        db.commit()
        db.refresh(grinding_area)

        # Ball Mill Motor
        m_201 = Asset(
            tag="320-M-201",
            description="Ball Mill Main Motor",
            type=AssetType.MOTOR,
            project_id=project.id,
            area="320",
            system="Grinding",
            io_type=IOType.ETHERNET_IP,
            manufacturer_part_id="Siemens HV Motor",
            electrical={"voltage": "4160V", "powerKW": 2500, "loadType": "Constant"},
            purchasing={"workPackageId": "PKG-MECH-02", "status": "Ordered"},
            location_id=grinding_area.id,
        )
        assets.append(m_201)

        # 330 - Leaching (CIL)
        leaching_area = LBSNode(
            name="CIL Leaching", type=LocationType.AREA, project_id=project.id, parent_id=site.id
        )
        db.add(leaching_area)
        db.commit()
        db.refresh(leaching_area)

        # Leach Tank Agitator
        for i in range(1, 7):
            assets.append(
                Asset(
                    tag=f"330-AG-{300+i}",
                    description=f"Leach Tank {i} Agitator",
                    type=AssetType.MOTOR,
                    project_id=project.id,
                    area="330",
                    system="Leaching",
                    io_type=IOType.ETHERNET_IP,
                    manufacturer_part_id="Agitator Drive",
                    electrical={"voltage": "600V", "powerKW": 45, "loadType": "Constant"},
                    purchasing={"workPackageId": "PKG-MECH-03", "status": "Engineering"},
                    location_id=leaching_area.id,
                )
            )
            # PH Transmitter
            assets.append(
                Asset(
                    tag=f"330-AIT-{300+i}",
                    description=f"Leach Tank {i} pH",
                    type=AssetType.INSTRUMENT,
                    project_id=project.id,
                    area="330",
                    system="Leaching",
                    io_type=IOType.AI,
                    manufacturer_part_id="Endress+Hauser CPS11D",
                    process={"minRange": 0, "maxRange": 14, "units": "pH"},
                    purchasing={"workPackageId": "PKG-INST-01", "status": "Ordered"},
                    location_id=leaching_area.id,
                )
            )

        # 340 - Flotation
        flotation_area = LBSNode(
            name="Flotation Circuit",
            type=LocationType.AREA,
            project_id=project.id,
            parent_id=site.id,
        )
        db.add(flotation_area)
        db.commit()
        db.refresh(flotation_area)

        # Flotation Cells
        for i in range(1, 5):
            assets.append(
                Asset(
                    tag=f"340-FC-{400+i}",
                    description=f"Rougher Cell {i}",
                    type=AssetType.MOTOR,
                    project_id=project.id,
                    area="340",
                    system="Flotation",
                    io_type=IOType.ETHERNET_IP,
                    manufacturer_part_id="Flotation Drive",
                    electrical={"voltage": "600V", "powerKW": 30, "loadType": "Constant"},
                    purchasing={"workPackageId": "PKG-MECH-04", "status": "Engineering"},
                    location_id=flotation_area.id,
                )
            )
            # Level Control Valve
            assets.append(
                Asset(
                    tag=f"340-LV-{400+i}",
                    description=f"Rougher Cell {i} Level Valve",
                    type=AssetType.VALVE,
                    project_id=project.id,
                    area="340",
                    system="Flotation",
                    io_type=IOType.AO,
                    manufacturer_part_id="Control Valve",
                    process={"fluid": "Slurry"},
                    purchasing={"workPackageId": "PKG-INST-01", "status": "Engineering"},
                    location_id=flotation_area.id,
                )
            )

        db.add_all(assets)
        db.commit()
        logger.info(f"Created {len(assets)} Assets")

        # 6. Create Connections
        # TODO: Add connections logic if needed for specific tests

        logger.info("Gold Mine data seeding completed successfully!")

    except Exception as e:
        logger.error(f"Error seeding data: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_data()
