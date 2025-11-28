import React, { useMemo, useCallback, useState, useRef, useEffect } from 'react';
import { AgGridReact } from 'ag-grid-react';
import { ColDef, ModuleRegistry, RowClickedEvent, CellValueChangedEvent } from 'ag-grid-community';
import {
    ClientSideRowModelModule,
    RowSelectionModule,
    TextFilterModule,
    NumberFilterModule,
    DateFilterModule,
    TextEditorModule,
    SelectEditorModule,
    CellStyleModule,
    ValidationModule
} from 'ag-grid-community';
import { synapseTheme } from '../../theme/ag-grid';
import { useThemeStore } from '../../store/useThemeStore';
import axios from 'axios';
import { API_URL } from '@/config';
import { useAuthStore } from '../../store/useAuthStore';
import { useProjectStore } from '../../store/useProjectStore';
import { Asset, PhysicalLocation } from '../../../types';
import { logger } from '../../services/logger';
import { Filter, Columns3, Download, Upload, Save, Loader2 } from 'lucide-react';
import { RightSidebar } from '../RightSidebar';
import { ColumnManager } from '../ColumnManager';
import { FilterPresets } from '../FilterPresets';
import { ClickableTag } from '../ui/ClickableTag';

// Register AG Grid modules
ModuleRegistry.registerModules([
    ClientSideRowModelModule,
    RowSelectionModule,
    TextFilterModule,
    NumberFilterModule,
    DateFilterModule,
    TextEditorModule,
    SelectEditorModule,
    CellStyleModule,
    ValidationModule
]);

interface AssetGridProps {
    instruments: Asset[];
    locations: PhysicalLocation[];
    onUpdateInstruments: (insts: Asset[]) => void;
    onAssetSelect?: (asset: Asset | null) => void;
}

export const AssetGrid: React.FC<AssetGridProps> = ({ instruments, locations, onUpdateInstruments, onAssetSelect }) => {
    const [searchFilter, setSearchFilter] = useState('');
    const [changedAssets, setChangedAssets] = useState<Record<string, Asset>>({});
    const [isSaving, setIsSaving] = useState(false);
    const [gridApi, setGridApi] = useState<any>(null);
    const gridRef = useRef<AgGridReact>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);
    const filterInputRef = useRef<HTMLInputElement>(null);

    // Ctrl+F to focus filter
    useEffect(() => {
        const handleKeyDown = (e: KeyboardEvent) => {
            if ((e.ctrlKey || e.metaKey) && e.key === 'f') {
                e.preventDefault();
                filterInputRef.current?.focus();
            }
        };

        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, []);

    const onGridReady = useCallback((params: any) => {
        setGridApi(params.api);
    }, []);

    const { currentProject } = useProjectStore();
    const { token } = useAuthStore();
    const { isDarkMode } = useThemeStore();

    const locationMap = useMemo(() => {
        const map: Record<string, string> = {};
        locations.forEach(l => map[l.id] = l.name);
        return map;
    }, [locations]);

    // Filter instruments based on search
    const filteredInstruments = useMemo(() => {
        if (!searchFilter.trim()) return instruments;
        const query = searchFilter.toLowerCase();
        return instruments.filter(i =>
            i.tag.toLowerCase().includes(query) ||
            i.description?.toLowerCase().includes(query) ||
            i.type?.toLowerCase().includes(query) ||
            i.area?.toLowerCase().includes(query) ||
            i.system?.toLowerCase().includes(query)
        );
    }, [instruments, searchFilter]);

    const columnDefs = useMemo<ColDef[]>(() => [
        // Core Identity
        // Core Identity
        {
            field: 'tag',
            headerName: 'Tag',
            pinned: 'left',
            width: 160,
            sortable: true,
            filter: true,
            cellRenderer: (params: any) => {
                if (!params.value) return null;
                return (
                    <span
                        className="font-mono font-medium text-mining-teal hover:underline cursor-pointer"
                        onClick={(e) => {
                            e.stopPropagation(); // Prevent row selection
                            if (onAssetSelect) onAssetSelect(params.data);
                        }}
                    >
                        {params.value}
                    </span>
                );
            }
        },
        { field: 'description', headerName: 'Description', width: 250, editable: true, filter: true, sortable: true },
        { field: 'type', headerName: 'Type', width: 120, filter: true, sortable: true },
        { field: 'ioType', headerName: 'IO Type', width: 110, filter: true, sortable: true },
        {
            field: 'area',
            headerName: 'Area',
            width: 100,
            filter: true,
            sortable: true,
            cellRenderer: (params: any) => {
                if (!params.value) return null;
                return (
                    <span
                        className="text-slate-300 hover:text-white hover:underline cursor-pointer"
                        onClick={(e) => {
                            e.preventDefault();
                            e.stopPropagation();
                            e.nativeEvent.stopImmediatePropagation(); // Force stop
                            setSearchFilter(params.value);
                        }}
                        title={`Filter by Area: ${params.value}`}
                    >
                        {params.value}
                    </span>
                );
            }
        },
        {
            field: 'system',
            headerName: 'System',
            width: 120,
            filter: true,
            sortable: true,
            cellRenderer: (params: any) => {
                if (!params.value) return null;
                return (
                    <span
                        className="text-slate-300 hover:text-white hover:underline cursor-pointer"
                        onClick={(e) => {
                            e.preventDefault();
                            e.stopPropagation();
                            e.nativeEvent.stopImmediatePropagation(); // Force stop
                            setSearchFilter(params.value);
                        }}
                        title={`Filter by System: ${params.value}`}
                    >
                        {params.value}
                    </span>
                );
            }
        },

        // Location
        {
            field: 'locationId',
            headerName: 'Location',
            width: 180,
            filter: true,
            sortable: true,
            valueFormatter: (params) => locationMap[params.value] || params.value || '-',
            editable: true,
            cellEditor: 'agSelectCellEditor',
            cellEditorParams: {
                values: ['', ...locations.map(l => l.id)],
                formatValue: (value: string) => locationMap[value] || value || '(None)'
            }
        },

        // Electrical Specs
        {
            headerName: 'Electrical',
            children: [
                { field: 'electrical.voltage', headerName: 'Voltage', width: 100, editable: true, filter: 'agNumberColumnFilter', sortable: true },
                { field: 'electrical.powerKW', headerName: 'Power (kW)', width: 110, editable: true, type: 'numericColumn', filter: 'agNumberColumnFilter', sortable: true },
                { field: 'electrical.loadType', headerName: 'Load Type', width: 120, editable: true, filter: 'agTextColumnFilter', sortable: true }
            ]
        },

        // Process Specs
        {
            headerName: 'Process',
            children: [
                { field: 'process.fluid', headerName: 'Fluid', width: 120, editable: true, filter: 'agTextColumnFilter', sortable: true },
                { field: 'process.minRange', headerName: 'Min', width: 90, editable: true, filter: 'agNumberColumnFilter', sortable: true },
                { field: 'process.maxRange', headerName: 'Max', width: 90, editable: true, filter: 'agNumberColumnFilter', sortable: true },
                { field: 'process.units', headerName: 'Units', width: 80, editable: true, filter: 'agTextColumnFilter', sortable: true }
            ]
        },

        // Purchasing
        {
            headerName: 'Procurement',
            children: [
                { field: 'manufacturerPartId', headerName: 'Part #', width: 160, editable: true, filter: true, sortable: true },
                { field: 'purchasing.workPackageId', headerName: 'Package', width: 140, editable: true, filter: true, sortable: true },
                { field: 'purchasing.status', headerName: 'Status', width: 120, editable: true, filter: true, sortable: true }
            ]
        }
    ], [locationMap, locations]);

    const defaultColDef = useMemo(() => ({
        resizable: true,
        sortable: true,
        filter: true
    }), []);

    const onCellValueChanged = useCallback((params: CellValueChangedEvent) => {
        const updatedAsset = params.data;

        // Update local state for immediate feedback
        const newInstruments = instruments.map(inst =>
            inst.id === updatedAsset.id ? updatedAsset : inst
        );
        onUpdateInstruments(newInstruments);

        // Track changes for bulk save
        setChangedAssets(prev => ({
            ...prev,
            [updatedAsset.id]: updatedAsset
        }));
    }, [instruments, onUpdateInstruments]);

    const onRowClicked = useCallback((event: RowClickedEvent) => {
        // We disable default row click navigation to allow specific column interactions
        // Navigation is now handled exclusively by onCellClicked for the 'tag' column
    }, []);

    const onCellClicked = useCallback((event: any) => {
        // Only navigate if the clicked column is explicitly the 'tag' column
        if (event.column?.getColId() === 'tag') {
            if (onAssetSelect && event.data) {
                onAssetSelect(event.data as Asset);
            }
        }
    }, [onAssetSelect]);

    const handleSave = async () => {
        if (Object.keys(changedAssets).length === 0) return;
        setIsSaving(true);
        try {
            const updates = Object.values(changedAssets).map((asset: Asset) => ({
                id: asset.id,
                tag: asset.tag,
                description: asset.description,
                type: asset.type,
                area: asset.area,
                system: asset.system,
                ioType: asset.ioType,
                electrical: asset.electrical,
                process: asset.process,
                purchasing: asset.purchasing,
                manufacturerPartId: asset.manufacturerPartId,
                locationId: asset.locationId
            }));

            const response = await axios.patch(`${API_URL}/api/v1/assets/bulk`, updates, {
                headers: {
                    'X-Project-ID': currentProject?.id,
                    'Authorization': `Bearer ${token}`
                }
            });

            if (response.status === 200) {
                setChangedAssets({});
                logger.success('Changes saved successfully');
            }
        } catch (error) {
            logger.error("Failed to save bulk updates", error);
        } finally {
            setIsSaving(false);
        }
    };

    const handleExport = async () => {
        try {
            const response = await axios.get(`${API_URL}/api/v1/import_export/export`, {
                headers: {
                    'X-Project-ID': currentProject?.id,
                    'Authorization': `Bearer ${token}`
                },
                responseType: 'blob',
            });

            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `assets_export_${currentProject?.name || currentProject?.id}.csv`);
            document.body.appendChild(link);
            link.click();
            link.remove();
            logger.success('Export completed');
        } catch (error) {
            logger.error("Export failed", error);
        }
    };

    const handleImportClick = () => {
        fileInputRef.current?.click();
    };

    const handleFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0];
        if (!file) return;

        const formData = new FormData();
        formData.append('file', file);

        try {
            setIsSaving(true);
            const response = await axios.post(`${API_URL}/api/v1/import_export/import`, formData, {
                headers: {
                    'X-Project-ID': currentProject?.id,
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'multipart/form-data'
                }
            });

            const summary = response.data;
            logger.success(`Import Complete: Created: ${summary.created}, Updated: ${summary.updated}, Errors: ${summary.errors.length}`);

            if (summary.errors.length > 0) {
                logger.warn("Import Errors:", summary.errors);
            }

            window.location.reload();
        } catch (error) {
            logger.error("Import failed", error);
        } finally {
            setIsSaving(false);
            if (fileInputRef.current) {
                fileInputRef.current.value = '';
            }
        }
    };

    return (
        <div className="h-full w-full flex flex-col">
            <input
                type="file"
                ref={fileInputRef}
                onChange={handleFileChange}
                className="hidden"
                accept=".csv"
            />

            {/* Enhanced Toolbar */}
            <div className="h-12 bg-slate-900 border-b border-slate-800 flex items-center px-6 gap-4">
                {/* Quick Filter */}
                <div className="relative flex-1 max-w-xs">
                    <Filter size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
                    <input
                        ref={filterInputRef}
                        type="text"
                        placeholder="Quick filter..."
                        value={searchFilter}
                        onChange={(e) => setSearchFilter(e.target.value)}
                        className="w-full bg-slate-800 border border-slate-700 rounded-lg pl-9 pr-3 py-1.5 text-sm text-slate-300 focus:ring-1 focus:ring-mining-teal focus:border-mining-teal outline-none transition-colors"
                    />
                </div>

                <span className="text-xs text-slate-500">
                    {filteredInstruments.length} / {instruments.length} records
                </span>

                <div className="flex-1" />

                {/* Status */}
                <span className="text-xs text-slate-500">
                    {Object.keys(changedAssets).length > 0 ? (
                        <span className="text-mining-gold">{Object.keys(changedAssets).length} unsaved</span>
                    ) : (
                        'All saved'
                    )}
                </span>

                {/* Actions */}
                <button
                    onClick={() => gridRef.current?.api?.sizeColumnsToFit()}
                    className="p-2 text-slate-400 hover:text-white hover:bg-slate-800 rounded transition-colors"
                    title="Auto-fit columns"
                >
                    <Columns3 size={16} />
                </button>

                <button
                    onClick={handleImportClick}
                    className="flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium bg-slate-800 text-slate-300 hover:bg-slate-700 transition-colors"
                >
                    <Upload size={14} />
                    Import
                </button>

                <button
                    onClick={handleExport}
                    className="flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium bg-slate-800 text-slate-300 hover:bg-slate-700 transition-colors"
                >
                    <Download size={14} />
                    Export
                </button>

                <button
                    onClick={handleSave}
                    disabled={Object.keys(changedAssets).length === 0 || isSaving}
                    className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${Object.keys(changedAssets).length > 0
                        ? 'bg-mining-teal text-slate-950 hover:bg-mining-teal/90'
                        : 'bg-slate-800 text-slate-500 cursor-not-allowed'
                        }`}
                >
                    {isSaving ? <Loader2 size={14} className="animate-spin" /> : <Save size={14} />}
                    {isSaving ? 'Saving...' : 'Save'}
                </button>
            </div>

            {/* Grid & Sidebar Container */}
            <div className="flex-1 flex overflow-hidden">
                {/* Grid */}
                <div className="flex-1 flex flex-col relative" data-ag-theme-mode={isDarkMode ? 'dark' : 'light'}>
                    {isSaving && (
                        <div className="absolute inset-0 bg-slate-950/80 flex items-center justify-center z-50 backdrop-blur-sm transition-all duration-200">
                            <div className="bg-slate-900 border border-slate-700 rounded-lg p-6 flex items-center gap-3 shadow-xl">
                                <Loader2 size={24} className="animate-spin text-mining-teal" />
                                <span className="text-white font-medium">Saving changes...</span>
                            </div>
                        </div>
                    )}
                    <AgGridReact
                        theme={synapseTheme}
                        ref={gridRef}
                        rowData={filteredInstruments}
                        columnDefs={columnDefs}
                        defaultColDef={defaultColDef}
                        onCellValueChanged={onCellValueChanged}
                        onCellClicked={onCellClicked}
                        onRowClicked={onRowClicked}
                        onGridReady={onGridReady}
                        animateRows={true}
                        rowSelection={{
                            mode: 'multiRow',
                            checkboxes: true,
                            headerCheckbox: true
                        }}
                        getRowId={(params) => params.data.id}
                    />
                </div>

                {/* Right Sidebar */}
                <RightSidebar
                    columnsContent={
                        <ColumnManager
                            pageName="assets_explorer"
                            columnDefs={columnDefs}
                            gridApi={gridApi}
                            onClose={() => { }}
                        />
                    }
                    filtersContent={
                        <FilterPresets
                            pageName="assets_explorer"
                            gridApi={gridApi}
                        />
                    }
                />
            </div>
        </div>
    );
};
