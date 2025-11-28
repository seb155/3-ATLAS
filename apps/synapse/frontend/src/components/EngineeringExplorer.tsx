import React, { useState, useMemo, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Asset, PhysicalLocation, LocationType, AssetType } from '../../types';
import { CabinetPlanner as Engine, TreeNode } from '../services/engineeringEngine';
import { RackPanel } from './RackPanel';
import { LocationOverview } from './LocationOverview';
import { AssetDetails } from './AssetDetails';
import { ExplorerSidebar } from './explorer/ExplorerSidebar';
import { AssetGrid } from './explorer/AssetGrid';
import { AssetDatasheet } from './explorer/AssetDatasheet';
import {
    LayoutDashboard, Database, Server, Settings, ArrowLeft, Activity, Zap, ShoppingBag, Factory, Cpu, Box
} from 'lucide-react';
import { useAppStore } from '../store/useAppStore';
import { useAuthStore } from '../store/useAuthStore';
import { useProjectStore } from '../store/useProjectStore';
import axios from 'axios';
import { API_URL } from '@/config';
import { CATALOG } from '../../constants';
import { Tabs } from './ui/Tabs';
import { Button } from './ui/Button';

// --- ICONS (Reused for Header) ---
const LocationIcon = ({ type }: { type: LocationType }) => {
    return <Box size={14} />;
};
const AssetTreeIcon = ({ type }: { type: AssetType }) => <Box size={14} />;
const FunctionalIcon = ({ type }: { type: string }) => <Box size={14} />;
const WbsIcon = ({ type }: { type: string }) => <Box size={14} />;

interface HistoryState {
    viewMode: 'LBS' | 'FBS' | 'WBS';
    selectedId: string;
    selectedNode: Asset | PhysicalLocation | TreeNode | null;
    activeTab: 'OVERVIEW' | 'GRID' | 'DATASHEET' | 'RACK' | 'DETAILS';
    focusedAssetId: string | null;
}

export const EngineeringExplorer: React.FC = () => {
    // Global State
    const { instruments, locations, setInstruments } = useAppStore();
    const { currentProject } = useProjectStore();
    const { token } = useAuthStore();

    // React Router
    const navigate = useNavigate();

    // Local UI State
    const [viewMode, setViewMode] = useState<'LBS' | 'FBS' | 'WBS'>('LBS');
    const [selectedId, setSelectedId] = useState<string>('');
    const [selectedNode, setSelectedNode] = useState<Asset | PhysicalLocation | TreeNode | null>(null);
    const [activeTab, setActiveTab] = useState<'OVERVIEW' | 'GRID' | 'DATASHEET' | 'RACK' | 'DETAILS'>('GRID');
    const [assetDetailsTab, setAssetDetailsTab] = useState<'SPECS' | 'WIRING'>('SPECS');
    const [focusedAssetId, setFocusedAssetId] = useState<string | null>(null);

    const [history, setHistory] = useState<HistoryState[]>([]);

    // Trees (Memoized)
    const fbsTree = useMemo(() => Engine.getFBSTree(instruments), [instruments]);
    const wbsTree = useMemo(() => Engine.getWBSTree(instruments), [instruments]);

    // --- NAVIGATION LOGIC ---
    const addToHistory = useCallback(() => {
        setHistory(prev => [...prev, {
            viewMode, selectedId, selectedNode, activeTab, focusedAssetId
        }]);
    }, [viewMode, selectedId, selectedNode, activeTab, focusedAssetId]);

    const handleBack = useCallback(() => {
        if (history.length === 0) return;
        const prev = history[history.length - 1];
        setViewMode(prev.viewMode);
        setSelectedId(prev.selectedId);
        setSelectedNode(prev.selectedNode);
        setActiveTab(prev.activeTab);
        setFocusedAssetId(prev.focusedAssetId);
        setHistory(h => h.slice(0, -1));
    }, [history]);

    const handleSelect = useCallback((id: string, node: Asset | PhysicalLocation | TreeNode | null) => {
        if (selectedId && selectedId !== id) addToHistory();

        setSelectedId(id);
        setSelectedNode(node);

        if (node.type === 'SIGNAL') {
            setActiveTab('DETAILS');
            setAssetDetailsTab('WIRING');
            const assetId = node.assetId || node.id.replace('sig-', '');
            setFocusedAssetId(assetId);
            const asset = instruments.find(i => i.id === assetId);
            if (asset) {
                setSelectedNode(asset);
                // Update URL for signal asset
                navigate(`/engineering/assets/${assetId}`);
            }
            return;
        }

        if (node.tag) {
            setActiveTab('DETAILS');
            setAssetDetailsTab('SPECS');
            setFocusedAssetId(node.id);
            // Update URL when selecting an asset with a tag
            navigate(`/engineering/assets/${node.id}`);
        } else {
            // If selecting a folder/location, navigate back to base engineering view
            navigate('/engineering');
        }
    }, [selectedId, addToHistory, instruments, navigate]);

    // Sync from URL params (React Router)
    const params = useParams<{ assetId?: string }>();
    useEffect(() => {
        if (params.assetId && params.assetId !== selectedId) {
            const asset = instruments.find(i => i.id === params.assetId);
            if (asset) {
                handleSelect(asset.id, asset);
            }
        }
    }, [params.assetId, instruments, selectedId]); // Added selectedId to prevent loop

    const handleCrossNavigate = useCallback((targetMode: 'LBS' | 'FBS' | 'WBS', targetId: string) => {
        addToHistory();
        setViewMode(targetMode);
        let targetNode: Asset | PhysicalLocation | TreeNode | null = null;

        if (targetMode === 'LBS') {
            targetNode = locations.find(l => l.id === targetId);
        } else if (targetMode === 'FBS') {
            for (const area of fbsTree) {
                if (area.id === targetId) targetNode = area;
                const sys = area.children?.find((s: TreeNode) => s.id === targetId);
                if (sys) targetNode = sys;
            }
        } else if (targetMode === 'WBS') {
            targetNode = wbsTree.find(pkg => pkg.id === targetId);
        }

        if (targetNode) {
            setSelectedId(targetId);
            setSelectedNode(targetNode);
            // Logic to set active tab based on node type (simplified)
            setActiveTab('GRID');
        } else {
            console.warn(`Node ${targetId} not found.`);
        }
    }, [addToHistory, locations, fbsTree, wbsTree]);

    const handleUpdateAsset = useCallback(async (updatedAsset: Asset) => {
        try {
            // Optimistic Update
            const updatedInstruments = instruments.map(i => i.id === updatedAsset.id ? updatedAsset : i);
            setInstruments(updatedInstruments);
            if (selectedNode && selectedNode.id === updatedAsset.id) {
                setSelectedNode(updatedAsset);
            }

            // API Call
            await axios.put(`${API_URL}/api/v1/assets/${updatedAsset.id}`, updatedAsset, {
                headers: {
                    'X-Project-ID': currentProject?.id,
                    'Authorization': `Bearer ${token}`
                }
            });
        } catch (error) {
            console.error("Failed to update asset:", error);
            // Revert optimistic update if needed (not implemented here for simplicity)
            throw error; // Re-throw so Datasheet knows it failed
        }
    }, [instruments, setInstruments, selectedNode, currentProject?.id, token]);

    // Filter Assets for Grid (Drill Down Logic)
    const filteredAssets = useMemo(() => {
        if (!selectedNode) return [];
        if (selectedNode.tag) return [selectedNode];

        // Handle Unassigned Assets Folder
        if (selectedNode.id === 'unassigned-root') {
            return instruments.filter(i => !i.locationId);
        }

        if (viewMode === 'LBS') {
            const descendantIds = Engine.getDescendantLocationIds(selectedNode.id, locations);
            const targetIds = [selectedNode.id, ...descendantIds];
            return instruments.filter(i => i.locationId && targetIds.includes(i.locationId));
        } else if (viewMode === 'FBS') {
            if (selectedNode.type === 'AREA') return instruments.filter(i => i.area === selectedNode.name.replace('Area ', ''));
            if (selectedNode.type === 'SYSTEM') return instruments.filter(i => i.system === selectedNode.originalSystem && i.area === selectedNode.originalArea);
        } else if (viewMode === 'WBS') {
            if (selectedNode.type === 'PACKAGE') return instruments.filter(i => i.purchasing?.workPackageId === selectedNode.name);
        }
        return [];
    }, [selectedNode, viewMode, instruments, locations]);

    const effectiveFocusedAsset = useMemo(() => {
        if (selectedNode?.tag) return selectedNode;
        if (focusedAssetId) return instruments.find(i => i.id === focusedAssetId);
        return null;
    }, [selectedNode, focusedAssetId, instruments]);

    return (
        <div className="flex h-full overflow-hidden bg-slate-950">

            <ExplorerSidebar
                instruments={instruments}
                locations={locations}
                viewMode={viewMode}
                setViewMode={setViewMode}
                selectedId={selectedId}
                onSelect={handleSelect}
            />

            {/* Main Content */}
            <div className="flex-1 flex flex-col min-w-0 bg-slate-900">
                {!selectedNode ? (
                    <div className="flex-1 flex flex-col items-center justify-center text-slate-500 opacity-50">
                        <Settings size={64} className="mb-4" strokeWidth={1} />
                        <p>Select a node to begin engineering.</p>
                    </div>
                ) : (
                    <>
                        <div className="h-14 border-b border-slate-800 flex items-center px-6 bg-slate-900 gap-4">
                            <Button
                                variant="ghost"
                                onClick={handleBack}
                                disabled={history.length === 0}
                                className="p-2 rounded-full"
                                title="Go Back"
                            >
                                <ArrowLeft size={20} />
                            </Button>

                            <h2 className="text-lg font-bold text-white flex items-center gap-2 flex-1">
                                <span className="truncate">
                                    {selectedNode.tag ? selectedNode.tag : selectedNode.name}
                                    {selectedNode.description && <span className="text-sm font-normal text-slate-500 ml-2">- {selectedNode.description}</span>}
                                </span>
                            </h2>
                        </div>

                        {/* Tabs */}
                        {!selectedNode.tag ? (
                            <Tabs
                                activeTab={activeTab}
                                onChange={(id) => setActiveTab(id as typeof activeTab)}
                                className="px-6"
                                tabs={[
                                    ...(viewMode === 'LBS' ? [{ id: 'OVERVIEW', label: 'Overview', icon: LayoutDashboard }] : []),
                                    { id: 'GRID', label: 'Assets', icon: Database, count: filteredAssets.length },
                                    ...(viewMode === 'LBS' ? [{ id: 'RACK', label: 'Rack Layout', icon: Server }] : [])
                                ]}
                            />
                        ) : (
                            <Tabs
                                activeTab={activeTab}
                                onChange={(id) => setActiveTab(id as typeof activeTab)}
                                className="px-6"
                                tabs={[
                                    { id: 'DETAILS', label: 'Overview', icon: LayoutDashboard },
                                    { id: 'DATASHEET', label: 'Datasheet', icon: Activity }
                                ]}
                            />
                        )}

                        <div className="flex-1 overflow-hidden bg-slate-950/30 relative">

                            {/* FOLDER VIEWS */}
                            {!selectedNode.tag && (
                                <>
                                    {activeTab === 'OVERVIEW' && viewMode === 'LBS' && (
                                        <LocationOverview locationId={selectedNode.id} instruments={instruments} locations={locations} onNavigate={(id) => handleSelect(id, locations.find(l => l.id === id))} />
                                    )}

                                    {activeTab === 'GRID' && (
                                        <AssetGrid
                                            instruments={filteredAssets}
                                            locations={locations}
                                            onUpdateInstruments={setInstruments}
                                            onAssetSelect={(asset) => {
                                                if (asset) {
                                                    handleSelect(asset.id, asset);
                                                }
                                            }}
                                        />
                                    )}

                                    {activeTab === 'RACK' && viewMode === 'LBS' && (
                                        <div className="p-6 h-full">
                                            <RackPanel locationId={selectedNode.id} instruments={instruments} locations={locations} catalog={CATALOG} />
                                        </div>
                                    )}
                                </>
                            )}

                            {/* ASSET VIEWS */}
                            {selectedNode.tag && (
                                <>
                                    {activeTab === 'DETAILS' && (
                                        (effectiveFocusedAsset) ?
                                            <AssetDetails
                                                asset={effectiveFocusedAsset}
                                                locations={locations}
                                                onNavigate={handleCrossNavigate}
                                                initialTab={assetDetailsTab}
                                            /> :
                                            <div className="p-10 text-center text-slate-500">No asset selected.</div>
                                    )}

                                    {activeTab === 'DATASHEET' && (
                                        <AssetDatasheet
                                            asset={selectedNode}
                                            locations={locations}
                                            onUpdate={handleUpdateAsset}
                                        />
                                    )}
                                </>
                            )}

                        </div>
                    </>
                )}
            </div>
        </div >
    );
};
