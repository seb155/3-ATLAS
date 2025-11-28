"""add_indexes_and_soft_delete

Revision ID: b3c4d5e6f7a8
Revises: 01b0b839868f
Create Date: 2025-11-28 12:00:00.000000

This migration adds:
1. Performance indexes on project_id columns
2. Soft delete columns (deleted_at) for data recovery
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b3c4d5e6f7a8'
down_revision: Union[str, None] = '01b0b839868f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ==========================================================================
    # PERFORMANCE INDEXES
    # ==========================================================================

    # Assets table - most queried table
    op.create_index('ix_asset_project_id', 'assets', ['project_id'], unique=False)
    op.create_index('ix_asset_type_project', 'assets', ['type', 'project_id'], unique=False)

    # LBS Nodes table
    op.create_index('ix_lbs_project_id', 'lbs_nodes', ['project_id'], unique=False)

    # Connections table
    op.create_index('ix_connection_project_id', 'connections', ['project_id'], unique=False)

    # ==========================================================================
    # SOFT DELETE COLUMNS
    # ==========================================================================

    # Assets table
    op.add_column('assets', sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True))
    op.create_index('ix_assets_deleted_at', 'assets', ['deleted_at'], unique=False)

    # LBS Nodes table
    op.add_column('lbs_nodes', sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True))
    op.create_index('ix_lbs_nodes_deleted_at', 'lbs_nodes', ['deleted_at'], unique=False)

    # Connections table
    op.add_column('connections', sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True))
    op.create_index('ix_connections_deleted_at', 'connections', ['deleted_at'], unique=False)


def downgrade() -> None:
    # ==========================================================================
    # REMOVE SOFT DELETE COLUMNS
    # ==========================================================================

    # Connections table
    op.drop_index('ix_connections_deleted_at', table_name='connections')
    op.drop_column('connections', 'deleted_at')

    # LBS Nodes table
    op.drop_index('ix_lbs_nodes_deleted_at', table_name='lbs_nodes')
    op.drop_column('lbs_nodes', 'deleted_at')

    # Assets table
    op.drop_index('ix_assets_deleted_at', table_name='assets')
    op.drop_column('assets', 'deleted_at')

    # ==========================================================================
    # REMOVE PERFORMANCE INDEXES
    # ==========================================================================

    op.drop_index('ix_connection_project_id', table_name='connections')
    op.drop_index('ix_lbs_project_id', table_name='lbs_nodes')
    op.drop_index('ix_asset_type_project', table_name='assets')
    op.drop_index('ix_asset_project_id', table_name='assets')
