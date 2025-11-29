"""add_cardinality_to_metamodel_edges

Revision ID: 4f51457cb3c5
Revises: 0001
Create Date: 2025-11-29 00:14:42.695379

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4f51457cb3c5'
down_revision: Union[str, None] = '0001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add cardinality column to metamodel_edges table
    op.add_column('metamodel_edges', sa.Column('cardinality', sa.String(), server_default='1:N', nullable=True))


def downgrade() -> None:
    # Remove cardinality column from metamodel_edges table
    op.drop_column('metamodel_edges', 'cardinality')
