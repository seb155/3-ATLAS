"""add_rule_enforcement_and_conflict_tracking

Revision ID: a1b2c3d4e5f6
Revises: d2b09ee54e28
Create Date: 2025-11-21 02:10:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = 'd2b09ee54e28'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new columns to rule_definitions table
    op.add_column('rule_definitions', sa.Column('category', sa.String(), nullable=True))
    op.add_column('rule_definitions', sa.Column('is_enforced', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('rule_definitions', sa.Column('overrides_rule_id', sa.String(), nullable=True))
    op.add_column('rule_definitions', sa.Column('conflicts_with', sa.JSON(), nullable=True))
    
    # Create indexes
    op.create_index(op.f('ix_rule_definitions_category'), 'rule_definitions', ['category'], unique=False)
    op.create_index(op.f('ix_rule_definitions_is_enforced'), 'rule_definitions', ['is_enforced'], unique=False)
    
    # Create foreign key constraint for overrides_rule_id
    op.create_foreign_key(
        'fk_rule_definitions_overrides_rule_id', 
        'rule_definitions', 
        'rule_definitions', 
        ['overrides_rule_id'], 
        ['id']
    )


def downgrade() -> None:
    # Drop foreign key constraint
    op.drop_constraint('fk_rule_definitions_overrides_rule_id', 'rule_definitions', type_='foreignkey')
    
    # Drop indexes
    op.drop_index(op.f('ix_rule_definitions_is_enforced'), table_name='rule_definitions')
    op.drop_index(op.f('ix_rule_definitions_category'), table_name='rule_definitions')
    
    # Drop columns
    op.drop_column('rule_definitions', 'conflicts_with')
    op.drop_column('rule_definitions', 'overrides_rule_id')
    op.drop_column('rule_definitions', 'is_enforced')
    op.drop_column('rule_definitions', 'category')
