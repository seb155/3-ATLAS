import { useState, useRef, useCallback, useMemo, useEffect } from 'react';
import axios from 'axios';
import { AgGridReact } from 'ag-grid-react';
import { ColDef, ModuleRegistry, RowClickedEvent } from 'ag-grid-community';
import {
    ClientSideRowModelModule,
    RowSelectionModule,
    TextFilterModule,
    NumberFilterModule,
    DateFilterModule,
    CellStyleModule,
    ValidationModule
} from 'ag-grid-community';
import {
    Upload, Download, Trash2, Database, FileSpreadsheet,
    ChevronRight, ChevronLeft, GripVertical, AlertTriangle,
    CheckCircle2, Loader2, FolderTree, Filter, Columns3,
    PanelRightClose, PanelRight, List, Zap, Clock, Play, ExternalLink
} from 'lucide-react';
import { logger } from '../services/logger';
import { useProjectStore } from '../store/useProjectStore';
import { useAppStore } from '../store/useAppStore';
import { useAuthStore } from '../store/useAuthStore';
import { Asset, AssetType, PhysicalLocation } from '../../types';
import { synapseTheme } from '../theme/ag-grid';
import { useThemeStore } from '../store/useThemeStore';
import { API_URL } from '../../config';
import { ColumnManager } from '../components/ColumnManager';


// Register AG Grid modules
ModuleRegistry.registerModules([
    ClientSideRowModelModule,
    RowSelectionModule,
    TextFilterModule,
    NumberFilterModule,
    DateFilterModule,
    CellStyleModule,
    ValidationModule
]);

// TreeNodeData can be Asset, PhysicalLocation, or generic object
type TreeNodeData =
    | Asset
    | PhysicalLocation
    | { id: string; name?: string; tag?: string; type?: string;[key: string]: unknown };

interface MiniTreeNodeProps {
    node: TreeNodeData;
    depth?: number;
    selectedId: string | null;
    onSelect: (node: TreeNodeData) => void;
    getChildren: (id: string | null) => TreeNodeData[];
}

// Mini Tree Node for navigation
const MiniTreeNode = ({ node, depth = 0, selectedId, onSelect, getChildren }: MiniTreeNodeProps) => {
    const [isExpanded, setIsExpanded] = useState(depth < 2);
    const children = getChildren(node.id);
    const hasChildren = children && children.length > 0;
    const isSelected = selectedId === node.id;
    const isAsset = !!(node as Asset).tag;

    return (
        <div>
            <div
                className={`flex items-center py-1 px-2 cursor-pointer text-xs transition-colors rounded ${isSelected
                    ? 'bg-mining-teal/20 text-mining-teal'
                    : isAsset ? 'text-slate-300 hover:bg-slate-800' : 'text-slate-400 hover:bg-slate-800 hover:text-slate-200'
                    }`}
                style={{ paddingLeft: `${depth * 12 + 4}px` }}
                onClick={() => onSelect(node)}
            >
                {hasChildren ? (
                    <button
                        onClick={(e) => { e.stopPropagation(); setIsExpanded(!isExpanded); }}
                        className="mr-1 p-0.5"
                    >
                        {isExpanded ? <ChevronRight size={10} className="rotate-90 transition-transform" /> : <ChevronRight size={10} className="transition-transform" />}
                    </button>
                ) : (
                    <span className="w-4 mr-1" />
                )}
                <span className={`truncate ${isAsset ? 'font-mono text-mining-teal' : 'font-medium'}`}>
                    {(node as Asset).tag || (node as Record<string, unknown>).name as string}
                </span>
                {isAsset && (node as Asset).type && (
                    <span className="ml-auto text-[10px] text-slate-500">{(node as Asset).type}</span>
                )}
            </div>
            {isExpanded && hasChildren && children.map((child: TreeNodeData) => (
                <MiniTreeNode
                    key={child.id}
                    node={child}
                    depth={depth + 1}
                    selectedId={selectedId}
                    onSelect={onSelect}
                    getChildren={getChildren}
                />
            ))}
        </div>
    );
};

export default function Ingestion() {
    const [isLoading, setIsLoading] = useState(false);
    const [status, setStatus] = useState<'IDLE' | 'IMPORTING' | 'SUCCESS' | 'ERROR'>('IDLE');
    const [panelWidth, setPanelWidth] = useState(320);
    const [isResizing, setIsResizing] = useState(false);
    const [showNavigator, setShowNavigator] = useState(true);
    const [showPanel, setShowPanel] = useState(true);
    const [selectedAssetId, setSelectedAssetId] = useState<string | null>(null);
    const [searchFilter, setSearchFilter] = useState('');
    const [navigatorMode, setNavigatorMode] = useState<'tree' | 'list'>('tree');
    const [activeRightTab, setActiveRightTab] = useState<'data' | 'columns' | 'filters' | 'actions'>('data');

    // Rule execution states
    const [isExecutingRules, setIsExecutingRules] = useState(false);
    const [ruleExecutionResult, setRuleExecutionResult] = useState<Record<string, unknown> | null>(null);

    const gridRef = useRef<AgGridReact>(null);
    const panelRef = useRef<HTMLDivElement>(null);

    const { currentProject } = useProjectStore();
    const { instruments, locations, refreshData } = useAppStore();
    const { token } = useAuthStore();
    const { isDarkMode } = useThemeStore();

    // Resizable panel logic
    const startResize = useCallback((e: React.MouseEvent) => {
        e.preventDefault();
        setIsResizing(true);
    }, []);

    useEffect(() => {
        const handleMouseMove = (e: MouseEvent) => {
            if (!isResizing) return;
            const newWidth = window.innerWidth - e.clientX;
            setPanelWidth(Math.max(280, Math.min(600, newWidth)));
        };

        const handleMouseUp = () => setIsResizing(false);

        if (isResizing) {
            document.addEventListener('mousemove', handleMouseMove);
            document.addEventListener('mouseup', handleMouseUp);
            document.body.style.cursor = 'col-resize';
            document.body.style.userSelect = 'none';
        }

        return () => {
            document.removeEventListener('mousemove', handleMouseMove);
            document.removeEventListener('mouseup', handleMouseUp);
            document.body.style.cursor = '';
            document.body.style.userSelect = '';
        };
    }, [isResizing]);

    // Build tree for navigator - supports both locations and direct asset list
    const getLocationChildren = useCallback((parentId: string | null) => {
        if (parentId === null) {
            // Root level - return locations without parent
            const rootLocations = locations.filter(l => !l.parentId);
            if (rootLocations.length > 0) return rootLocations;
            // If no locations, return all assets directly
            return instruments;
        }

        // Check if parentId is a location
        const isLocation = locations.some(l => l.id === parentId);
        if (isLocation) {
            const childLocs = locations.filter(l => l.parentId === parentId);
            const childAssets = instruments.filter(i => i.locationId === parentId);
            return [...childLocs, ...childAssets];
        }

        // parentId is an asset - no children
        return [];
    }, [locations, instruments]);

    // For list mode - group by type
    const assetsByType = useMemo(() => {
        const grouped: Record<string, typeof instruments> = {};
        instruments.forEach(asset => {
            const type = asset.type || 'UNKNOWN';
            if (!grouped[type]) grouped[type] = [];
            grouped[type].push(asset);
        });
        return grouped;
    }, [instruments]);

    // AG Grid Column Definitions - Raw data view
    const columnDefs = useMemo<ColDef[]>(() => [
        {
            field: 'tag',
            headerName: 'TAG',
            pinned: 'left',
            width: 140,
            filter: true,
            sortable: true,
            cellClass: 'font-mono font-medium text-mining-teal'
        },
        { field: 'type', headerName: 'TYPE', width: 120, filter: true, sortable: true },
        { field: 'description', headerName: 'DESCRIPTION', width: 220, filter: true, sortable: true },
        { field: 'area', headerName: 'AREA', width: 100, filter: true, sortable: true },
        { field: 'system', headerName: 'SYSTEM', width: 120, filter: true, sortable: true },
        { field: 'ioType', headerName: 'IO TYPE', width: 100, filter: true, sortable: true },
        {
            headerName: 'LOCATION',
            width: 150,
            valueGetter: (params) => {
                const loc = locations.find(l => l.id === params.data?.locationId);
                return loc?.name || '-';
            },
            filter: true,
            sortable: true
        },
        {
            headerName: 'ELECTRICAL',
            children: [
                { field: 'electrical.voltage', headerName: 'VOLTAGE', width: 90, filter: 'agNumberColumnFilter', sortable: true },
                { field: 'electrical.powerKW', headerName: 'POWER (kW)', width: 100, filter: 'agNumberColumnFilter', sortable: true },
                { field: 'electrical.loadType', headerName: 'LOAD TYPE', width: 100, filter: 'agTextColumnFilter', sortable: true }
            ]
        },
        {
            headerName: 'PROCESS',
            children: [
                { field: 'process.fluid', headerName: 'FLUID', width: 100, filter: 'agTextColumnFilter', sortable: true },
                { field: 'process.minRange', headerName: 'MIN', width: 70, filter: 'agNumberColumnFilter', sortable: true },
                { field: 'process.maxRange', headerName: 'MAX', width: 70, filter: 'agNumberColumnFilter', sortable: true },
                { field: 'process.units', headerName: 'UNITS', width: 80, filter: 'agTextColumnFilter', sortable: true }
            ]
        },
        {
            headerName: 'PROCUREMENT',
            children: [
                { field: 'manufacturerPartId', headerName: 'PART #', width: 140, filter: true, sortable: true },
                { field: 'purchasing.workPackageId', headerName: 'PACKAGE', width: 120, filter: true, sortable: true },
                { field: 'purchasing.status', headerName: 'STATUS', width: 100, filter: true, sortable: true }
            ]
        },
        { field: 'id', headerName: 'UUID', width: 280, cellClass: 'text-slate-500 font-mono text-xs' }
    ], [locations]);

    const defaultColDef = useMemo(() => ({
        resizable: true,
        sortable: true,
        filter: true,
        cellClass: 'text-slate-300'
    }), []);

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

    // Handle row click to sync with navigator
    const onRowClicked = useCallback((event: RowClickedEvent) => {
        setSelectedAssetId(event.data?.id);
    }, []);

    // Handle navigator selection
    const onNavigatorSelect = useCallback((node: TreeNodeData) => {
        if ((node as Asset).tag) {
            // It's an asset
            setSelectedAssetId(node.id);
            // Scroll to row in grid
            gridRef.current?.api?.forEachNode((rowNode) => {
                if (rowNode.data?.id === node.id) {
                    rowNode.setSelected(true);
                    gridRef.current?.api?.ensureNodeVisible(rowNode, 'middle');
                }
            });
        }
    }, []);

    // Import handlers
    const handleFileUpload = async (file: File) => {
        if (!file.name.endsWith('.csv')) {
            logger.error('Please upload a CSV file');
            return;
        }

        setIsLoading(true);
        setStatus('IMPORTING');
        const formData = new FormData();
        formData.append('file', file);

        try {
            const projectId = currentProject?.id || 'default-project';
            const res = await axios.post(`${API_URL}/api/v1/import_export/import`, formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                    'X-Project-ID': projectId,
                    'Authorization': `Bearer ${token}`
                }
            });

            const { created, updated, errors } = res.data;
            logger.success(`Imported: ${created} created, ${updated} updated`);
            if (errors.length > 0) {
                logger.warn(`Import finished with ${errors.length} errors`, { errors });
            }

            await refreshData();
            setStatus('SUCCESS');
        } catch (err) {
            logger.error('Import failed', err);
            setStatus('ERROR');
        } finally {
            setIsLoading(false);
        }
    };

    const handleDevImport = async () => {
        setIsLoading(true);
        setStatus('IMPORTING');
        try {
            if (!token) {
                logger.error('No authentication token found');
                setStatus('ERROR');
                return;
            }

            const projectId = currentProject?.id || 'default-project';
            const res = await axios.post(`${API_URL}/api/v1/import_export/dev-import`, {}, {
                headers: {
                    'X-Project-ID': projectId,
                    'Authorization': `Bearer ${token}`
                }
            });

            const { created, updated, errors } = res.data;
            logger.success(`Dev Import: ${created} created, ${updated} updated`);
            if (errors.length > 0) logger.warn(`Errors: ${errors.length}`, { errors });

            await refreshData();
            setStatus('SUCCESS');
        } catch (e) {
            logger.error('Dev Import failed', e as Error);
            setStatus('ERROR');
        } finally {
            setIsLoading(false);
        }
    };

    const handleExport = async () => {
        try {
            const projectId = currentProject?.id || 'default-project';
            const response = await axios.get(`${API_URL}/api/v1/import_export/export`, {
                headers: {
                    'X-Project-ID': projectId,
                    'Authorization': `Bearer ${token}`
                },
                responseType: 'blob',
            });

            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `assets_export_${currentProject?.name || 'project'}.csv`);
            document.body.appendChild(link);
            link.click();
            link.remove();
            logger.success('Export completed');
        } catch (e) {
            logger.error('Export failed', e as Error);
        }
    };

    const handleClearProjectData = async () => {
        if (!confirm("Are you sure you want to delete ALL assets for this project? This cannot be undone.")) return;

        try {
            const projectId = currentProject?.id || 'default-project';
            const res = await axios.delete(`${API_URL}/api/v1/mock/project-data`, {
                headers: {
                    'X-Project-ID': projectId,
                    'Authorization': `Bearer ${token}`
                }
            });

            logger.success(`Project data cleared: ${JSON.stringify(res.data.deleted)}`);
            await refreshData();
            setStatus('IDLE');
        } catch (e) {
            // 401 errors are handled globally by axios interceptor (auto-logout)
            // Only handle other errors here
            if (e?.response?.status !== 401) {
                logger.error("Failed to clear project data", e as Error);
            }
        }
    };

    const handleExecuteRules = async () => {
        setIsExecutingRules(true);
        setRuleExecutionResult(null);

        try {
            const projectId = currentProject?.id || 'default-project';
            const response = await axios.post(
                `${API_URL}/api/v1/rules/execute`,
                { project_id: projectId },
                {
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'X-Project-ID': projectId
                    }
                }
            );

            const result = response.data;
            setRuleExecutionResult(result);

            logger.success(
                `✅ Rules executed! Created ${result.actions_taken} assets in ${result.time_elapsed_ms}ms`
            );

            // Refresh data to show newly created assets
            await refreshData();

        } catch (error) {
            logger.error('Failed to execute rules: ' + error.message, error);
        } finally {
            setIsExecutingRules(false);
        }
    };

    const fileInputRef = useRef<HTMLInputElement>(null);

    return (
        <>
            <div className="flex h-[calc(100vh-4rem)] bg-slate-950 text-slate-200 overflow-hidden">
                {/* Left Mini Navigator (collapsible) */}
                {showNavigator && (
                    <div className="w-56 border-r border-slate-800 bg-slate-900/50 flex flex-col">
                        <div className="p-3 border-b border-slate-800 flex items-center justify-between">
                            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-2">
                                <FolderTree size={14} />
                                Navigator
                            </span>
                            <div className="flex items-center gap-1">
                                <button
                                    onClick={() => setNavigatorMode(navigatorMode === 'tree' ? 'list' : 'tree')}
                                    className={`p-1 rounded transition-colors ${navigatorMode === 'list' ? 'text-mining-teal bg-mining-teal/10' : 'text-slate-500 hover:text-slate-300'}`}
                                    title={navigatorMode === 'tree' ? 'Switch to List View' : 'Switch to Tree View'}
                                >
                                    <List size={12} />
                                </button>
                                <button
                                    onClick={() => setShowNavigator(false)}
                                    className="text-slate-500 hover:text-slate-300 p-1"
                                >
                                    <ChevronLeft size={14} />
                                </button>
                            </div>
                        </div>
                        <div className="flex-1 overflow-y-auto p-2 custom-scrollbar">
                            {instruments.length === 0 ? (
                                // Empty state
                                <div className="flex flex-col items-center justify-center h-full text-slate-500 px-4 text-center">
                                    <Database size={32} className="mb-2 opacity-30" />
                                    <p className="text-xs">No data loaded</p>
                                    <p className="text-[10px] text-slate-600 mt-1">Import data to begin</p>
                                </div>
                            ) : navigatorMode === 'tree' ? (
                                // Tree mode - show locations hierarchy or assets directly
                                locations.filter(l => !l.parentId).length > 0 ? (
                                    locations.filter(l => !l.parentId).map(root => (
                                        <MiniTreeNode
                                            key={root.id}
                                            node={root}
                                            selectedId={selectedAssetId}
                                            onSelect={onNavigatorSelect}
                                            getChildren={getLocationChildren}
                                        />
                                    ))
                                ) : (
                                    // No locations - show assets directly
                                    instruments.map(asset => (
                                        <div
                                            key={asset.id}
                                            className={`flex items-center py-1 px-2 cursor-pointer text-xs transition-colors rounded ${selectedAssetId === asset.id
                                                ? 'bg-mining-teal/20 text-mining-teal'
                                                : 'text-slate-300 hover:bg-slate-800'
                                                }`}
                                            onClick={() => onNavigatorSelect(asset)}
                                        >
                                            <span className="truncate font-mono text-mining-teal">{asset.tag}</span>
                                            <span className="ml-auto text-[10px] text-slate-500">{asset.type}</span>
                                        </div>
                                    ))
                                )
                            ) : (
                                // List mode - grouped by type
                                Object.entries(assetsByType).map(([type, assets]) => (
                                    <div key={type} className="mb-2">
                                        <div className="text-[10px] font-semibold text-slate-500 uppercase px-2 py-1">{type} ({assets.length})</div>
                                        {assets.map(asset => (
                                            <div
                                                key={asset.id}
                                                className={`flex items-center py-1 px-3 cursor-pointer text-xs transition-colors rounded ${selectedAssetId === asset.id
                                                    ? 'bg-mining-teal/20 text-mining-teal'
                                                    : 'text-slate-300 hover:bg-slate-800'
                                                    }`}
                                                onClick={() => onNavigatorSelect(asset)}
                                            >
                                                <span className="truncate font-mono">{asset.tag}</span>
                                            </div>
                                        ))}
                                    </div>
                                ))
                            )}
                        </div>
                        <div className="p-2 border-t border-slate-800 text-xs text-slate-500 text-center">
                            {instruments.length} assets | {locations.length} locations
                        </div>
                    </div>
                )}

                {/* Main Content - AG Grid */}
                <div className="flex-1 flex flex-col min-w-0">
                    {/* Toolbar */}
                    <div className="h-12 bg-slate-900/80 border-b border-slate-800 flex items-center px-4 gap-4">
                        {!showNavigator && (
                            <button
                                onClick={() => setShowNavigator(true)}
                                className="p-2 text-slate-400 hover:text-white hover:bg-slate-800 rounded transition-colors"
                                title="Show Navigator"
                            >
                                <FolderTree size={16} />
                            </button>
                        )}

                        <div className="flex items-center gap-2 flex-1">
                            <FileSpreadsheet size={18} className="text-mining-teal" />
                            <span className="font-semibold text-white">P&ID Data</span>
                            <span className="text-xs text-slate-500 ml-2">
                                {filteredInstruments.length} / {instruments.length} records
                            </span>
                        </div>

                        {/* Quick Filter */}
                        <div className="relative">
                            <Filter size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
                            <input
                                type="text"
                                placeholder="Filter..."
                                value={searchFilter}
                                onChange={(e) => setSearchFilter(e.target.value)}
                                className="w-48 bg-slate-800 border border-slate-700 rounded-lg pl-9 pr-3 py-1.5 text-sm text-slate-300 focus:ring-1 focus:ring-mining-teal focus:border-mining-teal outline-none transition-colors"
                            />
                        </div>

                        <button
                            onClick={() => gridRef.current?.api?.sizeColumnsToFit()}
                            className="p-2 text-slate-400 hover:text-white hover:bg-slate-800 rounded transition-colors"
                            title="Auto-fit columns"
                        >
                            <Columns3 size={16} />
                        </button>

                        {/* Column Manager is now in RightSidebar - No button needed */}


                        {/* Status indicator */}
                        {status === 'SUCCESS' && (
                            <div className="flex items-center gap-2 text-green-400 text-sm">
                                <CheckCircle2 size={16} />
                                <span>Success</span>
                            </div>
                        )}
                        {status === 'IMPORTING' && (
                            <div className="flex items-center gap-2 text-mining-teal text-sm">
                                <Loader2 size={16} className="animate-spin" />
                                <span>Processing...</span>
                            </div>
                        )}

                        {/* Execute Rules button after successful import */}
                        {status === 'SUCCESS' && (
                            <>
                                <div className="h-6 w-px bg-slate-700" />
                                <button
                                    onClick={handleExecuteRules}
                                    disabled={isExecutingRules}
                                    className="flex items-center gap-2 px-3 py-1.5 bg-green-600/20 hover:bg-green-600/30 disabled:opacity-50 disabled:cursor-not-allowed border border-green-500/30 rounded text-green-300 text-sm font-medium transition-colors"
                                    title="Execute all active rules on imported assets"
                                >
                                    {isExecutingRules ? (
                                        <>
                                            <Loader2 size={14} className="animate-spin" />
                                            <span>Executing...</span>
                                        </>
                                    ) : (
                                        <>
                                            <Play size={14} />
                                            <span>Execute Rules</span>
                                        </>
                                    )}
                                </button>
                            </>
                        )}
                    </div>

                    {/* Grid */}
                    <div className="flex-1" data-ag-theme-mode={isDarkMode ? 'dark' : 'light'}>
                        <AgGridReact
                            theme={synapseTheme}
                            ref={gridRef}
                            rowData={filteredInstruments}
                            columnDefs={columnDefs}
                            defaultColDef={defaultColDef}
                            animateRows={true}
                            rowSelection={{ mode: 'singleRow' }}
                            onRowClicked={onRowClicked}
                            suppressCellFocus={true}
                            getRowId={(params) => params.data.id}
                        />
                    </div>
                </div>

                {/* Right Panel - Resizable & Collapsible */}
                <div
                    ref={panelRef}
                    className="relative flex flex-col bg-slate-900 border-l border-slate-800 transition-all duration-300"
                    style={{ width: showPanel ? panelWidth : 48 }}
                >
                    {/* Resize Handle - only visible when expanded */}
                    {showPanel && (
                        <div
                            className="absolute left-0 top-0 bottom-0 w-1 cursor-col-resize hover:bg-mining-teal/50 transition-colors group z-10"
                            onMouseDown={startResize}
                        >
                            <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 opacity-0 group-hover:opacity-100 transition-opacity">
                                <GripVertical size={12} className="text-mining-teal" />
                            </div>
                        </div>
                    )}

                    {/* Collapsed State */}
                    {!showPanel && (
                        <div className="flex flex-col items-center justify-start pt-4 h-full">
                            <button
                                onClick={() => setShowPanel(true)}
                                className="p-2 text-slate-400 hover:text-mining-teal hover:bg-slate-800 rounded transition-colors mb-2"
                                title="Expand Panel"
                            >
                                <ChevronLeft size={20} />
                            </button>
                            <div className="writing-mode-vertical text-xs text-slate-500 font-medium uppercase tracking-wider mt-4"
                                style={{ writingMode: 'vertical-rl', textOrientation: 'mixed' }}
                            >
                                Data
                            </div>
                        </div>
                    )}

                    {/* Expanded State */}
                    {showPanel && (
                        <>
                            {/* Panel Header with Tabs */}
                            <div className="border-b border-slate-800 flex items-center justify-between p-2">
                                {/* Horizontal Tabs */}
                                <div className="flex gap-1">
                                    <button
                                        onClick={() => setActiveRightTab('data')}
                                        className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${activeRightTab === 'data'
                                            ? 'bg-mining-teal/20 text-mining-teal border border-mining-teal/30'
                                            : 'text-slate-400 hover:text-white hover:bg-slate-800 border border-transparent'
                                            }`}
                                    >
                                        <Database size={14} />
                                        Data
                                    </button>
                                    <button
                                        onClick={() => setActiveRightTab('columns')}
                                        className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${activeRightTab === 'columns'
                                            ? 'bg-mining-teal/20 text-mining-teal border border-mining-teal/30'
                                            : 'text-slate-400 hover:text-white hover:bg-slate-800 border border-transparent'
                                            }`}
                                    >
                                        <Columns3 size={14} />
                                        Columns
                                    </button>
                                    <button
                                        onClick={() => setActiveRightTab('filters')}
                                        className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${activeRightTab === 'filters'
                                            ? 'bg-mining-teal/20 text-mining-teal border border-mining-teal/30'
                                            : 'text-slate-400 hover:text-white hover:bg-slate-800 border border-transparent'
                                            }`}
                                    >
                                        <Filter size={14} />
                                        Filters
                                    </button>
                                    <button
                                        onClick={() => setActiveRightTab('actions')}
                                        className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${activeRightTab === 'actions'
                                            ? 'bg-mining-teal/20 text-mining-teal border border-mining-teal/30'
                                            : 'text-slate-400 hover:text-white hover:bg-slate-800 border border-transparent'
                                            }`}
                                    >
                                        <Zap size={14} />
                                        Actions
                                    </button>
                                </div>
                                <button
                                    onClick={() => setShowPanel(false)}
                                    className="text-slate-500 hover:text-slate-300 p-1"
                                >
                                    <ChevronRight size={16} />
                                </button>
                            </div>

                            {/* Panel Content */}
                            <div className="flex-1 overflow-y-auto custom-scrollbar">
                                {activeRightTab === 'data' && (
                                    <div className="p-4 space-y-4">
                                        {/* Upload Section */}
                                        <div className="bg-slate-800/50 rounded-xl p-4 border border-slate-700/50">
                                            <h3 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
                                                <Upload size={14} />
                                                Import Data
                                            </h3>

                                            <input
                                                ref={fileInputRef}
                                                type="file"
                                                accept=".csv"
                                                className="hidden"
                                                onChange={(e) => {
                                                    const file = e.target.files?.[0];
                                                    if (file) handleFileUpload(file);
                                                    e.target.value = '';
                                                }}
                                            />

                                            <div
                                                onClick={() => fileInputRef.current?.click()}
                                                className="border-2 border-dashed border-slate-600 hover:border-mining-teal/50 rounded-lg p-6 text-center transition-all cursor-pointer bg-slate-900/50 hover:bg-slate-800/50 group"
                                            >
                                                <div className="w-10 h-10 bg-slate-700 rounded-full flex items-center justify-center mx-auto mb-2 group-hover:scale-110 transition-transform">
                                                    <FileSpreadsheet size={18} className="text-mining-teal" />
                                                </div>
                                                <p className="text-sm text-slate-300 font-medium">Drop CSV here</p>
                                                <p className="text-xs text-slate-500 mt-1">or click to browse</p>
                                            </div>

                                            <button
                                                onClick={handleDevImport}
                                                disabled={isLoading}
                                                className="w-full mt-3 px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg text-sm font-medium text-slate-300 transition-colors flex items-center justify-center gap-2 disabled:opacity-50"
                                            >
                                                {isLoading ? <Loader2 size={14} className="animate-spin" /> : <Database size={14} />}
                                                Load Server Mock Data
                                            </button>
                                        </div>

                                        {/* Export Section */}
                                        <div className="bg-slate-800/50 rounded-xl p-4 border border-slate-700/50">
                                            <h3 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
                                                <Download size={14} />
                                                Export Data
                                            </h3>

                                            <button
                                                onClick={handleExport}
                                                className="w-full px-4 py-3 bg-mining-teal/20 hover:bg-mining-teal/30 border border-mining-teal/30 rounded-lg text-sm font-medium text-mining-teal transition-colors flex items-center justify-center gap-2"
                                            >
                                                <Download size={16} />
                                                Export to CSV
                                            </button>

                                            <p className="text-xs text-slate-500 mt-2 text-center">
                                                Downloads all {instruments.length} assets
                                            </p>
                                        </div>

                                        {/* Rule Engine Section */}
                                        <div className="bg-gradient-to-br from-slate-800/50 to-mining-teal/5 rounded-xl p-4 border border-mining-teal/30">
                                            <h3 className="text-sm font-semibold text-white mb-2 flex items-center gap-2">
                                                <Zap size={14} className="text-mining-teal" />
                                                Rule Engine
                                            </h3>
                                            <p className="text-xs text-slate-400 mb-3">
                                                Apply engineering rules to generate child assets (motors, instruments, locations, cables) from imported P&ID data.
                                            </p>

                                            <button
                                                onClick={handleExecuteRules}
                                                disabled={isExecutingRules || instruments.length === 0}
                                                className="w-full px-4 py-3 bg-mining-teal hover:bg-teal-600 disabled:bg-slate-700 disabled:text-slate-500 rounded-lg text-sm font-medium text-white transition-all flex items-center justify-center gap-2"
                                            >
                                                {isExecutingRules ? (
                                                    <>
                                                        <Clock size={16} className="animate-spin" />
                                                        Executing Rules...
                                                    </>
                                                ) : (
                                                    <>
                                                        <Zap size={16} />
                                                        Execute All Rules
                                                    </>
                                                )}
                                            </button>

                                            {ruleExecutionResult && (
                                                <div className="mt-3 space-y-2">
                                                    <div className="flex items-center justify-between text-xs">
                                                        <span className="text-slate-400">Rules Applied:</span>
                                                        <span className="text-mining-teal font-mono font-semibold">
                                                            {String(ruleExecutionResult.total_rules ?? 0)}
                                                        </span>
                                                    </div>
                                                    <div className="flex items-center justify-between text-xs">
                                                        <span className="text-slate-400">Assets Created:</span>
                                                        <span className="text-green-400 font-mono font-semibold">
                                                            +{String(ruleExecutionResult.actions_taken ?? 0)}
                                                        </span>
                                                    </div>
                                                    <div className="flex items-center justify-between text-xs">
                                                        <span className="text-slate-400">Execution Time:</span>
                                                        <span className="text-slate-300 font-mono">
                                                            {String(ruleExecutionResult.time_elapsed_ms ?? 0)}ms
                                                        </span>
                                                    </div>
                                                </div>
                                            )}
                                        </div>

                                        {/* Stats */}
                                        <div className="grid grid-cols-2 gap-2">
                                            <div className="bg-slate-800/50 rounded-lg p-3 border border-slate-700/50 text-center">
                                                <div className="text-2xl font-bold text-white">{instruments.length}</div>
                                                <div className="text-xs text-slate-500">Assets</div>
                                            </div>
                                            <div className="bg-slate-800/50 rounded-lg p-3 border border-slate-700/50 text-center">
                                                <div className="text-2xl font-bold text-white">{locations.length}</div>
                                                <div className="text-xs text-slate-500">Locations</div>
                                            </div>
                                        </div>

                                        {/* Asset Types Breakdown */}
                                        {instruments.length > 0 && (
                                            <div className="bg-slate-800/50 rounded-xl p-4 border border-slate-700/50">
                                                <h3 className="text-sm font-semibold text-white mb-3">Asset Breakdown</h3>
                                                <div className="space-y-2">
                                                    {Object.values(AssetType).map(type => {
                                                        const count = instruments.filter(i => i.type === type).length;
                                                        if (count === 0) return null;
                                                        const percentage = (count / instruments.length) * 100;
                                                        return (
                                                            <div key={type} className="flex items-center gap-2">
                                                                <span className="text-xs text-slate-400 w-24 truncate">{type}</span>
                                                                <div className="flex-1 h-2 bg-slate-700 rounded-full overflow-hidden">
                                                                    <div
                                                                        className="h-full bg-mining-teal rounded-full transition-all"
                                                                        style={{ width: `${percentage}%` }}
                                                                    />
                                                                </div>
                                                                <span className="text-xs text-slate-500 w-8 text-right">{count}</span>
                                                            </div>
                                                        );
                                                    })}
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                )}

                                {activeRightTab === 'columns' && (
                                    <ColumnManager
                                        pageName="ingestion"
                                        columnDefs={columnDefs}
                                        gridApi={gridRef.current?.api}
                                        onClose={() => {/* No close needed */ }}
                                    />
                                )}

                                {activeRightTab === 'filters' && (
                                    <div className="p-4 text-slate-400 text-center mt-10">
                                        <Filter size={48} className="mx-auto mb-4 opacity-20" />
                                        <p>Filter presets coming soon</p>
                                    </div>
                                )}

                                {activeRightTab === 'actions' && (
                                    <div className="p-4 text-slate-400 text-center mt-10">
                                        <Zap size={48} className="mx-auto mb-4 opacity-20" />
                                        <p>Quick actions coming soon</p>
                                    </div>
                                )}
                            </div>

                            {/* Danger Zone - Fixed at bottom (Data tab only) */}
                            {activeRightTab === 'data' && (
                                <div className="p-4 border-t border-slate-800 bg-slate-900">
                                    <div className="bg-red-900/20 border border-red-900/30 rounded-lg p-3">
                                        <div className="flex items-center gap-2 mb-2">
                                            <AlertTriangle size={14} className="text-red-400" />
                                            <span className="text-sm font-semibold text-red-400">Danger Zone</span>
                                        </div>
                                        <button
                                            onClick={handleClearProjectData}
                                            className="w-full px-4 py-2 rounded-lg text-sm font-medium transition-all bg-red-500/10 hover:bg-red-500/20 text-red-400 border border-red-500/30 hover:border-red-500/50 flex items-center justify-center gap-2"
                                        >
                                            <Trash2 size={14} />
                                            Clear All Project Data
                                        </button>
                                    </div>
                                </div>
                            )}
                        </>
                    )}
                </div>

                {/* Right Sidebar integrated into Data Operations panel */}
            </div>
        </>
    );
}
