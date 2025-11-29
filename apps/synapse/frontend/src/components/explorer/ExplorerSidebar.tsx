import React, { useState, useMemo } from 'react';
import { Search, MapPin, Building, LayoutGrid, Server, Database, Layers, Box, GripVertical, ChevronDown, ChevronRight, Factory, Cpu, ShoppingBag, Settings, Activity, Zap } from 'lucide-react';
import { Asset, PhysicalLocation, LocationType, AssetType } from '../../../types';
import { CabinetPlanner as Engine } from '../../services/engineeringEngine';

// Tree node type that can be either a location, asset, or virtual node
type TreeNodeData = PhysicalLocation | Asset | { id: string; name: string; type: string;[key: string]: unknown };

interface ExplorerSidebarProps {
    instruments: Asset[];
    locations: PhysicalLocation[];
    viewMode: 'LBS' | 'FBS' | 'WBS';
    setViewMode: (mode: 'LBS' | 'FBS' | 'WBS') => void;
    selectedId: string;
    onSelect: (id: string, node: TreeNodeData) => void;
    wbsTree?: TreeNodeData[];
}

// --- ICONS ---
const LocationIcon = ({ type }: { type: LocationType }) => {
    switch (type) {
        case LocationType.SITE: return <MapPin size={14} className="text-green-400" />;
        case LocationType.EHOUSE: return <Building size={14} className="text-blue-400" />;
        case LocationType.ROOM: return <LayoutGrid size={14} className="text-slate-400" />;
        case LocationType.MCC: return <Server size={14} className="text-orange-400" />;
        case LocationType.PLC: return <Database size={14} className="text-mining-teal" />;
        case LocationType.PANEL: return <Layers size={14} className="text-mining-gold" />;
        case LocationType.JB: return <Box size={14} className="text-slate-500" />;
        case LocationType.RIO: return <Layers size={14} className="text-purple-400" />;
        default: return <Box size={14} />;
    }
};

const AssetTreeIcon = ({ type }: { type: AssetType }) => {
    switch (type) {
        case AssetType.MOTOR: return <Settings size={14} className="text-orange-500" />;
        case AssetType.VALVE: return <Activity size={14} className="text-slate-400" />;
        default: return <Cpu size={14} className="text-mining-teal" />;
    }
};

const FunctionalIcon = ({ type }: { type: string }) => {
    if (type === 'AREA') return <Factory size={14} className="text-mining-teal" />;
    if (type === 'SYSTEM') return <Cpu size={14} className="text-blue-400" />;
    return <Box size={14} />;
};

const WbsIcon = ({ type }: { type: string }) => {
    if (type === 'PACKAGE') return <ShoppingBag size={14} className="text-mining-gold" />;
    return <Box size={14} />;
}

// --- TREE NODE ---
interface TreeNodeProps {
    node: TreeNodeData;
    childrenNodes: (id: string) => TreeNodeData[];
    selectedId: string;
    onSelect: (id: string, node: TreeNodeData) => void;
    depth?: number;
    renderIcon: (node: TreeNodeData) => React.ReactNode;
    renderLabel?: (node: TreeNodeData) => React.ReactNode;
}

const TreeNode = ({
    node,
    childrenNodes,
    selectedId,
    onSelect,
    depth = 0,
    renderIcon,
    renderLabel
}: TreeNodeProps) => {
    const [isExpanded, setIsExpanded] = useState(true);

    const children = childrenNodes(node.id);
    const hasChildren = children && children.length > 0;
    const isSelected = selectedId === node.id;
    const isAsset = !!(node as Asset).tag;
    const isSignal = (node as Record<string, unknown>).type === 'SIGNAL';

    return (
        <div className="select-none">
            <div
                className={`group flex items-center py-1.5 px-2 mx-1 rounded-md cursor-pointer transition-all ${isSelected
                    ? 'bg-mining-teal/10 text-white border-l-2 border-mining-teal'
                    : 'text-slate-400 hover:bg-slate-800 hover:text-slate-200 border-l-2 border-transparent'
                    }`}
                style={{ paddingLeft: `${depth * 16 + 8}px` }}
                onClick={() => onSelect(node.id, node)}
            >
                {!isAsset && !isSignal && <GripVertical size={12} className="opacity-0 group-hover:opacity-30 mr-1 cursor-grab" />}

                <button
                    onClick={(e) => { e.stopPropagation(); setIsExpanded(!isExpanded); }}
                    className={`mr-1 p-0.5 rounded hover:bg-slate-700 text-slate-500 ${!hasChildren ? 'invisible' : ''}`}
                >
                    {isExpanded ? <ChevronDown size={12} /> : <ChevronRight size={12} />}
                </button>

                <div className="mr-2">{renderIcon(node)}</div>

                <span className={`text-xs truncate ${isAsset ? 'font-mono text-slate-300' : isSignal ? 'font-mono text-slate-500' : 'font-medium font-mono'}`}>
                    {renderLabel ? renderLabel(node) : (node as Record<string, unknown>).name as string}
                </span>
            </div>

            {isExpanded && hasChildren && (
                <div>
                    {children.map((child: TreeNodeData) => (
                        <TreeNode
                            key={child.id}
                            node={child}
                            childrenNodes={childrenNodes}
                            selectedId={selectedId}
                            onSelect={onSelect}
                            depth={depth + 1}
                            renderIcon={renderIcon}
                            renderLabel={renderLabel}
                        />
                    ))}
                </div>
            )}
        </div>
    );
};

interface ViewToggleProps {
    label: string;
    mode: 'LBS' | 'FBS' | 'WBS';
    current: 'LBS' | 'FBS' | 'WBS';
    set: (mode: 'LBS' | 'FBS' | 'WBS') => void;
}

const ViewToggle = ({ label, mode, current, set }: ViewToggleProps) => (
    <button onClick={() => set(mode)} className={`flex-1 py-1 text-xs font-medium rounded transition-all ${current === mode ? 'bg-slate-700 text-white shadow' : 'text-slate-500 hover:text-slate-300'}`}>
        {label}
    </button>
);

export const ExplorerSidebar: React.FC<ExplorerSidebarProps> = ({
    instruments, locations, viewMode, setViewMode, selectedId, onSelect, wbsTree: wbsTreeProp
}) => {
    // Defensive: ensure arrays
    const safeInstruments = Array.isArray(instruments) ? instruments : [];
    const safeLocations = Array.isArray(locations) ? locations : [];

    const [searchQuery, setSearchQuery] = useState('');

    const fbsTree = useMemo(() => Engine.getFBSTree(safeInstruments), [safeInstruments]);
    const wbsTree = wbsTreeProp || useMemo(() => Engine.getWBSTree(safeInstruments), [safeInstruments]);

    // --- TREE LOGIC ---
    const enrichWithSignals = (nodeId: string) => {
        const asset = safeInstruments.find(i => i.id === nodeId);
        if (asset) return Engine.getSignalNodes(asset, safeLocations);
        return [];
    };

    const getLBSChildrenWrapper = (parentId: string) => {
        const signalChildren = enrichWithSignals(parentId);
        if (signalChildren.length > 0) return signalChildren;

        // Defensive checks
        if (!Array.isArray(locations)) return [];
        if (!Array.isArray(instruments)) return [];

        const childLocs = locations.filter(l => l.parentId === parentId);
        let childAssets: TreeNodeData[] = [];
        if (parentId) childAssets = instruments.filter(i => i.locationId === parentId);
        return [...childLocs, ...childAssets];
    }

    const getFBSChildren = (parentId: string) => {
        const signalChildren = enrichWithSignals(parentId);
        if (signalChildren.length > 0) return signalChildren;

        if (!parentId) return fbsTree;
        const area = fbsTree.find(a => a.id === parentId);
        if (area) return area.children;

        const parentNodeIsSystem = fbsTree.some(a => a.children?.some((s: TreeNodeData) => s.id === parentId));
        if (parentNodeIsSystem) {
            let sysNode: TreeNodeData | null = null;
            fbsTree.forEach(a => {
                const s = a.children?.find((x: TreeNodeData) => x.id === parentId);
                if (s) sysNode = s;
            });
            if (sysNode) {
                const sn = sysNode as Record<string, unknown>;
                return instruments.filter(i => i.system === sn.originalSystem && i.area === sn.originalArea);
            }
        }
        return [];
    };

    const getWBSChildren = (parentId: string) => {
        const signalChildren = enrichWithSignals(parentId);
        if (signalChildren.length > 0) return signalChildren;

        if (!parentId) return wbsTree;
        const pkg = wbsTree.find(p => p.id === parentId);
        if (pkg) return instruments.filter(i => i.packageId === pkg.id);
        return [];
    };

    const renderTreeIcon = (node: TreeNodeData, defaultIcon: React.ReactNode) => {
        const n = node as Record<string, unknown>;
        if (n.type === 'SIGNAL') return <Zap size={14} className={String(n.name || '').includes('->') ? "text-green-400" : "text-slate-600"} />;
        if ((node as Asset).tag) return <AssetTreeIcon type={(node as Asset).type} />;
        return defaultIcon;
    }

    const renderTreeLabel = (node: TreeNodeData) => {
        const n = node as Record<string, unknown>;
        if ((node as Asset).tag) return <span className="flex justify-between w-full"><span>{(node as Asset).tag}</span> <span className="text-slate-600 ml-2 text-[10px] italic">{(node as Asset).system}</span></span>;
        if (n.type === 'SIGNAL' && String(n.name || '').includes('->')) {
            const parts = String(n.name || '').split('->');
            return <span>{parts[0]} <span className="text-green-500">→ {parts[1]}</span></span>
        }
        return String(n.name || '');
    }

    const handleSearch = (e: React.KeyboardEvent<HTMLInputElement>) => {
        if (e.key === 'Enter') {
            const term = searchQuery.toLowerCase();
            const match = instruments.find(i =>
                i.tag.toLowerCase().includes(term) ||
                i.description.toLowerCase().includes(term)
            );
            if (match) onSelect(match.id, match);
        }
    };

    return (
        <div className="w-80 flex flex-col border-r border-slate-800 bg-slate-950/50">
            <div className="p-4 border-b border-slate-800">
                <div className="flex bg-slate-900 p-1 rounded-lg border border-slate-800 mb-4">
                    <ViewToggle label="LBS" mode="LBS" current={viewMode} set={setViewMode} />
                    <ViewToggle label="FBS" mode="FBS" current={viewMode} set={setViewMode} />
                    <ViewToggle label="WBS" mode="WBS" current={viewMode} set={setViewMode} />
                </div>
                <div className="relative">
                    <Search className="absolute left-2 top-1/2 -translate-y-1/2 text-slate-500" size={14} />
                    <input
                        type="text"
                        placeholder="Search Tag (Press Enter)..."
                        className="w-full bg-slate-900 border border-slate-800 rounded pl-8 pr-2 py-1 text-xs text-slate-300 focus:ring-1 focus:ring-mining-teal outline-none"
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        onKeyDown={handleSearch}
                    />
                </div>
            </div>

            <div className="flex-1 overflow-y-auto p-2 custom-scrollbar">
                {viewMode === 'LBS' && (
                    <>
                        {locations.filter(l => !l.parentId).map(root => (
                            <TreeNode
                                key={root.id}
                                node={root}
                                childrenNodes={(pid: string) => getLBSChildrenWrapper(pid)}
                                selectedId={selectedId}
                                onSelect={onSelect}
                                renderIcon={(node: TreeNodeData) => renderTreeIcon(node, <LocationIcon type={(node as PhysicalLocation).type} />)}
                                renderLabel={(node: TreeNodeData) => renderTreeLabel(node)}
                            />
                        ))}
                        {instruments.some(i => !i.locationId) && (
                            <TreeNode
                                key="unassigned-root"
                                node={{ id: 'unassigned-root', name: 'Unassigned Assets', type: 'FOLDER' }}
                                childrenNodes={(pid: string) => pid === 'unassigned-root' ? instruments.filter(i => !i.locationId) : []}
                                selectedId={selectedId}
                                onSelect={onSelect}
                                renderIcon={() => <Box size={14} className="text-slate-500" />}
                                renderLabel={() => <span className="text-slate-400 italic">Unassigned Assets</span>}
                            />
                        )}
                    </>
                )}
                {viewMode === 'FBS' && fbsTree.map(root => (
                    <TreeNode
                        key={root.id}
                        node={root}
                        childrenNodes={(pid: string) => getFBSChildren(pid)}
                        selectedId={selectedId}
                        onSelect={onSelect}
                        renderIcon={(node: TreeNodeData) => renderTreeIcon(node, <FunctionalIcon type={(node as Record<string, unknown>).type as string} />)}
                        renderLabel={(node: TreeNodeData) => renderTreeLabel(node)}
                    />
                ))}
                {viewMode === 'WBS' && wbsTree.map(root => (
                    <TreeNode
                        key={root.id}
                        node={root}
                        childrenNodes={(pid: string) => getWBSChildren(pid)}
                        selectedId={selectedId}
                        onSelect={onSelect}
                        renderIcon={(node: TreeNodeData) => renderTreeIcon(node, <WbsIcon type={(node as Record<string, unknown>).type as string} />)}
                        renderLabel={(node: TreeNodeData) => renderTreeLabel(node)}
                    />
                ))}
            </div>
        </div>
    );
};
