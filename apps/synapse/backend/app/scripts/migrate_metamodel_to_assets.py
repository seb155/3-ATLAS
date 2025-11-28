"""
Migrate data from metamodel_nodes to assets table.

This script merges the two data systems into one unified assets table.
"""

from app.core.database import SessionLocal
from app.models.metamodel import MetamodelNode
from app.models.models import Asset, AssetType


def migrate_data():
    """Migrate metamodel_nodes data to assets table."""
    db = SessionLocal()

    try:
        # Get all nodes
        nodes = db.query(MetamodelNode).all()

        migrated = 0
        updated = 0
        skipped = 0
        errors = []

        print(f"Found {len(nodes)} nodes to process...")

        for node in nodes:
            try:
                # Check if already exists in assets
                existing = db.query(Asset).filter(Asset.id == node.id).first()

                if existing:
                    # Update existing asset with metamodel data
                    existing.discipline = node.discipline.value if node.discipline else None
                    existing.semantic_type = (
                        node.semantic_type.value if node.semantic_type else None
                    )
                    existing.lod = node.lod
                    existing.isa95_level = node.isa95_level

                    # Merge properties
                    if node.properties:
                        if not existing.properties:
                            existing.properties = {}
                        existing.properties.update(node.properties)

                    updated += 1
                    print(f"  ✓ Updated: {existing.tag}")

                else:
                    # Create new asset from node
                    # Try to convert type to AssetType enum
                    try:
                        asset_type = AssetType[node.type.upper()]
                    except (KeyError, AttributeError):
                        print(
                            f"  ⚠ Warning: Unknown type '{node.type}' "
                            f"for node {node.name}, skipping"
                        )
                        skipped += 1
                        continue

                    new_asset = Asset(
                        id=node.id,  # KEEP SAME ID for FK integrity!
                        tag=node.name,
                        type=asset_type,
                        project_id=node.project_id,
                        description=node.description,
                        discipline=node.discipline.value if node.discipline else None,
                        semantic_type=node.semantic_type.value if node.semantic_type else None,
                        lod=node.lod,
                        isa95_level=node.isa95_level,
                        properties=node.properties,
                        data_status=node.data_status,
                        confidence_score=node.confidence_score,
                        data_source_id=node.data_source_id,
                    )
                    db.add(new_asset)
                    migrated += 1
                    print(f"  ✓ Created: {new_asset.tag} ({asset_type.value})")

            except Exception as e:
                error_msg = f"  ✗ Error processing node {node.name}: {str(e)}"
                print(error_msg)
                errors.append(error_msg)
                continue

        # Commit all changes
        db.commit()

        print(f"\n{'='*50}")
        print("Migration Complete!")
        print(f"{'='*50}")
        print(f"  Created new:  {migrated}")
        print(f"  Updated:      {updated}")
        print(f"  Skipped:      {skipped}")
        print(f"  Errors:       {len(errors)}")

        if errors:
            print("\nErrors:")
            for err in errors:
                print(err)

        return migrated, updated, skipped, len(errors)

    except Exception as e:
        db.rollback()
        print(f"\n✗ CRITICAL ERROR during migration: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("Starting data migration from metamodel_nodes to assets...")
    print("=" * 50)
    migrate_data()
    print("\nMigration script finished!")
