"""Add drawings table for Excalidraw integration

Revision ID: 002_drawings
Revises: 001_trilium_sync
Create Date: 2024-11-29

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '002_drawings'
down_revision: Union[str, None] = '001_trilium_sync'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create drawings table
    op.create_table(
        'drawings',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('description', sa.Text(), nullable=True, server_default=''),
        sa.Column('elements', postgresql.JSONB(), nullable=False, server_default='[]'),
        sa.Column('app_state', postgresql.JSONB(), nullable=True, server_default='{}'),
        sa.Column('files', postgresql.JSONB(), nullable=True, server_default='{}'),
        sa.Column('thumbnail', sa.Text(), nullable=True),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('parent_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('is_folder', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['parent_id'], ['drawings.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Add full-text search column (computed/generated)
    op.execute("""
        ALTER TABLE drawings
        ADD COLUMN content_tsvector TSVECTOR
        GENERATED ALWAYS AS (to_tsvector('english', coalesce(title, '') || ' ' || coalesce(description, ''))) STORED
    """)

    # Create indexes
    op.create_index('idx_drawings_user_id', 'drawings', ['user_id'])
    op.create_index('idx_drawings_parent_id', 'drawings', ['parent_id'])
    op.create_index('idx_drawings_title', 'drawings', ['title'])
    op.create_index('idx_drawings_content_tsvector', 'drawings', ['content_tsvector'], postgresql_using='gin')
    op.execute("CREATE INDEX idx_drawings_deleted_at ON drawings(deleted_at) WHERE deleted_at IS NULL")

    # Create note_drawing_embeds table
    op.create_table(
        'note_drawing_embeds',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('note_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('drawing_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('edit_mode', sa.String(10), nullable=False, server_default='modal'),
        sa.Column('width', sa.Integer(), nullable=False, server_default='800'),
        sa.Column('height', sa.Integer(), nullable=False, server_default='400'),
        sa.Column('position', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['note_id'], ['notes.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['drawing_id'], ['drawings.id'], ondelete='CASCADE'),
        sa.CheckConstraint("edit_mode IN ('modal', 'inline')", name='chk_edit_mode'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for embeds
    op.create_index('idx_note_drawing_embeds_note', 'note_drawing_embeds', ['note_id'])
    op.create_index('idx_note_drawing_embeds_drawing', 'note_drawing_embeds', ['drawing_id'])


def downgrade() -> None:
    # Drop note_drawing_embeds indexes and table
    op.drop_index('idx_note_drawing_embeds_drawing', table_name='note_drawing_embeds')
    op.drop_index('idx_note_drawing_embeds_note', table_name='note_drawing_embeds')
    op.drop_table('note_drawing_embeds')

    # Drop drawings indexes and table
    op.execute("DROP INDEX IF EXISTS idx_drawings_deleted_at")
    op.drop_index('idx_drawings_content_tsvector', table_name='drawings')
    op.drop_index('idx_drawings_title', table_name='drawings')
    op.drop_index('idx_drawings_parent_id', table_name='drawings')
    op.drop_index('idx_drawings_user_id', table_name='drawings')
    op.drop_table('drawings')
