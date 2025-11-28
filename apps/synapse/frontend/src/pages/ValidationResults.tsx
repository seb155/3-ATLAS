import React, { useState } from 'react';
import { AgGridReact } from 'ag-grid-react';
import type { ColDef } from 'ag-grid-community';
import { ClientSideRowModelModule, PaginationModule, RowAutoHeightModule } from 'ag-grid-community';
import { Play, Loader2, CheckCircle2, AlertTriangle, XCircle, RefreshCcw } from 'lucide-react';
import { synapseTheme } from '../theme/ag-grid';
import { useThemeStore } from '../store/useThemeStore';
import { useProjectStore } from '../store/useProjectStore';
import { useAuthStore } from '../store/useAuthStore';
import axios from 'axios';
import { API_URL } from '../config';

interface ValidationResult {
    asset_id: string;
    rule_id: string;
    rule_name: string;
    status: 'pass' | 'warning' | 'error';
    message: string;
}

interface ValidationSummary {
    total: number;
    pass: number;
    warning: number;
    error: number;
}

export const ValidationResults = () => {
    const { isDarkMode } = useThemeStore();
    const { currentProject } = useProjectStore();
    const { token } = useAuthStore();

    const [results, setResults] = useState<ValidationResult[]>([]);
    const [summary, setSummary] = useState<ValidationSummary>({ total: 0, pass: 0, warning: 0, error: 0 });
    const [loading, setLoading] = useState(false);

    const runValidation = async () => {
        if (!token || !currentProject) return;

        setLoading(true);
        try {
            const response = await axios.post(
                `${API_URL}/api/v1/projects/${currentProject.id}/validate`,
                {},
                {
                    headers: {
                        Authorization: `Bearer ${token}`,
                        'X-Project-ID': currentProject.id
                    }
                }
            );

            const results = response.data.results || [];
            setResults(results);

            // Calculate summary
            const summary = {
                total: results.length,
                pass: results.filter((r: ValidationResult) => r.status === 'pass').length,
                warning: results.filter((r: ValidationResult) => r.status === 'warning').length,
                error: results.filter((r: ValidationResult) => r.status === 'error').length
            };
            setSummary(summary);
        } catch (error) {
            console.error('Validation failed:', error);
        } finally {
            setLoading(false);
        }
    };

    const columnDefs: ColDef[] = [
        {
            headerName: 'Asset',
            field: 'asset_id',
            filter: true,
            flex: 1
        },
        {
            headerName: 'Rule',
            field: 'rule_name',
            filter: true,
            flex: 1.5
        },
        {
            headerName: 'Status',
            field: 'status',
            filter: true,
            width: 120,
            cellRenderer: (params: any) => {
                const status = params.value;
                const icons = {
                    pass: <CheckCircle2 size={16} className="text-green-400" />,
                    warning: <AlertTriangle size={16} className="text-yellow-400" />,
                    error: <XCircle size={16} className="text-red-400" />
                };
                const colors = {
                    pass: 'text-green-400',
                    warning: 'text-yellow-400',
                    error: 'text-red-400'
                };
                return (
                    <div className="flex items-center gap-2">
                        {icons[status as keyof typeof icons]}
                        <span className={`font-medium uppercase text-xs ${colors[status as keyof typeof colors]}`}>
                            {status}
                        </span>
                    </div>
                );
            }
        },
        {
            headerName: 'Message',
            field: 'message',
            filter: true,
            flex: 2,
            wrapText: true,
            autoHeight: true
        }
    ];

    const defaultColDef = {
        resizable: true,
        sortable: true
    };

    return (
        <div className="h-full flex flex-col bg-slate-950 p-6 space-y-6">
            {/* Header */}
            <div className="flex justify-between items-start">
                <div>
                    <h1 className="text-3xl font-bold text-white">Validation Results</h1>
                    <p className="text-slate-400 mt-2">
                        Data quality checks and rule validation for {currentProject?.name}
                    </p>
                </div>
                <button
                    onClick={runValidation}
                    disabled={loading}
                    className="flex items-center gap-2 px-4 py-2 bg-teal-600 hover:bg-teal-700 text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                    {loading ? (
                        <>
                            <Loader2 size={18} className="animate-spin" />
                            Running...
                        </>
                    ) : (
                        <>
                            <Play size={18} />
                            Run Validation
                        </>
                    )}
                </button>
            </div>

            {/* Summary Cards */}
            {results.length > 0 && (
                <div className="grid grid-cols-4 gap-4">
                    <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-4">
                        <div className="text-sm text-slate-400 mb-1">Total</div>
                        <div className="text-3xl font-bold text-white">{summary.total}</div>
                    </div>
                    <div className="bg-green-500/10 border border-green-500/20 rounded-xl p-4">
                        <div className="flex items-center text-sm text-green-400 mb-1">
                            <CheckCircle2 size={16} className="mr-1" />
                            Pass
                        </div>
                        <div className="text-3xl font-bold text-green-400">{summary.pass}</div>
                    </div>
                    <div className="bg-yellow-500/10 border border-yellow-500/20 rounded-xl p-4">
                        <div className="flex items-center text-sm text-yellow-400 mb-1">
                            <AlertTriangle size={16} className="mr-1" />
                            Warning
                        </div>
                        <div className="text-3xl font-bold text-yellow-400">{summary.warning}</div>
                    </div>
                    <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-4">
                        <div className="flex items-center text-sm text-red-400 mb-1">
                            <XCircle size={16} className="mr-1" />
                            Error
                        </div>
                        <div className="text-3xl font-bold text-red-400">{summary.error}</div>
                    </div>
                </div>
            )}

            {/* Results Grid */}
            <div className="flex-1 bg-slate-900 rounded-xl border border-slate-800 overflow-hidden">
                {results.length === 0 ? (
                    <div className="h-full flex flex-col items-center justify-center text-slate-400">
                        <CheckCircle2 size={48} className="mb-4 text-slate-600" />
                        <h3 className="text-lg font-medium text-slate-300">No validation results yet</h3>
                        <p className="text-sm mt-2">Click "Run Validation" to check your project data</p>
                    </div>
                ) : (
                    <div className="h-full" data-ag-theme-mode={isDarkMode ? 'dark' : 'light'}>
                        <AgGridReact
                            theme={synapseTheme}
                            rowData={results}
                            columnDefs={columnDefs}
                            defaultColDef={defaultColDef}
                            pagination={true}
                            paginationPageSize={50}
                            domLayout="normal"
                        />
                    </div>
                )}
            </div>
        </div>
    );
};

export default ValidationResults;
