/**
 * Common type definitions used across SYNAPSE
 */

// ============================================================================
// API RESPONSE TYPES
// ============================================================================

export interface ApiError {
    detail: string;
    message?: string;
    errors?: Array<{
        loc: string[];
        msg: string;
        type: string;
    }>;
}

export interface PaginatedResponse<T> {
    items: T[];
    total: number;
    page: number;
    size: number;
    pages: number;
}

// ============================================================================
// COMMON UTILITY TYPES
// ============================================================================

export type Nullable<T> = T | null;

export type Optional<T> = T | undefined;

export type ID = string;

export type Timestamp = string; // ISO 8601 format

// ============================================================================
// REACT COMPONENT TYPES
// ============================================================================

export interface BaseComponentProps {
    className?: string;
    testId?: string;
}

export interface LoadingState {
    isLoading: boolean;
    error: string | null;
}

// ============================================================================
// FORM TYPES
// ============================================================================

export interface FormField<T = string> {
    value: T;
    error: string | null;
    touched: boolean;
}

export type FormState<T> = {
    [K in keyof T]: FormField<T[K]>;
};

// ============================================================================
// TABLE/GRID TYPES
// ============================================================================

export interface SortConfig {
    field: string;
    direction: 'asc' | 'desc';
}

export interface FilterConfig {
    field: string;
    value: unknown;
    operator: 'equals' | 'contains' | 'greaterThan' | 'lessThan';
}

export interface GridColumn<T> {
    field: keyof T;
    headerName: string;
    width?: number;
    sortable?: boolean;
    filterable?: boolean;
    editable?: boolean;
    renderCell?: (value: T[keyof T], row: T) => React.ReactNode;
}

// ============================================================================
// TREE/HIERARCHY TYPES
// ============================================================================

export interface TreeNode<T = unknown> {
    id: string;
    name: string;
    type: string;
    children?: TreeNode<T>[];
    data?: T;
}

// ============================================================================
// PROJECT & AUTH TYPES
// ============================================================================

export interface User {
    id: string;
    email: string;
    full_name: string;
    role: 'ADMIN' | 'ENGINEER' | 'VIEWER' | 'CLIENT';
    is_active: boolean;
    created_at: string;
}

export interface Client {
    id: string;
    name: string;
    description: string | null;
    created_at: string;
}

export interface Project {
    id: string;
    name: string;
    description: string | null;
    client_id: string;
    is_active: boolean;
    created_at: string;
}

// ============================================================================
// AUDIT/ACTION LOG TYPES
// ============================================================================

export enum ActionType {
    CREATE = 'CREATE',
    UPDATE = 'UPDATE',
    DELETE = 'DELETE',
    IMPORT = 'IMPORT',
    EXPORT = 'EXPORT',
    RULE_EXECUTION = 'RULE_EXECUTION'
}

export enum ActionStatus {
    SUCCESS = 'SUCCESS',
    ERROR = 'ERROR',
    WARNING = 'WARNING'
}

export interface ActionLog {
    id: string;
    project_id: string;
    action_type: ActionType;
    entity_type: string;
    entity_id: string | null;
    parent_id: string | null;
    message: string;
    details: Record<string, unknown> | null;
    status: ActionStatus;
    timestamp: string;
}

// ============================================================================
// ASSET TYPES
// ============================================================================

export interface Asset {
    id: string;
    tag: string;
    description?: string;
    type: string;
    area?: string;
    system?: string;
    ioType?: string;
    locationId?: string;
    manufacturerPartId?: string;
    electrical?: {
        voltage?: number;
        powerKW?: number;
        loadType?: string;
    };
    process?: {
        fluid?: string;
        minRange?: number;
        maxRange?: number;
        units?: string;
    };
    purchasing?: {
        workPackageId?: string;
        status?: string;
    };
    properties?: Record<string, unknown>;
}

export interface PhysicalLocation {
    id: string;
    name: string;
    parentId?: string;
}

export interface Cable {
    id: string;
    tag: string;
    type: string;
    properties: {
        from?: string;
        to?: string;
        cable_type?: string;
        conductor_size?: string;
        length?: number;
        voltage_drop_percent?: number;
        sizing_method?: string;
        [key: string]: unknown;
    };
    area?: string;
    system?: string;
}
