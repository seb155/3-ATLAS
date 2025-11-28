"""
Seed script for Client and Project data.

Creates sample clients and projects for testing multi-project functionality.
"""

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.auth import Client, Project


def seed_clients_projects():
    db: Session = SessionLocal()

    try:
        # Check if data already exists
        existing_clients = db.query(Client).count()
        if existing_clients > 0:
            print(f"✅ Clients already exist ({existing_clients}). Skipping seed.")
            return

        # Create Clients
        clients_data = [
            {"name": "AuruMax Mining Corp", "contact_email": "projects@aurumax.com"},
            {"name": "BioTech Industries", "contact_email": "engineering@biotech-ind.com"},
            {"name": "Metropolis Water Treatment", "contact_email": "capital@metropolis-water.ca"},
        ]

        clients = []
        for client_data in clients_data:
            client = Client(**client_data)
            db.add(client)
            clients.append(client)

        db.commit()

        # Refresh to get IDs
        for client in clients:
            db.refresh(client)

        print(f"✅ Created {len(clients)} clients")

        # Create Projects
        projects_data = [
            # AuruMax projects
            {
                "name": "Gold Mine Expansion - Phase 3",
                "client_id": clients[0].id,
                "description": "150 new instruments, PlantPAX upgrade",
                "status": "ACTIVE",
            },
            {
                "name": "Crusher Plant Automation",
                "client_id": clients[0].id,
                "description": "New crusher control system",
                "status": "ACTIVE",
            },
            # BioTech projects
            {
                "name": "Fermentation Tank Instrumentation",
                "client_id": clients[1].id,
                "description": "20 bioreactors with advanced control",
                "status": "ACTIVE",
            },
            {
                "name": "Clean Room HVAC Upgrade",
                "client_id": clients[1].id,
                "description": "Environmental monitoring and control",
                "status": "HOLD",
            },
            # Metropolis Water projects
            {
                "name": "Water Treatment Plant - South",
                "client_id": clients[2].id,
                "description": "Complete automation retrofit",
                "status": "ACTIVE",
            },
            {
                "name": "Pump Station #7 Controls",
                "client_id": clients[2].id,
                "description": "VFD and SCADA integration",
                "status": "ACTIVE",
            },
        ]

        projects = []
        for project_data in projects_data:
            project = Project(**project_data)
            db.add(project)
            projects.append(project)

        db.commit()

        print(f"✅ Created {len(projects)} projects")
        print("\n📋 Summary:")
        print(f"  - Clients: {len(clients)}")
        print(f"  - Projects: {len(projects)}")
        print(f"    - ACTIVE: {sum(1 for p in projects if p.status == 'ACTIVE')}")
        print(f"    - HOLD: {sum(1 for p in projects if p.status == 'HOLD')}")

    except Exception as e:
        print(f"❌ Error seeding data: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("🌱 Seeding clients and projects...")
    seed_clients_projects()
    print("✅ Seed complete!")
