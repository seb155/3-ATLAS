/**
 * CSV Import Types
 * Types for the CSV import functionality
 */

export interface ImportSummary {
  success: boolean;
  total_rows: number;
  created: number;
  updated: number;
  failed: number;
  rules_executed?: number;
  child_assets_created?: number;
  rule_execution_time_ms?: number;
}

export interface ImportError {
  row: number;
  tag: string;
  error: string;
}

export interface ImportResponse {
  success: boolean;
  total_rows: number;
  created: number;
  updated: number;
  failed: number;
  errors?: ImportError[];
  rules_executed?: number;
  child_assets_created?: number;
  rule_execution_time_ms?: number;
}
