import React, { useState, useMemo } from 'react';
import { Asset, IOType, PhysicalLocation, LocationType, AssetType } from '../../types';
import { classifyInstrument } from '../services/aiService';
import { Sparkles, Plus, Cpu, Network } from 'lucide-react';

interface TagManagerProps {
  instruments: Asset[];
  locations: PhysicalLocation[];
  onUpdateInstruments: (insts: Asset[]) => void;
}

export const TagManager: React.FC<TagManagerProps> = ({ instruments, locations, onUpdateInstruments }) => {
  const [isAnalysing, setIsAnalysing] = useState(false);

  // Mock function to simulate adding a raw tag from P&ID
  const handleAddRawTag = () => {
    const newTag: Asset = {
      id: Math.random().toString(36).substr(2, 9),
      tag: `FIT-${Math.floor(Math.random() * 900) + 100}`,
      description: "New Flow Transmitter Ball Mill Discharge",
      type: AssetType.INSTRUMENT,
      area: "310",
      system: "Unclassified", // To be filled by AI
      ioType: IOType.AI,
      process: { fluid: "Slurry" }
    };
    onUpdateInstruments([...instruments, newTag]);
  };

  const handleAutoClassify = async () => {
    setIsAnalysing(true);
    const updates = await Promise.all(instruments.map(async (inst) => {
      if (inst.system === 'Unclassified' || inst.area === '000') {
        const prediction = await classifyInstrument(inst.tag, inst.description);
        return { ...inst, ...prediction };
      }
      return inst;
    }));
    onUpdateInstruments(updates);
    setIsAnalysing(false);
  };

  const handleLocationLink = (instId: string, locId: string) => {
    const updated = instruments.map(i => i.id === instId ? { ...i, locationId: locId } : i);
    onUpdateInstruments(updated);
  };

  // Helper to build breadcrumb path for location dropdown
  // e.g. "E-House 01 > Room 02 > PLC 01"
  const getLocationPath = (locId: string): string => {
    const loc = locations.find(l => l.id === locId);
    if (!loc) return '';
    const parentPath = loc.parentId ? getLocationPath(loc.parentId) : '';
    return parentPath ? `${parentPath} > ${loc.name}` : loc.name;
  };

  // Filter valid targets for direct instrument connection
  // These are the "terminatable" locations where a wire lands.
  const validTargets = useMemo(() => {
    return locations.filter(l =>
      l.type === LocationType.JB ||
      l.type === LocationType.PANEL ||
      l.type === LocationType.RIO ||
      l.type === LocationType.PLC ||
      l.type === LocationType.MCC
    ).map(l => ({
      ...l,
      fullPath: getLocationPath(l.id)
    })).sort((a, b) => a.fullPath.localeCompare(b.fullPath));
  }, [locations]);

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center bg-slate-800/50 p-4 rounded-xl border border-slate-700">
        <div>
          <h2 className="text-xl font-bold text-white">Functional Breakdown (FBS)</h2>
          <p className="text-sm text-slate-400">Ingest P&ID data and organize by Area/System.</p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={handleAddRawTag}
            className="flex items-center px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg text-sm font-medium transition-colors"
          >
            <Plus size={16} className="mr-2" />
            Simulate P&ID Ingest
          </button>
          <button
            onClick={handleAutoClassify}
            disabled={isAnalysing}
            className="flex items-center px-4 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 rounded-lg text-sm font-medium transition-colors shadow-lg shadow-indigo-900/20"
          >
            <Sparkles size={16} className={`mr-2 ${isAnalysing ? 'animate-spin' : ''}`} />
            {isAnalysing ? 'AI Processing...' : 'AI Auto-Classify'}
          </button>
        </div>
      </div>

      <div className="bg-slate-900 rounded-xl border border-slate-800 overflow-hidden shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left text-slate-300">
            <thead className="text-xs uppercase bg-slate-950 text-slate-400">
              <tr>
                <th className="px-6 py-3 font-mono">Tag</th>
                <th className="px-6 py-3">Description</th>
                <th className="px-6 py-3">Area</th>
                <th className="px-6 py-3">System</th>
                <th className="px-6 py-3">I/O Type</th>
                <th className="px-6 py-3 bg-slate-900 border-l border-slate-800 text-mining-teal">
                  LBS Link (Grid Routing)
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {instruments.map((inst) => (
                <tr key={inst.id} className="hover:bg-slate-800/50 transition-colors group">
                  <td className="px-6 py-3 font-mono font-medium text-white">{inst.tag}</td>
                  <td className="px-6 py-3 max-w-xs truncate">{inst.description}</td>
                  <td className="px-6 py-3 font-mono text-slate-400">{inst.area}</td>
                  <td className="px-6 py-3">
                    <span className={`px-2 py-1 rounded text-xs font-medium border ${inst.system === 'Unclassified'
                      ? 'bg-red-500/10 text-red-400 border-red-500/20'
                      : 'bg-blue-500/10 text-blue-400 border-blue-500/20'
                      }`}>
                      {inst.system}
                    </span>
                  </td>
                  <td className="px-6 py-3 font-mono text-xs">{inst.ioType}</td>
                  <td className="px-6 py-3 border-l border-slate-800 bg-slate-900/30">
                    <div className="flex items-center gap-2">
                      <Network size={14} className="text-slate-500 flex-shrink-0" />
                      <select
                        className="bg-slate-950 border border-slate-700 rounded text-xs py-1.5 px-2 focus:ring-1 focus:ring-mining-teal outline-none w-full max-w-xs truncate font-mono"
                        value={inst.locationId || ''}
                        onChange={(e) => handleLocationLink(inst.id, e.target.value)}
                      >
                        <option value="">-- Unlinked --</option>
                        {validTargets.map(loc => (
                          <option key={loc.id} value={loc.id}>
                            {loc.fullPath}
                          </option>
                        ))}
                      </select>
                    </div>
                  </td>
                </tr>
              ))}
              {instruments.length === 0 && (
                <tr>
                  <td colSpan={6} className="px-6 py-8 text-center text-slate-500">
                    No instruments loaded. Click "Simulate P&ID Ingest" to start.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};