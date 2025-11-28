"""point_edges_to_assets

Revision ID: 6faa9ed84b81
Revises: c67fdf9ee9d0
Create Date: 2025-11-22 02:15:50.946623

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6faa9ed84b81'
down_revision: Union[str, None] = 'c67fdf9ee9d0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
