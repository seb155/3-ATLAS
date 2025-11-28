"""convert_type_enum_to_string

Revision ID: c67fdf9ee9d0
Revises: 858a7c39edff
Create Date: 2025-11-22 02:14:37.598757

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c67fdf9ee9d0'
down_revision: Union[str, None] = '858a7c39edff'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Convert type from Enum to String for flexibility
    op.alter_column('assets', 'type',
                    type_=sa.String(),
                    existing_type=sa.Enum('INSTRUMENT', 'MOTOR', 'VALVE', 'CONTROL_SYSTEM', 'PUMP', 'TANK', name='assettype'),
                    postgresql_using='type::text',
                    nullable=False)


def downgrade() -> None:
    # Convert back from String to Enum
    op.alter_column('assets', 'type',
                    type_=sa.Enum('INSTRUMENT', 'MOTOR', 'VALVE', 'CONTROL_SYSTEM', 'PUMP', 'TANK', name='assettype'),
                    existing_type=sa.String(),
                    postgresql_using='type::assettype',
                    nullable=False)
