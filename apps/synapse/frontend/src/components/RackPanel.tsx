
import React, { useMemo, useState } from 'react';
import { Asset, PhysicalLocation, ManufacturerPart, LocationType } from '../../types';
import { CabinetPlanner as Engine } from '../services/engineeringEngine';
import { Box, AlertTriangle, Settings } from 'lucide-react';

interface RackPanelProps {
  locationId: string;
  instruments: Asset[];
  locations: PhysicalLocation[];
  catalog: ManufacturerPart[];
}

export const RackPanel: React.FC<RackPanelProps> = ({ locationId, instruments, locations, catalog }) => {
  const [sparePct, setSparePct] = useState<number>(20);
  const selectedLocation = locations.find(l => l.id === locationId);

  const calculationResults = useMemo(() => {
    if (!locationId) return [];
    return Engine.calculateRacks(instruments, locationId, locations, sparePct, catalog);
  }, [locationId, sparePct, instruments, locations, catalog]);

  const totalCards = calculationResults.reduce((acc, curr) => acc + curr.cardsRequired, 0);

  if (!selectedLocation) return null;

  const isValidForPlanning = [
    LocationType.PLC, LocationType.RIO, LocationType.PANEL, LocationType.MCC, LocationType.JB
  ].includes(selectedLocation.type);

  if (!isValidForPlanning) {
    return (
      <div className="h-full flex flex-col items-center justify-center text-slate-500">
        <AlertTriangle size={48} className="mb-4 opacity-30" />
        <p>Rack planning is not applicable for {selectedLocation?.type}.</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      <div className="bg-slate-900/50 p-4 rounded-lg border border-slate-800 mb-4 flex justify-between items-center">
        <div className="flex items-center text-slate-300 text-sm">
          <Settings size={16} className="mr-2 text-mining-gold" />
          <span>Automated Rack Planning</span>
        </div>
        <div className="flex items-center gap-4">
          <span className="text-xs font-medium text-slate-500 uppercase">Spare Capacity</span>
          <div className="flex items-center gap-2 bg-slate-950 px-3 py-1 rounded border border-slate-800">
            <input
              type="range" min="0" max="50" step="5" value={sparePct}
              onChange={(e) => setSparePct(Number(e.target.value))}
              className="w-24 h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-mining-gold"
            />
            <span className="text-mining-gold font-mono font-bold text-sm">{sparePct}%</span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-4 overflow-y-auto pb-4">
        {calculationResults.map((res, idx) => {
          const totalCapacity = res.cardsRequired * (res.channelsPerCard || 8);
          const usedCapacity = res.requiredSignals;
          const usagePct = (usedCapacity / totalCapacity) * 100;
          const isCritical = usagePct > 90;

          return (
            <div key={idx} className="bg-slate-900 p-4 rounded-lg border border-slate-800 flex flex-col relative overflow-hidden group hover:border-slate-600 transition-colors shadow-lg">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <span className="px-2 py-1 bg-slate-800 text-xs font-mono text-slate-300 rounded border border-slate-700">{res.ioType}</span>
                  <h4 className="text-white font-medium mt-2">{res.cardModel}</h4>
                </div>
                <div className="text-right">
                  <span className="block text-2xl font-bold text-white">{res.cardsRequired}</span>
                  <span className="text-xs text-slate-500">Cards</span>
                </div>
              </div>
              <div className="space-y-3 text-sm mt-2">
                <div>
                  <div className="flex justify-between text-xs mb-1">
                    <span className="text-slate-500">Utilization ({usedCapacity}/{totalCapacity})</span>
                    <span className={`font-mono ${isCritical ? 'text-red-500' : 'text-green-500'}`}>{usagePct.toFixed(1)}%</span>
                  </div>
                  <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                    <div className={`h-full ${isCritical ? 'bg-red-500' : 'bg-mining-teal'}`} style={{ width: `${usagePct}%` }}></div>
                  </div>
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  );
};
