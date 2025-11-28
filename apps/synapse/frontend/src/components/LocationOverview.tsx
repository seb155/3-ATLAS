
import React, { useMemo } from 'react';
import { Asset, PhysicalLocation } from '../../types';
import { CabinetPlanner as Engine } from '../services/engineeringEngine';
import { PieChart, Zap, Server, Thermometer, Cpu, ArrowRight, Box, HardDrive } from 'lucide-react';

interface LocationOverviewProps {
  locationId: string;
  instruments: Asset[];
  locations: PhysicalLocation[];
  onNavigate: (locId: string) => void;
}

export const LocationOverview: React.FC<LocationOverviewProps> = ({ locationId, instruments, locations, onNavigate }) => {
  const currentLocation = locations.find(l => l.id === locationId);
  const childrenLocations = useMemo(() => locations.filter(l => l.parentId === locationId), [locations, locationId]);

  const linkedAssets = useMemo(() => {
    const descendantIds = Engine.getDescendantLocationIds(locationId, locations);
    const targetIds = [locationId, ...descendantIds];
    return instruments.filter(i => i.locationId && targetIds.includes(i.locationId));
  }, [instruments, locations, locationId]);

  // Design Metrics Calculation
  const designMetrics = useMemo(() => {
    // Fake calculation logic for PoC
    const totalHeat = linkedAssets.length * 15; // 15W per device est.
    const totalPower = linkedAssets.reduce((acc, curr) => acc + (curr.electrical?.powerKW || 0.1), 0);
    return { totalHeat, totalPower };
  }, [linkedAssets]);

  if (!currentLocation) return <div>Location not found</div>;

  return (
    <div className="h-full overflow-y-auto pr-2 custom-scrollbar p-6 space-y-6">

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <StatCard icon={Cpu} label="Total Assets" value={linkedAssets.length} color="text-mining-teal" bg="bg-mining-teal/10" />
        <StatCard icon={Zap} label="Design Power Load" value={`${designMetrics.totalPower.toFixed(1)} kW`} color="text-blue-400" bg="bg-blue-500/10" />
        <StatCard icon={Thermometer} label="Heat Dissipation" value={`${designMetrics.totalHeat} W`} color="text-orange-400" bg="bg-orange-500/10" />
        <StatCard icon={HardDrive} label="Design Capacity" value={currentLocation.designHeatDissipation ? `${(designMetrics.totalHeat / currentLocation.designHeatDissipation * 100).toFixed(0)}%` : 'N/A'} color="text-purple-400" bg="bg-purple-500/10" />
      </div>

      <div className="bg-slate-900 rounded-xl border border-slate-800 p-6 shadow-lg">
        <h3 className="text-lg font-bold text-white flex items-center gap-2 mb-4">
          <Box size={18} className="text-slate-400" />
          Internal Architecture (Equipment Layout)
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {childrenLocations.map(child => (
            <div
              key={child.id}
              onClick={() => onNavigate(child.id)}
              className="bg-slate-950 hover:bg-slate-800 border border-slate-800 hover:border-mining-teal group cursor-pointer p-4 rounded-lg transition-all relative overflow-hidden"
            >
              <div className="flex justify-between items-start mb-3">
                <div className="p-2 bg-slate-900 rounded border border-slate-800">
                  {child.type === 'MCC' ? <Zap size={20} className="text-orange-400" /> : <Server size={20} className="text-slate-400" />}
                </div>
                <ArrowRight size={16} className="text-mining-teal opacity-0 group-hover:opacity-100 transition-all" />
              </div>
              <h4 className="font-mono font-bold text-slate-200">{child.name}</h4>
              <p className="text-xs text-slate-500 mb-2">{child.type}</p>

              {/* Mini utilization bar mock */}
              <div className="w-full bg-slate-900 h-1 rounded overflow-hidden">
                <div className="bg-slate-700 h-full w-1/2"></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

interface StatCardProps {
  icon: React.ComponentType<{ size?: number }>;
  label: string;
  value: string | number;
  color: string;
  bg: string;
}

const StatCard: React.FC<StatCardProps> = ({ icon: Icon, label, value, color, bg }) => (
  <div className="bg-slate-900 p-4 rounded-lg border border-slate-800 shadow-lg flex items-center">
    <div className={`p-3 rounded-full ${bg} ${color} mr-4`}>
      <Icon size={24} />
    </div>
    <div>
      <p className="text-slate-400 text-xs uppercase font-bold">{label}</p>
      <p className="text-2xl font-bold text-white font-mono">{value}</p>
    </div>
  </div>
);
