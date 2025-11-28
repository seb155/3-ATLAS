import React, { useState, useEffect, useMemo } from 'react';
import axios from 'axios';
import { AgGridReact } from 'ag-grid-react';
import { AllCommunityModule, ModuleRegistry, themeQuartz } from 'ag-grid-community';
import { API_URL } from '../config';
import { RawDataRow } from '../types/ingestion';
import { synapseTheme } from '../theme/ag-grid';
import { useThemeStore } from '../store/useThemeStore';

// Register AG Grid modules
ModuleRegistry.registerModules([AllCommunityModule]);

interface RawDataGridProps {
    sourceId: string;
}

// Custom theme removed in favor of global CSS class

export const RawDataGrid: React.FC<RawDataGridProps> = ({ sourceId }) => {
    const [rows, setRows] = useState<RawDataRow[]>([]);
    const [loading, setLoading] = useState(false);
    const { isDarkMode } = useThemeStore();

    useEffect(() => {
        fetchRows();
    }, [sourceId]);

    const fetchRows = async () => {
        setLoading(true);
        try {
            const response = await axios.get(`${API_URL}/api/v1/ingest/sources/${sourceId}/rows`);
            setRows(response.data);
        } catch (error) {
            console.error('Error fetching rows:', error);
        } finally {
            setLoading(false);
        }
    };

    const columnDefs = useMemo(() => {
        if (rows.length === 0) return [];

        const firstRow = rows[0].raw_data;
        return Object.keys(firstRow).map(key => ({
            field: key,
            headerName: key,
            sortable: true,
            filter: true,
            resizable: true,
            flex: 1,
            minWidth: 150
        }));
    }, [rows]);

    const rowData = useMemo(() => {
        return rows.map(row => row.raw_data);
    }, [rows]);

    if (loading) {
        return (
            <div className="p-6 text-center text-slate-400">
                <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-mining-teal"></div>
                <p className="mt-2">Loading rows...</p>
            </div>
        );
    }

    if (rows.length === 0) {
        return (
            <div className="p-6 text-center text-slate-500">
                No rows found for this data source.
            </div>
        );
    }

    return (
        <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
            <div className="p-4 border-b border-slate-800 flex items-center justify-between">
                <h2 className="font-semibold text-white">Raw Data Inspector</h2>
                <span className="text-xs text-slate-400">Showing first {rows.length} rows</span>
            </div>
            <div style={{ height: '1200px', width: '100%' }} data-ag-theme-mode={isDarkMode ? 'dark' : 'light'}>
                <AgGridReact
                    theme={synapseTheme}
                    columnDefs={columnDefs}
                    rowData={rowData}
                    defaultColDef={{
                        sortable: true,
                        filter: true,
                        resizable: true
                    }}
                    pagination={true}
                    paginationPageSize={50}
                />
            </div>
        </div>
    );
};
