"""Add workflow_events and versioning tables

Revision ID: f1a2b3c4d5e6
Revises: 01b0b839868f
Create Date: 2025-11-28 10:00:00.000000

This migration adds the complete traceability system:
- workflow_events: Central event log for all actions
- asset_versions: Full snapshot versioning
- property_changes: Field-level change tracking
- batch_operations: Group operations for rollback
- asset_changes: Simple view for quick queries

Design based on: .dev/design/2025-11-28-whiteboard-session.md
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'f1a2b3c4d5e6'
down_revision: Union[str, None] = 'b3c4d5e6f7a8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create ENUM types
    log_level_enum = sa.Enum(
        'TRACE', 'DEBUG', 'INFO', 'WARN', 'ERROR', 'FATAL',
        name='loglevel'
    )
    log_source_enum = sa.Enum(
        'SYSTEM', 'IMPORT', 'RULE', 'PACKAGE', 'USER', 'API', 'ROLLBACK',
        name='logsource'
    )
    workflow_action_enum = sa.Enum(
        'CREATE', 'UPDATE', 'DELETE', 'EXECUTE', 'EXPORT', 'IMPORT', 'ROLLBACK', 'VALIDATE', 'LINK',
        name='workflowactiontype'
    )
    workflow_status_enum = sa.Enum(
        'PENDING', 'IN_PROGRESS', 'COMPLETED', 'FAILED', 'ROLLED_BACK',
        name='workflowstatus'
    )
    change_source_enum = sa.Enum(
        'USER', 'RULE', 'IMPORT', 'API', 'ROLLBACK', 'SYSTEM',
        name='changesource'
    )
    batch_operation_type_enum = sa.Enum(
        'IMPORT', 'RULE_EXECUTION', 'BULK_UPDATE', 'BULK_DELETE', 'PACKAGE_GENERATION',
        name='batchoperationtype'
    )

    # Create ENUMs in database
    log_level_enum.create(op.get_bind(), checkfirst=True)
    log_source_enum.create(op.get_bind(), checkfirst=True)
    workflow_action_enum.create(op.get_bind(), checkfirst=True)
    workflow_status_enum.create(op.get_bind(), checkfirst=True)
    change_source_enum.create(op.get_bind(), checkfirst=True)
    batch_operation_type_enum.create(op.get_bind(), checkfirst=True)

    # 1. Create batch_operations table first (referenced by asset_versions)
    op.create_table(
        'batch_operations',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('operation_type', sa.Enum(
            'IMPORT', 'RULE_EXECUTION', 'BULK_UPDATE', 'BULK_DELETE', 'PACKAGE_GENERATION',
            name='batchoperationtype', create_type=False
        ), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('project_id', sa.String(), nullable=False),
        sa.Column('affected_assets', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by', sa.String(), nullable=True),
        sa.Column('is_rolled_back', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('rolled_back_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('rolled_back_by', sa.String(), nullable=True),
        sa.Column('rollback_reason', sa.Text(), nullable=True),
        sa.Column('correlation_id', sa.String(), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id']),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.ForeignKeyConstraint(['rolled_back_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_batch_operations_operation_type', 'batch_operations', ['operation_type'])
    op.create_index('ix_batch_operations_project_id', 'batch_operations', ['project_id'])
    op.create_index('ix_batch_operations_is_rolled_back', 'batch_operations', ['is_rolled_back'])
    op.create_index('ix_batch_operations_correlation_id', 'batch_operations', ['correlation_id'])
    op.create_index('ix_batch_operations_project_started', 'batch_operations', ['project_id', 'started_at'])

    # 2. Create workflow_events table
    op.create_table(
        'workflow_events',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('level', sa.Enum(
            'TRACE', 'DEBUG', 'INFO', 'WARN', 'ERROR', 'FATAL',
            name='loglevel', create_type=False
        ), nullable=False),
        sa.Column('source', sa.Enum(
            'SYSTEM', 'IMPORT', 'RULE', 'PACKAGE', 'USER', 'API', 'ROLLBACK',
            name='logsource', create_type=False
        ), nullable=False),
        sa.Column('action_type', sa.Enum(
            'CREATE', 'UPDATE', 'DELETE', 'EXECUTE', 'EXPORT', 'IMPORT', 'ROLLBACK', 'VALIDATE', 'LINK',
            name='workflowactiontype', create_type=False
        ), nullable=False),
        sa.Column('project_id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=True),
        sa.Column('session_id', sa.String(), nullable=True),
        sa.Column('entity_type', sa.String(50), nullable=True),
        sa.Column('entity_id', sa.String(), nullable=True),
        sa.Column('entity_tag', sa.String(100), nullable=True),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('details', sa.JSON(), nullable=True, server_default='{}'),
        sa.Column('parent_event_id', sa.String(), nullable=True),
        sa.Column('correlation_id', sa.String(), nullable=False),
        sa.Column('status', sa.Enum(
            'PENDING', 'IN_PROGRESS', 'COMPLETED', 'FAILED', 'ROLLED_BACK',
            name='workflowstatus', create_type=False
        ), nullable=False, server_default='COMPLETED'),
        sa.Column('duration_ms', sa.Integer(), nullable=True),
        sa.Column('error', sa.Text(), nullable=True),
        sa.Column('fbs_code', sa.String(20), nullable=True),
        sa.Column('lbs_code', sa.String(20), nullable=True),
        sa.Column('discipline', sa.String(50), nullable=True),
        sa.Column('package_code', sa.String(50), nullable=True),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['parent_event_id'], ['workflow_events.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_workflow_events_level', 'workflow_events', ['level'])
    op.create_index('ix_workflow_events_source', 'workflow_events', ['source'])
    op.create_index('ix_workflow_events_action_type', 'workflow_events', ['action_type'])
    op.create_index('ix_workflow_events_project_id', 'workflow_events', ['project_id'])
    op.create_index('ix_workflow_events_user_id', 'workflow_events', ['user_id'])
    op.create_index('ix_workflow_events_session_id', 'workflow_events', ['session_id'])
    op.create_index('ix_workflow_events_entity_type', 'workflow_events', ['entity_type'])
    op.create_index('ix_workflow_events_entity_id', 'workflow_events', ['entity_id'])
    op.create_index('ix_workflow_events_correlation_id', 'workflow_events', ['correlation_id'])
    op.create_index('ix_workflow_events_project_timestamp', 'workflow_events', ['project_id', 'timestamp'])
    op.create_index('ix_workflow_events_entity', 'workflow_events', ['entity_type', 'entity_id'])
    op.create_index('ix_workflow_events_breakdown', 'workflow_events', ['fbs_code', 'lbs_code', 'discipline'])

    # 3. Create asset_versions table
    op.create_table(
        'asset_versions',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('asset_id', sa.String(), nullable=False),
        sa.Column('version_number', sa.Integer(), nullable=False),
        sa.Column('snapshot', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('created_by', sa.String(), nullable=True),
        sa.Column('change_reason', sa.String(500), nullable=True),
        sa.Column('change_source', sa.Enum(
            'USER', 'RULE', 'IMPORT', 'API', 'ROLLBACK', 'SYSTEM',
            name='changesource', create_type=False
        ), nullable=False, server_default='USER'),
        sa.Column('event_id', sa.String(), nullable=True),
        sa.Column('batch_id', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['asset_id'], ['assets.id']),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.ForeignKeyConstraint(['event_id'], ['workflow_events.id']),
        sa.ForeignKeyConstraint(['batch_id'], ['batch_operations.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_asset_versions_asset_id', 'asset_versions', ['asset_id'])
    op.create_index('ix_asset_versions_batch_id', 'asset_versions', ['batch_id'])
    op.create_index('ix_asset_versions_asset_version', 'asset_versions', ['asset_id', 'version_number'])

    # 4. Create property_changes table
    op.create_table(
        'property_changes',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('asset_id', sa.String(), nullable=False),
        sa.Column('version_id', sa.String(), nullable=False),
        sa.Column('property_name', sa.String(100), nullable=False),
        sa.Column('property_path', sa.String(500), nullable=True),
        sa.Column('old_value', sa.JSON(), nullable=True),
        sa.Column('new_value', sa.JSON(), nullable=True),
        sa.Column('changed_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('changed_by', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['asset_id'], ['assets.id']),
        sa.ForeignKeyConstraint(['version_id'], ['asset_versions.id']),
        sa.ForeignKeyConstraint(['changed_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_property_changes_asset_id', 'property_changes', ['asset_id'])
    op.create_index('ix_property_changes_version_id', 'property_changes', ['version_id'])
    op.create_index('ix_property_changes_asset_property', 'property_changes', ['asset_id', 'property_name'])

    # 5. Create asset_changes table (simple view)
    op.create_table(
        'asset_changes',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('event_id', sa.String(), nullable=False),
        sa.Column('asset_id', sa.String(), nullable=False),
        sa.Column('field_name', sa.String(100), nullable=False),
        sa.Column('old_value', sa.JSON(), nullable=True),
        sa.Column('new_value', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['event_id'], ['workflow_events.id']),
        sa.ForeignKeyConstraint(['asset_id'], ['assets.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_asset_changes_event_id', 'asset_changes', ['event_id'])
    op.create_index('ix_asset_changes_asset_id', 'asset_changes', ['asset_id'])


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('asset_changes')
    op.drop_table('property_changes')
    op.drop_table('asset_versions')
    op.drop_table('workflow_events')
    op.drop_table('batch_operations')

    # Drop ENUM types
    op.execute('DROP TYPE IF EXISTS batchoperationtype')
    op.execute('DROP TYPE IF EXISTS changesource')
    op.execute('DROP TYPE IF EXISTS workflowstatus')
    op.execute('DROP TYPE IF EXISTS workflowactiontype')
    op.execute('DROP TYPE IF EXISTS logsource')
    op.execute('DROP TYPE IF EXISTS loglevel')
