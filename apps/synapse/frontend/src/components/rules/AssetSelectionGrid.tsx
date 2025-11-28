
import React, { useState, useEffect } from 'react';
import { AgGridReact } from 'ag-grid-react';
import axios from 'axios';
import { API_URL } from '../../../config';
import { useAuthStore } from '../../store/useAuthStore';
import { Loader2 } from 'lucide-react';
import { Asset } from '../../types';
import { synapseTheme } from '../../theme/ag-grid';
import { useThemeStore } from '../../store/useThemeStore';


interface AssetSelectionGridProps {
    projectId: string | undefined;
    onSelectionChange: (assets: Asset[]) => void;
}

export const AssetSelectionGrid: React.FC<AssetSelectionGridProps> = ({
    projectId,
    onSelectionChange
}) => {
    const [assets, setAssets] = useState<Asset[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const { token } = useAuthStore();
    const { isDarkMode } = useThemeStore();

    useEffect(() => {
        if (projectId) {
            fetchAssets();
        }
    }, [projectId]);

    const fetchAssets = async () => {
        if (!projectId) return;

        setIsLoading(true);
        try {
            const response = await axios.get(
                `${API_URL} /api/metamodel / nodes`,
                {
                    headers: { 'Authorization': `Bearer ${token} ` },
                    params: { project_id: projectId }
                }
            );
            setAssets(response.data.nodes || []);
        } catch (error) {
            console.error('Failed to fetch assets:', error);
            setAssets([]);
        } finally {
            setIsLoading(false);
        }
    };

    const columnDefs = [
        {
            headerName: '',
            field: 'id' as keyof Asset,
            checkboxSelection: true,
            headerCheckboxSelection: true,
            width: 50,
            pinned: 'left' as const
        },
        {
            headerName: 'Tag',
            field: 'name' as keyof Asset,
            flex: 1,
            minWidth: 150
        },
        {
            headerName: 'Type',
            field: 'type' as keyof Asset,
            width: 120
        },
        {
            headerName: 'Discipline',
            field: 'discipline' as keyof Asset,
            width: 120
        },
        {
            headerName: 'Semantic Type',
            field: 'semantic_type' as keyof Asset,
            width: 130
        }
    ];

    if (isLoading) {
        return (
            <div className="h-[500px] flex items-center justify-center">
                <div className="flex items-center gap-2 text-slate-400">
                    <Loader2 className="w-5 h-5 animate-spin" />
                    <span>Loading assets...</span>
                </div>
            </div>
        );
    }

    if (!projectId) {
        return (
            <div className="h-[500px] flex items-center justify-center text-slate-500">
                Select a project to view assets
            </div>
        );
    }

    // Import moved to top level
    // ... (imports)

    // ... (inside component)
    return (
        <div className="h-[500px]" data-ag-theme-mode={isDarkMode ? 'dark' : 'light'}>
            <AgGridReact
                theme={synapseTheme}
                rowData={assets}
                columnDefs={columnDefs}
                rowSelection={{ mode: 'multiRow' }}
                suppressRowClickSelection={true}
                onSelectionChanged={(event) => {
                    const selected = event.api.getSelectedRows();
                    onSelectionChange(selected);
                }}
                defaultColDef={{
                    sortable: true,
                    filter: true,
                    resizable: true
                }}
                pagination={true}
                paginationPageSize={20}
            />
        </div>
    );
}
