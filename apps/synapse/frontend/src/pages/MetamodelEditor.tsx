import React, { useCallback, useEffect, useState, useMemo } from 'react';
import ReactFlow, {
    MiniMap,
    Controls,
    Background,
    useNodesState,
    useEdgesState,
    addEdge,
    Connection,
    Edge,
    Node,
    MarkerType,
    Panel,
    Handle,
    Position,
    ReactFlowInstance
} from 'reactflow';
import 'reactflow/dist/style.css';
import axios from 'axios';
import dagre from 'dagre';
import { Layers, Filter, Settings, Search, Layout, ZoomIn, ZoomOut, Database, Box, Activity, Zap, Cpu } from 'lucide-react';

import { API_URL } from '../../config';
import { useMetamodelStore } from '../store/useMetamodelStore';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';

// --- Types ---
type Discipline = 'PROCESS' | 'ELECTRICAL' | 'AUTOMATION' | 'MECHANICAL' | 'PROJECT' | 'PROCUREMENT' | 'GENERAL';
type ViewMode = 'DISCIPLINE' | 'FBS' | 'LBS' | 'ISA95' | 'PROCUREMENT';

interface MetamodelNodeData {
    id: string;
    name: string;
    node_type: string;
    discipline?: Discipline;
    semantic_type?: string;
    [key: string]: unknown;
}

interface MetamodelEdgeData {
    source_node_id: string;
    target_node_id: string;
    relation_type: string;
    [key: string]: unknown;
}

interface ActionLog {
    id: string;
    message: string;
    timestamp: string;
    entity_type?: string;
    [key: string]: unknown;
}

const DISCIPLINE_COLORS: Record<Discipline, string> = {
    PROCESS: '#3b82f6', // Blue
    ELECTRICAL: '#ef4444', // Red
    AUTOMATION: '#10b981', // Green
    MECHANICAL: '#f59e0b', // Orange
    PROJECT: '#8b5cf6', // Purple
    PROCUREMENT: '#d946ef', // Pink
    GENERAL: '#64748b', // Slate
};

export default function MetamodelEditor() {
    // --- State ---
    const [nodes, setNodes, onNodesChange] = useNodesState([]);
    const [edges, setEdges, onEdgesChange] = useEdgesState([]);
    const [rawNodes, setRawNodes] = useState<MetamodelNodeData[]>([]);
    const [rawEdges, setRawEdges] = useState<MetamodelEdgeData[]>([]);
    const [logs, setLogs] = useState<ActionLog[]>([]);
    const [rfInstance, setRfInstance] = useState<ReactFlowInstance | null>(null);

    const { highlightedNodeId, setHighlightedNodeId } = useMetamodelStore();

    // Controls
    const [viewMode, setViewMode] = useState<ViewMode>('DISCIPLINE');
    const [lod, setLod] = useState<number>(3); // 1=Macro, 3=Detail
    const [activeDisciplines, setActiveDisciplines] = useState<Record<Discipline, boolean>>({
        PROCESS: true, ELECTRICAL: true, AUTOMATION: true, MECHANICAL: true, PROJECT: true, PROCUREMENT: true, GENERAL: true
    });
    const [searchTerm, setSearchTerm] = useState('');

    // --- Fetch Data ---
    const fetchGraph = async () => {
        try {
            const res = await axios.get(`${API_URL}/api/v1/metamodel/graph`);
            setRawNodes(res.data.nodes);
            setRawEdges(res.data.edges);
        } catch (err) {
            console.error("Failed to fetch graph", err);
        }
    };

    const fetchLogs = async () => {
        try {
            const res = await axios.get(`${API_URL}/api/v1/mock/logs`);
            setLogs(res.data);
        } catch (err) {
            console.error("Failed to fetch logs", err);
        }
    };

    useEffect(() => {
        fetchGraph();
        const interval = setInterval(fetchLogs, 2000); // Poll logs every 2s
        return () => clearInterval(interval);
    }, []);

    // --- Graph Sync Effect ---
    useEffect(() => {
        if (highlightedNodeId && rfInstance && nodes.length > 0) {
            const node = nodes.find(n => n.id === highlightedNodeId);
            if (node) {
                // Center and zoom to the node
                rfInstance.setCenter(node.position.x + 90, node.position.y + 25, { zoom: 1.5, duration: 800 });

                // Highlight visually (optional: could update node style here)
                setNodes(nds => nds.map(n => {
                    if (n.id === highlightedNodeId) {
                        return {
                            ...n,
                            style: { ...n.style, boxShadow: '0 0 20px 5px #facc15', borderColor: '#facc15' }
                        };
                    }
                    return n;
                }));

                // Reset highlight after a delay or keep it? 
                // Let's keep it until another action or manual reset.
            }
        }
    }, [highlightedNodeId, rfInstance, nodes.length, setNodes]);

    // --- Layout Strategy ---
    const getLayoutedElements = useCallback((nodes: Node<MetamodelNodeData>[], edges: Edge<MetamodelEdgeData>[], mode: ViewMode) => {
        const dagreGraph = new dagre.graphlib.Graph({ compound: true });
        dagreGraph.setDefaultEdgeLabel(() => ({}));

        // Adaptive Layout Settings
        let rankdir = 'LR'; // Default Flow
        let nodesep = 50;
        let ranksep = 50;

        if (mode === 'ISA95' || mode === 'LBS' || mode === 'FBS') {
            rankdir = 'TB'; // Hierarchy
            nodesep = 80;
            ranksep = 80;
        }

        dagreGraph.setGraph({ rankdir, nodesep, ranksep });

        // Add Nodes
        nodes.forEach((node) => {
            const width = (node.data?.width as number) || (node.style?.width as number) || 180;
            dagreGraph.setNode(node.id, { width, height: 50 });
        });

        // Add Edges
        edges.forEach((edge) => {
            dagreGraph.setEdge(edge.source, edge.target);
        });

        dagre.layout(dagreGraph);

        const layoutedNodes = nodes.map((node) => {
            const nodeWithPosition = dagreGraph.node(node.id);
            const width = (node.data?.width as number) || (node.style?.width as number) || 180;
            return {
                ...node,
                position: {
                    x: nodeWithPosition.x - width / 2,
                    y: nodeWithPosition.y - 25,
                },
            };
        });

        return { nodes: layoutedNodes, edges };
    }, []);

    // --- Processing Loop ---
    useEffect(() => {
        if (rawNodes.length === 0) return;

        // 1. Filter Nodes
        const filteredNodes = rawNodes.filter(n => {
            const lod_level = (n.lod as number) || 3;
            if (lod_level > lod) return false;
            if (!activeDisciplines[n.discipline as Discipline]) return false;
            if (searchTerm && !n.name.toLowerCase().includes(searchTerm.toLowerCase())) return false;
            return true;
        });

        // 2. Filter Edges
        const nodeIds = new Set(filteredNodes.map(n => n.id));
        const filteredEdges = rawEdges.filter(e =>
            nodeIds.has(e.source_node_id) && nodeIds.has(e.target_node_id) &&
            activeDisciplines[e.discipline as Discipline]
        );

        // 3. Map to React Flow
        const flowNodes = filteredNodes.map(n => {
            // Adaptive Styling
            let shapeStyle = {};
            if (n.semantic_type === 'CONTAINER') {
                shapeStyle = { borderStyle: 'dashed', backgroundColor: 'rgba(30, 41, 59, 0.5)' };
            }

            return {
                id: n.id,
                data: { label: n.name, ...n },
                style: {
                    background: '#1e293b',
                    color: '#f8fafc',
                    border: `2px solid ${DISCIPLINE_COLORS[n.discipline as Discipline] || '#64748b'}`,
                    borderRadius: n.semantic_type === 'ASSET' ? '8px' : '4px',
                    padding: '10px',
                    width: 180,
                    fontSize: '12px',
                    fontWeight: 'bold',
                    boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
                    ...shapeStyle
                },
                position: { x: 0, y: 0 }
            };
        });

        const flowEdges = filteredEdges.map(e => {
            const disciplineColor = DISCIPLINE_COLORS[(e.discipline as Discipline) || 'GENERAL'];
            const isPropagated = (e.propagates as boolean) === true;
            return {
                id: String(e.id),
                source: String(e.source_node_id),
                target: String(e.target_node_id),
                label: e.relation_type,
                type: 'smoothstep',
                animated: isPropagated || false,
                style: { stroke: disciplineColor, strokeWidth: 2 },
                labelStyle: { fill: disciplineColor, fontWeight: 600 },
                markerEnd: { type: MarkerType.ArrowClosed, color: disciplineColor },
            };
        });

        // 4. Apply Layout
        const { nodes: layoutedNodes, edges: layoutedEdges } = getLayoutedElements(
            flowNodes,
            flowEdges,
            viewMode
        );

        setNodes(layoutedNodes);
        setEdges(layoutedEdges);

    }, [rawNodes, rawEdges, lod, activeDisciplines, searchTerm, viewMode, getLayoutedElements]);

    // --- Handlers ---
    const onConnect = useCallback(async (params: Connection) => {
        const relationType = prompt("Enter relationship type:", "connected_to");
        if (!relationType) return;
        try {
            await axios.post(`${API_URL}/api/v1/metamodel/edge`, {
                source_node_id: params.source,
                target_node_id: params.target,
                relation_type: relationType,
                discipline: 'GENERAL'
            });
            fetchGraph();
        } catch (err) { console.error(err); }
    }, []);

    const seedGraph = async () => {
        if (confirm("Reset and seed default engineering rules?")) {
            await axios.post(`${API_URL}/api/v1/metamodel/seed`);
            fetchGraph();
        }
    }

    // --- UI Components ---
    return (
        <div className="flex h-[calc(100vh-4rem)] bg-slate-950 text-slate-200">
            {/* Left Sidebar: Layers */}
            <div className="w-64 border-r border-slate-800 p-4 flex flex-col gap-6 bg-slate-900/50">
                <div>
                    <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-3 flex items-center gap-2">
                        <Layers size={14} /> Perspectives
                    </h3>
                    <div className="space-y-1">
                        {[
                            { id: 'DISCIPLINE', label: 'Discipline Flow', icon: Activity },
                            { id: 'ISA95', label: 'ISA95 Hierarchy', icon: Database },
                            { id: 'LBS', label: 'Physical (LBS)', icon: Box },
                            { id: 'FBS', label: 'Functional (FBS)', icon: Cpu },
                        ].map(mode => (
                            <Button
                                key={mode.id}
                                onClick={() => setViewMode(mode.id as ViewMode)}
                                variant={viewMode === mode.id ? 'secondary' : 'ghost'}
                                className={`w-full justify-start ${viewMode === mode.id ? 'bg-mining-teal/20 text-mining-teal border-mining-teal/30' : 'text-slate-400'}`}
                                leftIcon={<mode.icon size={14} />}
                            >
                                {mode.label}
                            </Button>
                        ))}
                    </div>
                </div>

                <div>
                    <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-3 flex items-center gap-2">
                        <Settings size={14} /> Actions
                    </h3>
                    <Button
                        onClick={seedGraph}
                        variant="outline"
                        className="w-full justify-center"
                        leftIcon={<Database size={14} />}
                    >
                        Reset / Seed
                    </Button>
                </div>

                <div>
                    <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-3 flex items-center gap-2">
                        <Filter size={14} /> Disciplines
                    </h3>
                    <div className="space-y-2">
                        {Object.keys(DISCIPLINE_COLORS).map((disc) => (
                            <label key={disc} className="flex items-center gap-2 cursor-pointer group">
                                <div className={`w-4 h-4 rounded border flex items-center justify-center transition-colors ${activeDisciplines[disc as Discipline]
                                    ? 'bg-slate-800 border-slate-600'
                                    : 'bg-transparent border-slate-700'
                                    }`}>
                                    {activeDisciplines[disc as Discipline] && (
                                        <div className="w-2 h-2 rounded-full" style={{ backgroundColor: DISCIPLINE_COLORS[disc as Discipline] }} />
                                    )}
                                </div>
                                <input
                                    type="checkbox"
                                    className="hidden"
                                    checked={activeDisciplines[disc as Discipline]}
                                    onChange={() => setActiveDisciplines(prev => ({ ...prev, [disc]: !prev[disc as Discipline] }))}
                                />
                                <span className={`text-sm ${activeDisciplines[disc as Discipline] ? 'text-slate-200' : 'text-slate-500'}`}>
                                    {disc.charAt(0) + disc.slice(1).toLowerCase()}
                                </span>
                            </label>
                        ))}
                    </div>
                </div>
            </div>

            {/* Main Canvas */}
            <div className="flex-1 relative">
                <ReactFlow
                    nodes={nodes}
                    edges={edges}
                    onNodesChange={onNodesChange}
                    onEdgesChange={onEdgesChange}
                    onConnect={onConnect}
                    onInit={setRfInstance}
                    fitView
                    className="bg-slate-950"
                >
                    <Background color="#334155" gap={20} size={1} />
                    <Controls className="bg-slate-800 border-slate-700 fill-slate-400" />
                    <Panel position="top-center" className="bg-slate-900/80 backdrop-blur p-2 rounded-lg border border-slate-700 flex gap-4 shadow-xl">
                        <div className="flex items-center gap-2 border-r border-slate-700 pr-4">
                            <Search size={16} className="text-slate-400" />
                            <input
                                type="text"
                                placeholder="Search nodes..."
                                className="bg-transparent border-none outline-none text-sm w-32 text-white placeholder-slate-500"
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                            />
                        </div>
                        <div className="flex items-center gap-2">
                            <span className="text-xs text-slate-400 font-mono">LOD:</span>
                            <input
                                type="range" min="1" max="3" step="1"
                                value={lod}
                                onChange={(e) => setLod(parseInt(e.target.value))}
                                className="w-24 accent-mining-teal"
                            />
                            <Badge variant="outline" className="text-xs font-bold text-mining-teal border-mining-teal/30 bg-mining-teal/10">
                                {lod === 1 ? 'MACRO' : lod === 2 ? 'EQUIP' : 'DETAIL'}
                            </Badge>
                        </div>
                    </Panel>

                    {/* Legend Panel */}
                    <Panel position="bottom-right" className="bg-slate-900/80 backdrop-blur p-3 rounded-lg border border-slate-700">
                        <div className="text-xs font-bold text-slate-500 mb-2">LEGEND</div>
                        <div className="flex flex-col gap-1">
                            <div className="flex items-center gap-2"><div className="w-3 h-3 rounded-full bg-blue-500"></div><span className="text-xs text-slate-300">Process</span></div>
                            <div className="flex items-center gap-2"><div className="w-3 h-3 rounded-full bg-red-500"></div><span className="text-xs text-slate-300">Electrical</span></div>
                            <div className="flex items-center gap-2"><div className="w-3 h-3 rounded-full bg-green-500"></div><span className="text-xs text-slate-300">Automation</span></div>
                        </div>
                    </Panel>
                </ReactFlow>
            </div>

            {/* Right Sidebar Removed as per user request */}
        </div>
    );
}
