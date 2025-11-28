"""add_metamodel_columns_to_assets

Revision ID: 858a7c39edff
Revises: 6f5972dbcbb6
Create Date: 2025-11-22 02:12:37.102997

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '858a7c39edff'
down_revision: Union[str, None] = '6f5972dbcbb6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add metamodel columns to assets table
    op.add_column('assets', sa.Column('discipline', sa.String(), nullable=True))
    op.add_column('assets', sa.Column('semantic_type', sa.String(), nullable=True))
    op.add_column('assets', sa.Column('lod', sa.Integer(), nullable=True))
    op.add_column('assets', sa.Column('isa95_level', sa.Integer(), nullable=True))
    op.add_column('assets', sa.Column('properties', sa.JSON(), nullable=True))
    
    # Add indexes for performance
    op.create_index('ix_assets_discipline', 'assets', ['discipline'])
    op.create_index('ix_assets_semantic_type', 'assets', ['semantic_type'])


def downgrade() -> None:
    # Remove indexes
    op.drop_index('ix_assets_semantic_type', 'assets')
    op.drop_index('ix_assets_discipline', 'assets')
    
    # Remove columns
    op.drop_column('assets', 'properties')
    op.drop_column('assets', 'isa95_level')
    op.drop_column('assets', 'lod')
    op.drop_column('assets', 'semantic_type')
    op.drop_column('assets', 'discipline')
