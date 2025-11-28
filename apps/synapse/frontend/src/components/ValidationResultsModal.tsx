import React, { useMemo } from 'react';
import { AgGridReact } from 'ag-grid-react';
import { ModuleRegistry } from 'ag-grid-community';
import type { ColDef } from 'ag-grid-community';
import { ClientSideRowModelModule, PaginationModule, RowAutoHeightModule } from 'ag-grid-community';
import { X, AlertTriangle, CheckCircle2, AlertCircle } from 'lucide-react';
import { synapseTheme } from '../theme/ag-grid';
import { useThemeStore } from '../store/useThemeStore';


ModuleRegistry.registerModules([ClientSideRowModelModule, PaginationModule, RowAutoHeightModule]);

interface ValidationResult {
    asset_tag: string;
    rule_name: string;
    status: 'PASS' | 'WARNING' | 'ERROR';
    message: string;
    details?: Record<string, any>;
}

interface ValidationResultsModalProps {
    isOpen: boolean;
    onClose: () => void;
    results: ValidationResult[];
    summary: {
        total: number;
        pass: number;
        warning: number;
        error: number;
    };
}

export const ValidationResultsModal: React.FC<ValidationResultsModalProps> = ({ isOpen, onClose, results, summary }) => {
    const { isDarkMode } = useThemeStore();

    if (!isOpen) return null;

    const columnDefs: ColDef[] = [
        {
            headerName: 'Asset',
            field: 'asset_tag',
            flex: 1,
            filter: 'agTextColumnFilter',
            sortable: true
        },
        {
            headerName: 'Rule',
            field: 'rule_name',
            flex: 2,
            filter: 'agTextColumnFilter',
            sortable: true
        },
        {
            headerName: 'Status',
            field: 'status',
            width: 120,
            filter: 'agTextColumnFilter',
            sortable: true,
            cellStyle: (params) => {
                if (params.value === 'PASS') return { color: '#10b981', fontWeight: '600' };
                if (params.value === 'WARNING') return { color: '#f59e0b', fontWeight: '600' };
                if (params.value === 'ERROR') return { color: '#ef4444', fontWeight: '600' };
                return {};
            }
        },
        {
            headerName: 'Message',
            field: 'message',
            flex: 3,
            filter: 'agTextColumnFilter',
            wrapText: true,
            autoHeight: true
        }
    ];

    const defaultColDef: ColDef = {
        resizable: true,
        sortable: true,
        filter: true
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
            <div className="bg-white dark:bg-slate-900 rounded-lg shadow-xl w-[90vw] h-[80vh] flex flex-col">
                {/* Header */}
                <div className="border-b border-gray-200 dark:border-slate-800 p-6">
                    <div className="flex items-center justify-between">
                        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                            Validation Results
                        </h2>
                        <button
                            onClick={onClose}
                            className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
                        >
                            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                            </svg>
                        </button>
                    </div>

                    {/* Summary Stats */}
                    <div className="mt-4 grid grid-cols-4 gap-4">
                        <div className="bg-gray-50 dark:bg-slate-950 p-3 rounded border border-gray-200 dark:border-slate-800">
                            <div className="text-sm text-gray-500 dark:text-gray-400">Total</div>
                            <div className="text-2xl font-bold text-gray-900 dark:text-white">{summary.total}</div>
                        </div>
                        <div className="bg-green-50 dark:bg-green-900/20 p-3 rounded border border-green-100 dark:border-green-900/30">
                            <div className="text-sm text-green-700 dark:text-green-400">Pass</div>
                            <div className="text-2xl font-bold text-green-600 dark:text-green-500">{summary.pass}</div>
                        </div>
                        <div className="bg-yellow-50 dark:bg-yellow-900/20 p-3 rounded border border-yellow-100 dark:border-yellow-900/30">
                            <div className="text-sm text-yellow-700 dark:text-yellow-400">Warning</div>
                            <div className="text-2xl font-bold text-yellow-600 dark:text-yellow-500">{summary.warning}</div>
                        </div>
                        <div className="bg-red-50 dark:bg-red-900/20 p-3 rounded border border-red-100 dark:border-red-900/30">
                            <div className="text-sm text-red-700 dark:text-red-400">Error</div>
                            <div className="text-2xl font-bold text-red-600 dark:text-red-500">{summary.error}</div>
                        </div>
                    </div>
                </div>

                {/* AG Grid */}
                <div className="flex-1 p-6 bg-slate-900">
                    <div className="h-full" data-ag-theme-mode={isDarkMode ? 'dark' : 'light'}>
                        <AgGridReact
                            theme={synapseTheme}
                            rowData={results}
                            columnDefs={columnDefs}
                            defaultColDef={defaultColDef}
                            pagination={true}
                            paginationPageSize={50}
                            suppressCellFocus={true}
                            rowSelection="multiple"
                            animateRows={true}
                        />
                    </div>
                </div>

                {/* Footer */}
                <div className="border-t border-gray-200 dark:border-gray-700 p-4 flex justify-end gap-2">
                    <button
                        onClick={onClose}
                        className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-200 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded hover:bg-gray-50 dark:hover:bg-gray-600"
                    >
                        Close
                    </button>
                </div>
            </div>
        </div>
    );
};

export default ValidationResultsModal;
