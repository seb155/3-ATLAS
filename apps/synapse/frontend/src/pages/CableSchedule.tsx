import React, { useMemo, useState, useEffect } from 'react';
import { AgGridReact } from 'ag-grid-react';
import { ColDef } from 'ag-grid-community';

import { FileDown, RefreshCw } from 'lucide-react';
import { synapseTheme } from '../theme/ag-grid';
import { useThemeStore } from '../store/useThemeStore';
import axios from 'axios';
import { useAuthStore } from '../store/useAuthStore';
import { useProjectStore } from '../store/useProjectStore';
import { useAppStore } from '../store/useAppStore'; // Assuming this is needed for `cables` and `refreshCables`
import { API_URL } from '@/config';

export const CableSchedule = () => {
    const { token } = useAuthStore();
    const { currentProject } = useProjectStore();
    const { cables, refreshCables } = useAppStore();
    const { isDarkMode } = useThemeStore();
    const [loading, setLoading] = useState(false);

    // Use store refresh instead of local fetch
    const handleRefresh = async () => {
        if (!token || !currentProject) return;
        setLoading(true);
        await refreshCables();
        setLoading(false);
    };

    useEffect(() => {
        handleRefresh();
    }, [currentProject, token]);

    // Define Columns
    const columnDefs = useMemo<ColDef[]>(() => [
        { field: 'tag', headerName: 'Cable Tag', sortable: true, filter: true, pinned: 'left', width: 180 },
        {
            headerName: 'From',
            field: 'properties.from',
            valueGetter: (params) => params.data.properties?.from || 'MCC (TBD)',
            sortable: true,
            filter: true
        },
        {
            headerName: 'To',
            field: 'properties.to',
            valueGetter: (params) => {
                // In future, resolve edge. For now, infer from tag or properties
                // Cable tag is usually {asset_tag}-CBL
                const tag = params.data.tag;
                if (tag.includes('-CBL')) return tag.replace('-CBL', '');
                return params.data.properties?.to || 'Unknown';
            },
            sortable: true,
            filter: true
        },
        { field: 'properties.cable_type', headerName: 'Type', sortable: true, filter: true },
        { field: 'properties.conductor_size', headerName: 'Size', sortable: true, filter: true },
        { field: 'properties.length', headerName: 'Length (m)', sortable: true, filter: true, type: 'numericColumn' },
        {
            field: 'properties.voltage_drop_percent',
            headerName: 'VD %',
            sortable: true,
            filter: true,
            cellStyle: (params) => {
                if (params.value > 3.0) return { color: '#ef4444', fontWeight: 'bold' }; // Red if > 3%
                return { color: '#10b981' }; // Green otherwise
            }
        },
        { field: 'properties.sizing_method', headerName: 'Sizing', sortable: true, filter: true },
        { field: 'area', headerName: 'Area', sortable: true, filter: true },
        { field: 'system', headerName: 'System', sortable: true, filter: true },
    ], []);

    const defaultColDef = useMemo(() => ({
        resizable: true,
        sortable: true,
        filter: true,
    }), []);

    return (
        <div className="h-full flex flex-col bg-slate-950 p-6 space-y-4">
            {/* Header */}
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-2xl font-bold text-white tracking-tight">Cable Schedule</h1>
                    <p className="text-slate-400 mt-1">
                        {cables.length} cables generated • CEC Standards Applied
                    </p>
                </div>
                <div className="flex gap-3">
                    <button
                        onClick={handleRefresh}
                        className="flex items-center px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg transition-colors border border-slate-700"
                        disabled={loading}
                    >
                        <RefreshCw size={16} className={`mr-2 ${loading ? 'animate-spin' : ''}`} />
                        Refresh
                    </button>
                    <button className="flex items-center px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg font-medium transition-colors shadow-lg shadow-emerald-900/20">
                        <FileDown size={16} className="mr-2" />
                        Export Schedule
                    </button>
                </div>
            </div>


            {/* Grid */}
            <div className="flex-1 bg-slate-900 rounded-xl border border-slate-800 overflow-hidden shadow-xl">
                <div className="h-full w-full" data-ag-theme-mode={isDarkMode ? 'dark' : 'light'}>
                    <AgGridReact
                        theme={synapseTheme}
                        rowData={cables}
                        columnDefs={columnDefs}
                        defaultColDef={defaultColDef}
                        animateRows={true}
                        rowSelection={{ mode: 'multiRow' }}
                    />
                </div>
            </div>
        </div>
    );
};

export default CableSchedule;
