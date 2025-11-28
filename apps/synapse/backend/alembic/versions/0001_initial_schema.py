"""Initial Schema - Complete Database Setup

Revision ID: 0001
Revises: None
Create Date: 2025-11-28

This migration creates all tables for SYNAPSE platform:
- Authentication: users, clients, projects
- Assets: assets, lbs_nodes, connections
- Rules: rule_definitions, rule_executions
- Cables: cables, cable_types, cable_sizing_rules
- Packages: packages
- Metamodel: metamodel_nodes, metamodel_edges
- Ingestion: data_sources, staged_rows
- Workflow: workflow_events, asset_versions, property_changes, batch_operations
- Audit: audit_logs, action_logs, asset_changes
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = '0001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ==========================================================================
    # CORE TABLES
    # ==========================================================================

    # Users
    op.create_table('users',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('full_name', sa.String(), nullable=True),
        sa.Column('role', sa.Enum('ADMIN', 'ENGINEER', 'VIEWER', 'CLIENT', name='userrole'), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)

    # Clients
    op.create_table('clients',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('contact_email', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )

    # Projects
    op.create_table('projects',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('client_id', sa.String(), nullable=False),
        sa.Column('country', sa.String(), nullable=True),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=True),
        sa.ForeignKeyConstraint(['client_id'], ['clients.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # ==========================================================================
    # LOCATION BREAKDOWN STRUCTURE
    # ==========================================================================

    op.create_table('lbs_nodes',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('type', sa.Enum('SITE', 'AREA', 'EHOUSE', 'ROOM', 'CABINET', 'JUNCTION_BOX', name='locationtype'), nullable=False),
        sa.Column('project_id', sa.String(), nullable=False),
        sa.Column('parent_id', sa.String(), nullable=True),
        sa.Column('capacity_slots', sa.Integer(), nullable=True),
        sa.Column('design_heat_dissipation', sa.Float(), nullable=True),
        sa.Column('ip_rating', sa.String(), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['parent_id'], ['lbs_nodes.id']),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_lbs_nodes_project_id', 'lbs_nodes', ['project_id'])
    op.create_index('ix_lbs_nodes_deleted_at', 'lbs_nodes', ['deleted_at'])

    # ==========================================================================
    # PACKAGES
    # ==========================================================================

    op.create_table('packages',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('project_id', sa.String(), nullable=False),
        sa.Column('status', sa.Enum('OPEN', 'ISSUED', 'CLOSED', name='packagestatus'), nullable=True, server_default='OPEN'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=True),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_packages_project_id', 'packages', ['project_id'])

    # ==========================================================================
    # ASSETS
    # ==========================================================================

    op.create_table('assets',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('tag', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('project_id', sa.String(), nullable=False),
        # FBS
        sa.Column('area', sa.String(), nullable=True),
        sa.Column('system', sa.String(), nullable=True),
        # Domains
        sa.Column('io_type', sa.Enum('AI', 'AO', 'DI', 'DO', 'PROFIBUS', 'ETHERNET', 'HARDWIRED', 'PROFINET', 'ETHERNET_IP', 'MODBUS_TCP', name='iotype'), nullable=True),
        sa.Column('mechanical', sa.JSON(), nullable=True),
        sa.Column('electrical', sa.JSON(), nullable=True),
        sa.Column('process', sa.JSON(), nullable=True),
        sa.Column('purchasing', sa.JSON(), nullable=True),
        sa.Column('manufacturer_part_id', sa.String(), nullable=True),
        # Data Quality
        sa.Column('data_status', sa.Enum('FRESH_IMPORT', 'IN_REVIEW', 'VALIDATED', 'ERROR', name='assetdatastatus'), nullable=True, server_default='FRESH_IMPORT'),
        sa.Column('confidence_score', sa.Float(), nullable=True, server_default='1.0'),
        sa.Column('data_source_id', sa.String(), nullable=True),
        # Metamodel
        sa.Column('discipline', sa.String(), nullable=True),
        sa.Column('semantic_type', sa.String(), nullable=True),
        sa.Column('lod', sa.Integer(), nullable=True),
        sa.Column('isa95_level', sa.Integer(), nullable=True),
        sa.Column('properties', sa.JSON(), nullable=True),
        # Links
        sa.Column('location_id', sa.String(), nullable=True),
        sa.Column('package_id', sa.String(), nullable=True),
        # Soft delete
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['location_id'], ['lbs_nodes.id']),
        sa.ForeignKeyConstraint(['package_id'], ['packages.id']),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tag', 'project_id', name='uix_project_tag')
    )
    op.create_index('ix_assets_tag', 'assets', ['tag'])
    op.create_index('ix_assets_project_id', 'assets', ['project_id'])
    op.create_index('ix_assets_type_project', 'assets', ['type', 'project_id'])
    op.create_index('ix_assets_discipline', 'assets', ['discipline'])
    op.create_index('ix_assets_semantic_type', 'assets', ['semantic_type'])
    op.create_index('ix_assets_data_status', 'assets', ['data_status'])
    op.create_index('ix_assets_deleted_at', 'assets', ['deleted_at'])
    op.create_index('ix_assets_package_id', 'assets', ['package_id'])

    # ==========================================================================
    # CONNECTIONS
    # ==========================================================================

    op.create_table('connections',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('from_id', sa.String(), nullable=False),
        sa.Column('to_id', sa.String(), nullable=False),
        sa.Column('project_id', sa.String(), nullable=False),
        sa.Column('type', sa.String(), nullable=True),
        sa.Column('cable_tag', sa.String(), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_connections_project_id', 'connections', ['project_id'])
    op.create_index('ix_connections_deleted_at', 'connections', ['deleted_at'])

    # ==========================================================================
    # METAMODEL
    # ==========================================================================

    op.create_table('metamodel_nodes',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('discipline', sa.Enum('PROCESS', 'ELECTRICAL', 'AUTOMATION', 'PROCUREMENT', 'MECHANICAL', 'PROJECT', name='disciplinetype'), nullable=True),
        sa.Column('semantic_type', sa.String(), nullable=True),
        sa.Column('lod', sa.Integer(), nullable=True),
        sa.Column('isa95_level', sa.Integer(), nullable=True),
        sa.Column('properties', sa.JSON(), nullable=True),
        sa.Column('project_id', sa.String(), nullable=True),
        sa.Column('data_status', sa.Enum('FRESH_IMPORT', 'IN_REVIEW', 'VALIDATED', 'ERROR', name='assetdatastatus'), nullable=True),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_metamodel_nodes_type', 'metamodel_nodes', ['type'])
    op.create_index('ix_metamodel_nodes_discipline', 'metamodel_nodes', ['discipline'])
    op.create_index('ix_metamodel_nodes_project_id', 'metamodel_nodes', ['project_id'])
    op.create_index('ix_metamodel_nodes_data_status', 'metamodel_nodes', ['data_status'])

    op.create_table('metamodel_edges',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('source_node_id', sa.String(), nullable=False),
        sa.Column('target_node_id', sa.String(), nullable=False),
        sa.Column('relation_type', sa.String(), nullable=False),
        sa.Column('discipline', sa.String(), nullable=True),
        sa.Column('properties', sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_metamodel_edges_source', 'metamodel_edges', ['source_node_id'])
    op.create_index('ix_metamodel_edges_target', 'metamodel_edges', ['target_node_id'])
    op.create_index('ix_metamodel_edges_relation', 'metamodel_edges', ['relation_type'])

    # ==========================================================================
    # RULES
    # ==========================================================================

    op.create_table('rule_definitions',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        # Source & Priority
        sa.Column('source', sa.Enum('FIRM', 'COUNTRY', 'PROJECT', 'CLIENT', name='rulesource'), nullable=False),
        sa.Column('source_id', sa.String(), nullable=True),
        sa.Column('priority', sa.Integer(), nullable=False, server_default='10'),
        # Categorization
        sa.Column('discipline', sa.String(), nullable=True),
        sa.Column('category', sa.String(), nullable=True),
        sa.Column('action_type', sa.Enum('CREATE_CHILD', 'CREATE_CABLE', 'CREATE_RELATIONSHIP', 'SET_PROPERTY', 'CREATE_PACKAGE', 'ALLOCATE_IO', 'VALIDATE', name='ruleactiontype'), nullable=False),
        # Enforcement
        sa.Column('is_enforced', sa.Boolean(), nullable=False, server_default='false'),
        # Rule Logic
        sa.Column('condition', sa.JSON(), nullable=False),
        sa.Column('action', sa.JSON(), nullable=False),
        # Conflict Tracking
        sa.Column('overrides_rule_id', sa.String(), nullable=True),
        sa.Column('conflicts_with', sa.JSON(), nullable=True),
        # Metadata
        sa.Column('validation_status', sa.Enum('DRAFT', 'DEV_VALIDATED', 'PROD_READY', 'DEPRECATED', name='rulevalidationstatus'), nullable=True, server_default='DRAFT'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_by', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=True),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
        # Execution Stats
        sa.Column('execution_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('last_executed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('success_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('failure_count', sa.Integer(), nullable=False, server_default='0'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.ForeignKeyConstraint(['overrides_rule_id'], ['rule_definitions.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_rule_definitions_name', 'rule_definitions', ['name'])
    op.create_index('ix_rule_definitions_source', 'rule_definitions', ['source'])
    op.create_index('ix_rule_definitions_priority', 'rule_definitions', ['priority'])
    op.create_index('ix_rule_definitions_discipline', 'rule_definitions', ['discipline'])
    op.create_index('ix_rule_definitions_category', 'rule_definitions', ['category'])
    op.create_index('ix_rule_definitions_action_type', 'rule_definitions', ['action_type'])
    op.create_index('ix_rule_definitions_is_active', 'rule_definitions', ['is_active'])
    op.create_index('ix_rule_definitions_is_enforced', 'rule_definitions', ['is_enforced'])
    op.create_index('ix_rule_definitions_validation_status', 'rule_definitions', ['validation_status'])

    op.create_table('rule_executions',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('rule_id', sa.String(), nullable=False),
        sa.Column('project_id', sa.String(), nullable=False),
        sa.Column('asset_id', sa.String(), nullable=True),
        sa.Column('action_type', sa.String(), nullable=False),
        sa.Column('action_taken', sa.Text(), nullable=False),
        sa.Column('condition_matched', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_entity_id', sa.String(), nullable=True),
        sa.Column('created_entity_type', sa.String(), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=True),
        sa.Column('execution_time_ms', sa.Integer(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('stack_trace', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id']),
        sa.ForeignKeyConstraint(['rule_id'], ['rule_definitions.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_rule_executions_rule_id', 'rule_executions', ['rule_id'])
    op.create_index('ix_rule_executions_project_id', 'rule_executions', ['project_id'])
    op.create_index('ix_rule_executions_asset_id', 'rule_executions', ['asset_id'])
    op.create_index('ix_rule_executions_timestamp', 'rule_executions', ['timestamp'])

    # ==========================================================================
    # CABLES
    # ==========================================================================

    op.create_table('cable_types',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('manufacturer', sa.String(100), nullable=True),
        sa.Column('part_number', sa.String(100), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('cable_family', sa.String(100), nullable=True),
        sa.Column('cable_type', sa.String(50), nullable=True),
        sa.Column('conductor_material', sa.String(20), nullable=True),
        sa.Column('conductor_size', sa.String(20), nullable=True),
        sa.Column('number_of_conductors', sa.Integer(), nullable=True),
        sa.Column('insulation_type', sa.String(50), nullable=True),
        sa.Column('voltage_rating', sa.String(20), nullable=True),
        sa.Column('current_rating_amps', sa.Float(), nullable=True),
        sa.Column('properties', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_cable_types_cable_type', 'cable_types', ['cable_type'])
    op.create_index('ix_cable_types_manufacturer', 'cable_types', ['manufacturer'])

    op.create_table('cable_sizing_rules',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('code_standard', sa.String(50), nullable=False),
        sa.Column('voltage_level', sa.String(20), nullable=True),
        sa.Column('conductor_size', sa.String(20), nullable=False),
        sa.Column('ampacity_amps', sa.Float(), nullable=False),
        sa.Column('derating_factors', sa.JSON(), nullable=True),
        sa.Column('resistance_ohm_per_km', sa.Float(), nullable=True),
        sa.Column('properties', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_cable_sizing_rules_code_standard', 'cable_sizing_rules', ['code_standard'])

    op.create_table('cables',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('project_id', sa.String(), nullable=False),
        sa.Column('tag', sa.String(50), nullable=False),
        sa.Column('cable_type', sa.String(50), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('from_asset_id', sa.String(), nullable=True),
        sa.Column('to_asset_id', sa.String(), nullable=True),
        sa.Column('conductor_size', sa.String(20), nullable=True),
        sa.Column('length_meters', sa.Float(), nullable=True),
        sa.Column('voltage_drop_volts', sa.Float(), nullable=True),
        sa.Column('voltage_drop_percent', sa.Float(), nullable=True),
        sa.Column('code_standard', sa.String(50), nullable=True),
        sa.Column('cable_type_id', sa.UUID(), nullable=True),
        sa.Column('properties', sa.JSON(), nullable=True),
        sa.Column('created_by_rule_id', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('status', sa.String(20), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=True),
        sa.ForeignKeyConstraint(['cable_type_id'], ['cable_types.id']),
        sa.ForeignKeyConstraint(['created_by_rule_id'], ['rule_definitions.id']),
        sa.ForeignKeyConstraint(['from_asset_id'], ['assets.id']),
        sa.ForeignKeyConstraint(['to_asset_id'], ['assets.id']),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_cables_tag', 'cables', ['tag'])
    op.create_index('ix_cables_project_id', 'cables', ['project_id'])
    op.create_index('ix_cables_cable_type', 'cables', ['cable_type'])

    # ==========================================================================
    # INGESTION
    # ==========================================================================

    op.create_table('data_sources',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('project_id', sa.String(), nullable=False),
        sa.Column('filename', sa.String(), nullable=False),
        sa.Column('file_type', sa.String(), nullable=True),
        sa.Column('file_size', sa.Integer(), nullable=True),
        sa.Column('row_count', sa.Integer(), nullable=True),
        sa.Column('column_count', sa.Integer(), nullable=True),
        sa.Column('headers', sa.JSON(), nullable=True),
        sa.Column('column_mapping', sa.JSON(), nullable=True),
        sa.Column('status', sa.Enum('PENDING', 'MAPPING', 'VALIDATING', 'IMPORTING', 'COMPLETED', 'FAILED', name='importstatus'), nullable=True, server_default='PENDING'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('stats', sa.JSON(), nullable=True),
        sa.Column('uploaded_by', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id']),
        sa.ForeignKeyConstraint(['uploaded_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_data_sources_project_id', 'data_sources', ['project_id'])
    op.create_index('ix_data_sources_status', 'data_sources', ['status'])

    op.create_table('staged_rows',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('data_source_id', sa.String(), nullable=False),
        sa.Column('row_number', sa.Integer(), nullable=False),
        sa.Column('raw_data', sa.JSON(), nullable=False),
        sa.Column('mapped_data', sa.JSON(), nullable=True),
        sa.Column('detected_type', sa.Enum('ASSET', 'CONNECTION', 'LOCATION', 'UNKNOWN', name='detectedtype'), nullable=True, server_default='UNKNOWN'),
        sa.Column('status', sa.Enum('PENDING', 'VALID', 'WARNING', 'ERROR', 'IMPORTED', name='ingeststatus'), nullable=True, server_default='PENDING'),
        sa.Column('validation_errors', sa.JSON(), nullable=True),
        sa.Column('created_asset_id', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['data_source_id'], ['data_sources.id']),
        sa.ForeignKeyConstraint(['created_asset_id'], ['assets.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_staged_rows_data_source_id', 'staged_rows', ['data_source_id'])
    op.create_index('ix_staged_rows_status', 'staged_rows', ['status'])

    # ==========================================================================
    # AUDIT & ACTION LOGS
    # ==========================================================================

    op.create_table('audit_logs',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=True),
        sa.Column('project_id', sa.String(), nullable=True),
        sa.Column('action', sa.String(), nullable=False),
        sa.Column('entity_type', sa.String(), nullable=False),
        sa.Column('entity_id', sa.String(), nullable=False),
        sa.Column('changes', sa.JSON(), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=True),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('action_logs',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('project_id', sa.String(), nullable=True),
        sa.Column('parent_id', sa.UUID(), nullable=True),
        sa.Column('action_type', sa.Enum('RULE_EXECUTION', 'CREATE', 'UPDATE', 'LINK', 'ERROR', name='actiontype'), nullable=False),
        sa.Column('entity_type', sa.String(), nullable=True),
        sa.Column('entity_id', sa.UUID(), nullable=True),
        sa.Column('discipline', sa.Enum('PROCESS', 'ELECTRICAL', 'AUTOMATION', 'PROCUREMENT', 'MECHANICAL', 'PROJECT', name='disciplinetype'), nullable=True),
        sa.Column('description', sa.String(), nullable=False),
        sa.Column('details', sa.JSON(), nullable=True),
        sa.Column('status', sa.Enum('COMPLETED', 'ROLLED_BACK', 'FAILED', 'WARNING', name='actionstatus'), nullable=True, server_default='COMPLETED'),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=True),
        sa.ForeignKeyConstraint(['parent_id'], ['action_logs.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # ==========================================================================
    # WORKFLOW EVENTS & VERSIONING
    # ==========================================================================

    op.create_table('batch_operations',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('operation_type', sa.Enum('IMPORT', 'RULE_EXECUTION', 'BULK_UPDATE', 'BULK_DELETE', 'PACKAGE_GENERATION', name='batchoperationtype'), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('project_id', sa.String(), nullable=False),
        sa.Column('affected_assets', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
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
    op.create_index('ix_batch_operations_correlation_id', 'batch_operations', ['correlation_id'])
    op.create_index('ix_batch_operations_is_rolled_back', 'batch_operations', ['is_rolled_back'])

    op.create_table('workflow_events',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('level', sa.Enum('TRACE', 'DEBUG', 'INFO', 'WARN', 'ERROR', 'FATAL', name='loglevel'), nullable=False),
        sa.Column('source', sa.Enum('SYSTEM', 'IMPORT', 'RULE', 'PACKAGE', 'USER', 'API', 'ROLLBACK', name='logsource'), nullable=False),
        sa.Column('action_type', sa.Enum('CREATE', 'UPDATE', 'DELETE', 'EXECUTE', 'EXPORT', 'IMPORT', 'ROLLBACK', 'VALIDATE', 'LINK', name='workflowactiontype'), nullable=False),
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
        sa.Column('status', sa.Enum('PENDING', 'IN_PROGRESS', 'COMPLETED', 'FAILED', 'ROLLED_BACK', name='workflowstatus'), nullable=False, server_default='COMPLETED'),
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
    op.create_index('ix_workflow_events_correlation_id', 'workflow_events', ['correlation_id'])
    op.create_index('ix_workflow_events_entity', 'workflow_events', ['entity_type', 'entity_id'])
    op.create_index('ix_workflow_events_project_timestamp', 'workflow_events', ['project_id', 'timestamp'])

    op.create_table('asset_versions',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('asset_id', sa.String(), nullable=False),
        sa.Column('version_number', sa.Integer(), nullable=False),
        sa.Column('snapshot', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('created_by', sa.String(), nullable=True),
        sa.Column('change_reason', sa.String(500), nullable=True),
        sa.Column('change_source', sa.Enum('USER', 'RULE', 'IMPORT', 'API', 'ROLLBACK', 'SYSTEM', name='changesource'), nullable=False, server_default='USER'),
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

    op.create_table('property_changes',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('asset_id', sa.String(), nullable=False),
        sa.Column('version_id', sa.String(), nullable=False),
        sa.Column('property_name', sa.String(100), nullable=False),
        sa.Column('property_path', sa.String(500), nullable=True),
        sa.Column('old_value', sa.JSON(), nullable=True),
        sa.Column('new_value', sa.JSON(), nullable=True),
        sa.Column('changed_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('changed_by', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['asset_id'], ['assets.id']),
        sa.ForeignKeyConstraint(['version_id'], ['asset_versions.id']),
        sa.ForeignKeyConstraint(['changed_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_property_changes_asset_id', 'property_changes', ['asset_id'])
    op.create_index('ix_property_changes_version_id', 'property_changes', ['version_id'])
    op.create_index('ix_property_changes_asset_property', 'property_changes', ['asset_id', 'property_name'])

    op.create_table('asset_changes',
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
    # Drop all tables in reverse order
    op.drop_table('asset_changes')
    op.drop_table('property_changes')
    op.drop_table('asset_versions')
    op.drop_table('workflow_events')
    op.drop_table('batch_operations')
    op.drop_table('action_logs')
    op.drop_table('audit_logs')
    op.drop_table('staged_rows')
    op.drop_table('data_sources')
    op.drop_table('cables')
    op.drop_table('cable_sizing_rules')
    op.drop_table('cable_types')
    op.drop_table('rule_executions')
    op.drop_table('rule_definitions')
    op.drop_table('metamodel_edges')
    op.drop_table('metamodel_nodes')
    op.drop_table('connections')
    op.drop_table('assets')
    op.drop_table('packages')
    op.drop_table('lbs_nodes')
    op.drop_table('projects')
    op.drop_table('clients')
    op.drop_table('users')

    # Drop all enums
    op.execute('DROP TYPE IF EXISTS batchoperationtype')
    op.execute('DROP TYPE IF EXISTS changesource')
    op.execute('DROP TYPE IF EXISTS workflowstatus')
    op.execute('DROP TYPE IF EXISTS workflowactiontype')
    op.execute('DROP TYPE IF EXISTS logsource')
    op.execute('DROP TYPE IF EXISTS loglevel')
    op.execute('DROP TYPE IF EXISTS actionstatus')
    op.execute('DROP TYPE IF EXISTS actiontype')
    op.execute('DROP TYPE IF EXISTS detectedtype')
    op.execute('DROP TYPE IF EXISTS ingeststatus')
    op.execute('DROP TYPE IF EXISTS importstatus')
    op.execute('DROP TYPE IF EXISTS disciplinetype')
    op.execute('DROP TYPE IF EXISTS packagestatus')
    op.execute('DROP TYPE IF EXISTS rulevalidationstatus')
    op.execute('DROP TYPE IF EXISTS ruleactiontype')
    op.execute('DROP TYPE IF EXISTS rulesource')
    op.execute('DROP TYPE IF EXISTS assetdatastatus')
    op.execute('DROP TYPE IF EXISTS iotype')
    op.execute('DROP TYPE IF EXISTS locationtype')
    op.execute('DROP TYPE IF EXISTS userrole')
