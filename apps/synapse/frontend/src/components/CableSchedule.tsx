import React, { useMemo } from 'react';
import { Asset, PhysicalLocation } from '../../types';
import { CabinetPlanner as Engine } from '../services/engineeringEngine';
import { FileDown } from 'lucide-react';

interface CableScheduleProps {
  instruments: Asset[];
  locations: PhysicalLocation[];
}

export const CableSchedule: React.FC<CableScheduleProps> = ({ instruments, locations }) => {

  // Real-time calculation of cables based on rules
  const cables = useMemo(() => {
    return Engine.generateCableSchedule(instruments, locations);
  }, [instruments, locations]);

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-xl font-bold text-white">Automated Cable Schedule</h2>
          <p className="text-sm text-slate-400">Generated via Rule Engine (Inst → JB, JB → PLC)</p>
        </div>
        <button className="flex items-center px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-sm font-medium transition-colors">
          <FileDown size={16} className="mr-2" />
          Export to Excel
        </button>
      </div>

      <div className="bg-slate-900 rounded-xl border border-slate-800 overflow-hidden shadow-lg">
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left text-slate-300">
            <thead className="text-xs uppercase bg-slate-950 text-slate-400 font-mono">
              <tr>
                <th className="px-6 py-3">Cable Tag</th>
                <th className="px-6 py-3">From (Source)</th>
                <th className="px-6 py-3">To (Dest)</th>
                <th className="px-6 py-3">Type</th>
                <th className="px-6 py-3">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {cables.map((cable) => (
                <tr key={cable.id} className="hover:bg-slate-800/50 transition-colors">
                  <td className="px-6 py-3 font-mono font-bold text-white">{cable.tag}</td>
                  <td className="px-6 py-3">
                    <div className="flex flex-col">
                      <span className="text-white">{cable.fromName}</span>
                      <span className="text-xs text-slate-500 font-mono">{cable.fromId}</span>
                    </div>
                  </td>
                  <td className="px-6 py-3">
                    <div className="flex flex-col">
                      <span className="text-white">{cable.toName}</span>
                      <span className="text-xs text-slate-500 font-mono">{cable.toId}</span>
                    </div>
                  </td>
                  <td className="px-6 py-3">
                    <span className={`text-xs px-2 py-1 rounded-full border ${cable.type === 'HOMERUN'
                        ? 'bg-purple-500/10 text-purple-400 border-purple-500/20'
                        : 'bg-slate-700 text-slate-300 border-slate-600'
                      }`}>
                      {cable.type}
                    </span>
                  </td>
                  <td className="px-6 py-3">
                    <span className="text-green-500 text-xs font-mono flex items-center">
                      ● READY
                    </span>
                  </td>
                </tr>
              ))}
              {cables.length === 0 && (
                <tr>
                  <td colSpan={5} className="px-6 py-12 text-center text-slate-500">
                    No cables generated. Ensure instruments are linked to Locations in the Tag Manager.
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