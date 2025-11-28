/**
 * Type definitions for SYNAPSE Rule Engine
 * 
 * This file provides complete type safety for the rule management system.
 */

// ============================================================================
// ENUMS
// ============================================================================

export enum RuleSource {
    FIRM = 'FIRM',
    COUNTRY = 'COUNTRY',
    PROJECT = 'PROJECT',
    CLIENT = 'CLIENT'
}

export enum RuleActionType {
    CREATE_CHILD = 'CREATE_CHILD',
    SET_PROPERTY = 'SET_PROPERTY',
    CREATE_CABLE = 'CREATE_CABLE',
    CREATE_PACKAGE = 'CREATE_PACKAGE',
    ALLOCATE_IO = 'ALLOCATE_IO',
    VALIDATE = 'VALIDATE'
}

export enum RuleValidationStatus {
    DRAFT = 'DRAFT',
    DEV_VALIDATED = 'DEV_VALIDATED',
    PROD_READY = 'PROD_READY',
    DEPRECATED = 'DEPRECATED'
}

// ============================================================================
// CONDITION TYPES
// ============================================================================

export type ComparisonOperator = '==' | '!=' | '>' | '<' | '>=' | '<=' | 'contains' | 'in';

export interface PropertyFilter {
    key: string;
    op: ComparisonOperator;
    value: string | number | boolean | null;
}

export interface RuleCondition {
    asset_type?: string;
    node_type?: string;  // For matching metamodel nodes (AREA, SITE, etc.)
    property_filters?: PropertyFilter[];
    // Add more condition types as needed
}

// ============================================================================
// ACTION TYPES
// ============================================================================

export interface CreateChildAction {
    type: string;
    naming: string;
    relation: string;
    discipline: string;
    semantic_type: string;
    inherit_properties: string[];
    properties: Record<string, unknown>;
}

export interface SetPropertyAction {
    [key: string]: string | number | boolean | null;
}

export interface CreateCableAction {
    from: string;
    to: string;
    cable_tag: string;
    cable_type: string;
    insulation: string;
    sizing_method: string;
    voltage_drop_limit: number;
}

export interface CreatePackageAction {
    package_type: string;
    naming: string;
    includes: string[];
    excludes: string[];
}

export interface AllocateIOAction {
    cabinet: string;
    card_type: string;
    card_model: string;
    auto_expand: boolean;
}

export interface ValidateAction {
    check: 'has_child' | 'has_property' | 'has_cable';
    child_type?: string;
    property_name?: string;
    error_message: string;
    severity: 'ERROR' | 'WARNING' | 'INFO';
}

export interface RuleAction {
    create_child?: CreateChildAction;
    set_property?: SetPropertyAction;
    create_cable?: CreateCableAction;
    create_package?: CreatePackageAction;
    allocate_io?: AllocateIOAction;
    validate?: ValidateAction;
}

// ============================================================================
// RULE DEFINITION
// ============================================================================

export interface Rule {
    id: string;
    name: string;
    description: string;
    source: RuleSource;
    source_id: string | null;
    priority: number;
    discipline: string;
    category: string;
    action_type: RuleActionType;
    condition: RuleCondition;
    action: RuleAction;
    is_active: boolean;
    is_enforced: boolean;
    overrides_rule_id: string | null;
    conflicts_with: string[];
    execution_count: number;
    success_count: number;
    failure_count: number;
    validation_status?: RuleValidationStatus;
    created_at: string;
    updated_at: string;
}

// ============================================================================
// RULE CREATION (without generated fields)
// ============================================================================

export type RuleCreate = Omit<Rule, 'id' | 'created_at' | 'updated_at' | 'execution_count' | 'success_count' | 'failure_count'>;

export type RuleUpdate = Partial<RuleCreate>;

// ============================================================================
// RULE EXECUTION
// ============================================================================

export interface RuleExecutionResult {
    rule_id: string;
    rule_name: string;
    condition_matched: boolean;
    action_taken: string | null;
    created_entity_id: string | null;
    error_message: string | null;
    timestamp: string;
}

export interface RuleExecutionSummary {
    total_rules: number;
    actions_taken: number;
    execution_time_ms: number;
    details: RuleExecutionResult[];
}

// ============================================================================
// SINGLE RULE EXECUTION
// ============================================================================

export interface SingleRuleExecutionRequest {
    asset_ids?: string[];  // Optional: selective application
}

export interface SingleRuleExecutionResult {
    rule_id: string;
    rule_name: string;
    assets_processed: number;
    actions_taken: number;
    execution_time_ms: number;
    results: Array<{
        asset_id: string;
        asset_tag: string;
        condition_matched: boolean;
        action_taken: string;
        created_entity_id: string | null;
    }>;
}

// ============================================================================
// RULE TEST (with mock data)
// ============================================================================

export interface RuleTestRequest {
    mock_asset: {
        tag: string;
        asset_type: string;
        properties: Record<string, unknown>;
    };
}

export interface RuleTestResult {
    rule_id: string;
    condition_matched: boolean;
    would_create: string | null;
    properties_set: Record<string, unknown> | null;
    explanation: string;
}
