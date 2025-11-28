
import React, { useState, useEffect, useMemo } from 'react';
import { Asset, AssetType, IOType, PhysicalLocation } from '../../types';
import { CabinetPlanner as Engine } from '../services/engineeringEngine';
import { Settings, Cpu, Zap, ShoppingCart, FileText, Box, MapPin, Factory, ArrowRight, Network, Activity, Cable } from 'lucide-react';

interface AssetDetailsProps {
    asset: Asset;
    locations: PhysicalLocation[]; // Needed to resolve connection names
    onNavigate?: (viewMode: 'LBS' | 'FBS' | 'WBS', nodeId: string) => void;
    initialTab?: 'SPECS' | 'WIRING' | 'PURCHASE' | 'DOCS';
}

export const AssetDetails: React.FC<AssetDetailsProps> = ({ asset, locations, onNavigate, initialTab = 'SPECS' }) => {
    const [activeTab, setActiveTab] = useState<'SPECS' | 'WIRING' | 'PURCHASE' | 'DOCS'>(initialTab);

    // Sync active tab if initialTab changes (e.g. selecting a signal vs an asset in the tree)
    useEffect(() => {
        setActiveTab(initialTab);
    }, [initialTab, asset.id]);

    const getIcon = () => {
        if (asset.type === AssetType.MOTOR) return <Settings size={24} className="text-orange-400" />;
        if (asset.type === AssetType.VALVE) return <Box size={24} className="text-slate-400" />;
        return <Cpu size={24} className="text-mining-teal" />;
    };

    // construct IDs based on EngineeringEngine logic
    const fbsId = `sys-${asset.area}-${asset.system}`;
    const wbsId = asset.purchasing?.workPackageId ? `pkg-${asset.purchasing.workPackageId}` : null;
    const lbsId = asset.locationId;

    // Calculate Cable for Wiring Tab
    const connectionInfo = useMemo(() => {
        const cables = Engine.generateCableSchedule([asset], locations);
        const myCable = cables.find(c => c.fromId === asset.id);
        const destination = locations.find(l => l.id === asset.locationId);
        return { cable: myCable, destination };
    }, [asset, locations]);

    return (
        <div className="h-full flex flex-col bg-slate-900">
            {/* Header */}
            <div className="p-6 border-b border-slate-800 bg-slate-950/30">
                <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-4">
                        <div className="p-3 bg-slate-900 rounded border border-slate-800 shadow-lg">
                            {getIcon()}
                        </div>
                        <div>
                            <div className="flex items-center gap-2">
                                <h2 className="text-2xl font-bold text-white font-mono tracking-wide">{asset.tag}</h2>
                                <span className="text-xs px-2 py-1 bg-slate-800 rounded text-slate-400 border border-slate-700">{asset.type}</span>
                            </div>
                            <p className="text-slate-400">{asset.description}</p>
                        </div>
                    </div>
                    <div className="text-right text-xs font-mono text-slate-500">
                        <div className="bg-slate-900 px-2 py-1 rounded border border-slate-800 mb-1">{asset.id}</div>
                    </div>
                </div>

                {/* Context Navigation Bar */}
                {onNavigate && (
                    <div className="flex flex-wrap gap-2 text-xs font-medium">
                        {/* LBS Link */}
                        <button
                            onClick={() => lbsId && onNavigate('LBS', lbsId)}
                            disabled={!lbsId}
                            className={`flex items-center gap-2 px-3 py-1.5 rounded-full border transition-all ${lbsId
                                ? 'bg-slate-900 border-slate-700 text-blue-400 hover:border-blue-500 hover:bg-slate-800'
                                : 'bg-slate-900/50 border-transparent text-slate-600 cursor-not-allowed'
                                }`}
                        >
                            <MapPin size={12} />
                            {lbsId ? `Loc: ${lbsId}` : 'No Location'}
                            {lbsId && <ArrowRight size={12} className="opacity-50" />}
                        </button>

                        {/* FBS Link */}
                        <button
                            onClick={() => onNavigate('FBS', fbsId)}
                            className="flex items-center gap-2 px-3 py-1.5 rounded-full border bg-slate-900 border-slate-700 text-mining-teal hover:border-mining-teal hover:bg-slate-800 transition-all"
                        >
                            <Factory size={12} />
                            Sys: {asset.system}
                            <ArrowRight size={12} className="opacity-50" />
                        </button>

                        {/* WBS Link */}
                        <button
                            onClick={() => wbsId && onNavigate('WBS', wbsId)}
                            disabled={!wbsId}
                            className={`flex items-center gap-2 px-3 py-1.5 rounded-full border transition-all ${wbsId
                                ? 'bg-slate-900 border-slate-700 text-mining-gold hover:border-mining-gold hover:bg-slate-800'
                                : 'bg-slate-900/50 border-transparent text-slate-600 cursor-not-allowed'
                                }`}
                        >
                            <ShoppingCart size={12} />
                            Pkg: {asset.purchasing?.workPackageId || 'None'}
                            {wbsId && <ArrowRight size={12} className="opacity-50" />}
                        </button>
                    </div>
                )}
            </div>

            {/* Tabs */}
            <div className="flex items-center px-6 border-b border-slate-800 bg-slate-900">
                <button onClick={() => setActiveTab('SPECS')} className={`px-4 py-3 text-sm font-medium border-b-2 transition-colors ${activeTab === 'SPECS' ? 'border-mining-teal text-white' : 'border-transparent text-slate-400'}`}>Specifications</button>
                <button onClick={() => setActiveTab('WIRING')} className={`px-4 py-3 text-sm font-medium border-b-2 transition-colors ${activeTab === 'WIRING' ? 'border-mining-teal text-white' : 'border-transparent text-slate-400'}`}>Wiring & Loop</button>
                <button onClick={() => setActiveTab('PURCHASE')} className={`px-4 py-3 text-sm font-medium border-b-2 transition-colors ${activeTab === 'PURCHASE' ? 'border-mining-teal text-white' : 'border-transparent text-slate-400'}`}>Procurement</button>
                <button onClick={() => setActiveTab('DOCS')} className={`px-4 py-3 text-sm font-medium border-b-2 transition-colors ${activeTab === 'DOCS' ? 'border-mining-teal text-white' : 'border-transparent text-slate-400'}`}>Documents</button>
            </div>

            {/* Content */}
            <div className="flex-1 p-6 overflow-y-auto custom-scrollbar">

                {activeTab === 'SPECS' && (
                    <div className="space-y-6">

                        {/* Process Data */}
                        {asset.process && (
                            <div className="bg-slate-950 rounded border border-slate-800 overflow-hidden">
                                <div className="bg-slate-900 px-4 py-2 border-b border-slate-800 flex items-center gap-2 text-blue-400 font-bold text-sm uppercase">
                                    <FileText size={14} /> Process Conditions
                                </div>
                                <div className="p-4 grid grid-cols-2 gap-4 text-sm">
                                    <DetailRow label="Service Fluid" value={asset.process.fluid} />
                                    <DetailRow label="Calibrated Range" value={`${asset.process.minRange} - ${asset.process.maxRange} ${asset.process.units}`} />
                                    <DetailRow label="Operational Setpoint" value={asset.process.setpoint} />
                                </div>
                            </div>
                        )}

                        {/* Electrical Data */}
                        {asset.electrical && (
                            <div className="bg-slate-950 rounded border border-slate-800 overflow-hidden">
                                <div className="bg-slate-900 px-4 py-2 border-b border-slate-800 flex items-center gap-2 text-mining-gold font-bold text-sm uppercase">
                                    <Zap size={14} /> Electrical Spec
                                </div>
                                <div className="p-4 grid grid-cols-2 gap-4 text-sm">
                                    <DetailRow label="Voltage" value={asset.electrical.voltage} />
                                    <DetailRow label="Rated Power" value={`${asset.electrical.powerKW} kW`} />
                                    <DetailRow label="Load Type" value={asset.electrical.loadType} />
                                    <DetailRow label="Fed From" value={asset.electrical.mccId} mono />
                                </div>
                            </div>
                        )}

                        {/* Mechanical Data */}
                        {asset.mechanical && (
                            <div className="bg-slate-950 rounded border border-slate-800 overflow-hidden">
                                <div className="bg-slate-900 px-4 py-2 border-b border-slate-800 flex items-center gap-2 text-slate-300 font-bold text-sm uppercase">
                                    <Settings size={14} /> Mechanical Spec
                                </div>
                                <div className="p-4 grid grid-cols-2 gap-4 text-sm">
                                    <DetailRow label="Model No." value={asset.mechanical.modelNo} />
                                    <DetailRow label="Weight" value={`${asset.mechanical.weightKg} kg`} />
                                    <DetailRow label="Housing Material" value={asset.mechanical.material} />
                                </div>
                            </div>
                        )}

                        {/* Automation Data */}
                        <div className="bg-slate-950 rounded border border-slate-800 overflow-hidden">
                            <div className="bg-slate-900 px-4 py-2 border-b border-slate-800 flex items-center gap-2 text-mining-teal font-bold text-sm uppercase">
                                <Cpu size={14} /> Automation & Control
                            </div>
                            <div className="p-4 grid grid-cols-2 gap-4 text-sm">
                                <DetailRow label="I/O Type" value={asset.ioType} mono />
                                <DetailRow label="Linked Node" value={asset.locationId || 'Unassigned'} mono />
                            </div>
                        </div>

                    </div>
                )}

                {activeTab === 'WIRING' && (
                    <div className="space-y-6">
                        <div className="bg-slate-950 rounded border border-slate-800 overflow-hidden p-6">
                            <h3 className="text-white font-bold mb-6 flex items-center gap-2">
                                <Network size={18} className="text-mining-teal" /> Instrument Loop Diagram
                            </h3>

                            {connectionInfo.destination ? (
                                <div className="flex items-center justify-between max-w-3xl mx-auto">
                                    {/* Source Asset */}
                                    <div className="flex flex-col items-center gap-3 group">
                                        <div className="w-16 h-16 rounded-full bg-slate-900 border-2 border-slate-700 flex items-center justify-center shadow-lg z-10">
                                            {getIcon()}
                                        </div>
                                        <div className="text-center">
                                            <div className="font-mono font-bold text-white text-sm">{asset.tag}</div>
                                            <div className="text-xs text-slate-500 uppercase">Field Device</div>
                                        </div>
                                    </div>

                                    {/* Connection Line (Cable) */}
                                    <div className="flex-1 h-0.5 bg-slate-700 relative mx-4">
                                        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-slate-950 border border-slate-700 rounded px-3 py-1 text-xs font-mono text-green-400 flex items-center gap-2 shadow-sm whitespace-nowrap">
                                            <Cable size={12} />
                                            {connectionInfo.cable?.tag || 'AUTO-GEN'}
                                        </div>
                                    </div>

                                    {/* Destination Node */}
                                    <div
                                        className="flex flex-col items-center gap-3 group cursor-pointer hover:opacity-80 transition-opacity"
                                        onClick={() => connectionInfo.destination && onNavigate && onNavigate('LBS', connectionInfo.destination.id)}
                                    >
                                        <div className="w-16 h-16 rounded bg-slate-900 border-2 border-slate-700 flex items-center justify-center shadow-lg z-10 group-hover:border-mining-teal transition-colors">
                                            <Box size={24} className="text-slate-300" />
                                        </div>
                                        <div className="text-center">
                                            <button
                                                onClick={(e) => {
                                                    e.stopPropagation();
                                                    connectionInfo.destination && onNavigate && onNavigate('LBS', connectionInfo.destination.id);
                                                }}
                                                className="font-mono font-bold text-mining-teal text-sm hover:underline cursor-pointer transition-all flex items-center gap-1"
                                            >
                                                {connectionInfo.destination.name}
                                                <ArrowRight size={10} />
                                            </button>
                                            <div className="text-xs text-slate-500 uppercase">Termination</div>
                                        </div>
                                    </div>
                                </div>
                            ) : (
                                <div className="text-center py-12 text-slate-500 bg-slate-900/50 rounded border border-dashed border-slate-800">
                                    <Activity size={32} className="mx-auto mb-2 opacity-20" />
                                    <p>No Physical Link Defined</p>
                                    <p className="text-xs mt-1">Assign a location in the Grid or Tag Manager to generate a loop.</p>
                                </div>
                            )}
                        </div>

                        {connectionInfo.cable && (
                            <div className="bg-slate-950 rounded border border-slate-800 overflow-hidden">
                                <div className="bg-slate-900 px-4 py-2 border-b border-slate-800 flex items-center gap-2 text-green-400 font-bold text-sm uppercase">
                                    <Cable size={14} /> Cable Schedule Properties
                                </div>
                                <div className="p-4 grid grid-cols-2 gap-4 text-sm">
                                    <DetailRow label="Cable Tag" value={connectionInfo.cable.tag} mono />
                                    <DetailRow label="Cable Type" value={connectionInfo.cable.type} />
                                    <DetailRow label="Source" value={connectionInfo.cable.fromName} />
                                    <DetailRow label="Destination" value={connectionInfo.cable.toName} />
                                </div>
                            </div>
                        )}
                    </div>
                )}

                {activeTab === 'PURCHASE' && (
                    <div className="bg-slate-950 rounded border border-slate-800 overflow-hidden">
                        <div className="bg-slate-900 px-4 py-2 border-b border-slate-800 flex items-center gap-2 text-green-400 font-bold text-sm uppercase">
                            <ShoppingCart size={14} /> Procurement Status
                        </div>
                        <div className="p-4 grid grid-cols-1 gap-4 text-sm">
                            <DetailRow label="Work Package" value={asset.purchasing?.workPackageId} mono />
                            <DetailRow label="PO Number" value={asset.purchasing?.poNumber || 'Pending'} />
                            <div className="flex justify-between py-2 border-b border-slate-800/50">
                                <span className="text-slate-500">Current Status</span>
                                <span className={`px-2 py-0.5 rounded text-xs border ${asset.purchasing?.status === 'Ordered' ? 'bg-green-900 text-green-400 border-green-700' :
                                    asset.purchasing?.status === 'Engineering' ? 'bg-blue-900 text-blue-400 border-blue-700' :
                                        'bg-slate-800 text-slate-400 border-slate-700'
                                    }`}>
                                    {asset.purchasing?.status || 'Unknown'}
                                </span>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

const DetailRow = ({ label, value, mono }: { label: string, value?: string | number, mono?: boolean }) => (
    <div className="flex justify-between py-2 border-b border-slate-800/50 last:border-0">
        <span className="text-slate-500">{label}</span>
        <span className={`text-slate-200 ${mono ? 'font-mono text-xs' : ''}`}>{value || '-'}</span>
    </div>
);
