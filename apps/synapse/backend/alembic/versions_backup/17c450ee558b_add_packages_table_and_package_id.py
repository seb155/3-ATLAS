"""add_packages_table_and_package_id

Revision ID: 17c450ee558b
Revises: d21466a69190
Create Date: 2025-11-22 19:36:46.951987

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '17c450ee558b'
down_revision: Union[str, None] = 'd21466a69190'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create packages table
    op.create_table(
        'packages',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('project_id', sa.String(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_packages_project_id'), 'packages', ['project_id'], unique=False)
    op.create_index(op.f('ix_packages_status'), 'packages', ['status'], unique=False)
    
    # Add package_id column to assets table
    op.add_column('assets', sa.Column('package_id', sa.String(), nullable=True))
    op.create_foreign_key('fk_assets_package_id', 'assets', 'packages', ['package_id'], ['id'])
    op.create_index(op.f('ix_assets_package_id'), 'assets', ['package_id'], unique=False)


def downgrade() -> None:
    # Remove package_id from assets
    op.drop_index(op.f('ix_assets_package_id'), table_name='assets')
    op.drop_constraint('fk_assets_package_id', 'assets', type_='foreignkey')
    op.drop_column('assets', 'package_id')
    
    # Drop packages table
    op.drop_index(op.f('ix_packages_status'), table_name='packages')
    op.drop_index(op.f('ix_packages_project_id'), table_name='packages')
    op.drop_table('packages')
