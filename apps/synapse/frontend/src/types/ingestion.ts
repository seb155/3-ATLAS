/**
 * Type definitions for SYNAPSE Data Ingestion
 * 
 * This file provides complete type safety for CSV import and raw data handling.
 */

// ============================================================================
// INGESTION SOURCE
// ============================================================================

export enum IngestionStatus {
    PENDING = 'PENDING',
    PROCESSING = 'PROCESSING',
    COMPLETED = 'COMPLETED',
    ERROR = 'ERROR'
}

export interface IngestionSource {
    id: string;
    filename: string;
    file_size_bytes: number;
    uploaded_at: string;
    row_count: number;
    status: IngestionStatus;
    error_message: string | null;
    project_id: string;
    uploaded_by_user_id: string;
}

// ============================================================================
// RAW DATA ROW
// ============================================================================

export interface RawDataRow {
    id: string;
    source_id: string;
    row_number: number;
    raw_data: Record<string, string | number | boolean | null>;
    created_at: string;
}

// ============================================================================
// COLUMN MAPPING
// ============================================================================

export interface ColumnMapping {
    source_column: string;
    target_field: string;
    transform?: 'uppercase' | 'lowercase' | 'trim' | 'none';
}

// ============================================================================
// IMPORT CONFIGURATION
// ============================================================================

export interface ImportConfig {
    source_id: string;
    column_mappings: ColumnMapping[];
    skip_rows: number;
    auto_execute_rules: boolean;
    validation_rules?: string[];  // Rule IDs to validate against
}

// ============================================================================
// IMPORT RESULT
// ============================================================================

export interface ImportResult {
    total_rows_processed: number;
    assets_created: number;
    assets_updated: number;
    errors: Array<{
        row_number: number;
        error_message: string;
    }>;
    execution_time_ms: number;
    rule_execution_summary?: {
        rules_executed: number;
        actions_taken: number;
    };
}

// ============================================================================
// EXPORT TYPES
// ============================================================================

export enum ExportFormat {
    CSV = 'CSV',
    EXCEL = 'EXCEL',
    JSON = 'JSON'
}

export interface ExportConfig {
    format: ExportFormat;
    include_fields: string[];
    filter?: {
        asset_types?: string[];
        areas?: string[];
    };
}
