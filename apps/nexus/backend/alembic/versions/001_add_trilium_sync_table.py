"""Add trilium_sync table for TriliumNext synchronization

Revision ID: 001_trilium_sync
Revises:
Create Date: 2024-11-29

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_trilium_sync'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create trilium_sync table
    op.create_table(
        'trilium_sync',
        sa.Column('nexus_note_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('trilium_note_id', sa.String(12), nullable=False),
        sa.Column('last_synced_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('trilium_utc_modified', sa.BigInteger(), nullable=True),
        sa.Column('sync_status', sa.String(20), nullable=False, server_default='synced'),
        sa.Column('source', sa.String(10), nullable=False, server_default='trilium'),
        sa.Column('trilium_type', sa.String(20), nullable=True),
        sa.Column('trilium_mime', sa.String(50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['nexus_note_id'], ['notes.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('nexus_note_id')
    )

    # Create indexes
    op.create_index('idx_trilium_sync_trilium_id', 'trilium_sync', ['trilium_note_id'], unique=True)
    op.create_index('idx_trilium_sync_status', 'trilium_sync', ['sync_status'])
    op.create_index('idx_trilium_sync_source', 'trilium_sync', ['source'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_trilium_sync_source', table_name='trilium_sync')
    op.drop_index('idx_trilium_sync_status', table_name='trilium_sync')
    op.drop_index('idx_trilium_sync_trilium_id', table_name='trilium_sync')

    # Drop table
    op.drop_table('trilium_sync')
