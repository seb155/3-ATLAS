
import React, { useState } from 'react';
import { Plus, Trash2, HelpCircle } from 'lucide-react';
import { RuleCondition, PropertyFilter, ComparisonOperator } from '../../types/rules';

interface ConditionBuilderProps {
  condition: RuleCondition;
  onChange: (condition: RuleCondition) => void;
}

export default function ConditionBuilder({ condition, onChange }: ConditionBuilderProps) {
  const [assetType, setAssetType] = useState(condition?.asset_type || '');
  const [nodeType, setNodeType] = useState(condition?.node_type || '');
  const [propertyFilters, setPropertyFilters] = useState(
    condition?.property_filters || []
  );

  const updateCondition = (updates: Partial<RuleCondition>) => {
    const newCondition = { ...condition, ...updates };
    // Clean up empty fields
    if (!newCondition.asset_type) delete newCondition.asset_type;
    if (!newCondition.node_type) delete newCondition.node_type;
    if (!newCondition.property_filters || newCondition.property_filters.length === 0) {
      delete newCondition.property_filters;
    }
    onChange(newCondition);
  };

  const handleAssetTypeChange = (value: string) => {
    setAssetType(value);
    updateCondition({ asset_type: value || undefined, node_type: undefined });
    setNodeType('');
  };

  const handleNodeTypeChange = (value: string) => {
    setNodeType(value);
    updateCondition({ node_type: value || undefined, asset_type: undefined });
    setAssetType('');
  };

  const handlePropertyFilterChange = (index: number, field: string, value: string) => {
    const newFilters = [...propertyFilters];
    newFilters[index] = { ...newFilters[index], [field]: value };
    setPropertyFilters(newFilters);
    updateCondition({ property_filters: newFilters });
  };

  const addPropertyFilter = () => {
    const newFilters: PropertyFilter[] = [...propertyFilters, { key: '', op: '==' as ComparisonOperator, value: '' }];
    setPropertyFilters(newFilters);
    updateCondition({ property_filters: newFilters });
  };

  const removePropertyFilter = (index: number) => {
    const newFilters = propertyFilters.filter((_: PropertyFilter, i: number) => i !== index);
    setPropertyFilters(newFilters);
    updateCondition({ property_filters: newFilters });
  };

  const assetTypes = [
    'PUMP',
    'TANK',
    'AGITATOR',
    'VALVE',
    'HEAT_EXCHANGER',
    'REACTOR',
    'MOTOR',
    'LEVEL_TRANSMITTER',
    'PRESSURE_TRANSMITTER',
    'FLOW_TRANSMITTER',
    'TEMPERATURE_TRANSMITTER',
  ];

  const nodeTypes = [
    'AREA',
    'SITE',
    'UNIT',
    'SYSTEM',
  ];

  const operators = [
    { value: '==', label: 'Equals' },
    { value: '!=', label: 'Not Equals' },
    { value: '>', label: 'Greater Than' },
    { value: '<', label: 'Less Than' },
    { value: '>=', label: 'Greater or Equal' },
    { value: '<=', label: 'Less or Equal' },
    { value: 'in', label: 'In List' },
    { value: 'contains', label: 'Contains' },
  ];

  return (
    <div className="space-y-4">
      {/* Type Selection */}
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-slate-300 mb-1">
            Asset Type
            <HelpCircle className="inline w-3 h-3 ml-1 text-slate-500" />
          </label>
          <select
            value={assetType}
            onChange={(e) => handleAssetTypeChange(e.target.value)}
            className="w-full px-3 py-2 bg-slate-900 border border-slate-600 rounded-lg focus:ring-2 focus:ring-green-500 text-white"
          >
            <option value="">-- Select Asset Type --</option>
            {assetTypes.map((type) => (
              <option key={type} value={type}>
                {type}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-300 mb-1">
            OR Node Type
            <HelpCircle className="inline w-3 h-3 ml-1 text-slate-500" />
          </label>
          <select
            value={nodeType}
            onChange={(e) => handleNodeTypeChange(e.target.value)}
            className="w-full px-3 py-2 bg-slate-900 border border-slate-600 rounded-lg focus:ring-2 focus:ring-green-500 text-white"
          >
            <option value="">-- Select Node Type --</option>
            {nodeTypes.map((type) => (
              <option key={type} value={type}>
                {type}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Property Filters */}
      <div>
        <div className="flex items-center justify-between mb-2">
          <label className="block text-sm font-medium text-slate-300">
            Property Filters (Optional)
          </label>
          <button
            onClick={addPropertyFilter}
            className="flex items-center gap-1 px-2 py-1 text-xs text-green-400 hover:bg-slate-700 rounded transition-colors"
          >
            <Plus className="w-3 h-3" />
            Add Filter
          </button>
        </div>

        {propertyFilters.length === 0 ? (
          <div className="text-sm text-slate-400 italic p-3 bg-slate-800/50 rounded border border-dashed border-slate-700">
            No property filters. Rule will match all assets of the selected type.
          </div>
        ) : (
          <div className="space-y-2">
            {propertyFilters.map((filter: PropertyFilter, index: number) => (
              <div key={index} className="flex items-center gap-2 p-2 bg-slate-800 border border-slate-600 rounded-lg">
                <input
                  type="text"
                  placeholder="Property key"
                  value={filter.key || ''}
                  onChange={(e) => handlePropertyFilterChange(index, 'key', e.target.value)}
                  className="flex-1 px-2 py-1 text-sm bg-slate-900 border border-slate-600 rounded focus:ring-2 focus:ring-green-500 text-white placeholder-slate-500"
                />
                <select
                  value={filter.op || '=='}
                  onChange={(e) => handlePropertyFilterChange(index, 'op', e.target.value)}
                  className="w-32 px-2 py-1 text-sm bg-slate-900 border border-slate-600 rounded focus:ring-2 focus:ring-green-500 text-white"
                >
                  {operators.map((op) => (
                    <option key={op.value} value={op.value}>
                      {op.label}
                    </option>
                  ))}
                </select>
                <input
                  type="text"
                  placeholder="Value"
                  value={String(filter.value || '')}
                  onChange={(e) => handlePropertyFilterChange(index, 'value', e.target.value)}
                  className="flex-1 px-2 py-1 text-sm bg-slate-900 border border-slate-600 rounded focus:ring-2 focus:ring-green-500 text-white placeholder-slate-500"
                />
                <button
                  onClick={() => removePropertyFilter(index)}
                  className="p-1 text-red-400 hover:bg-slate-700 rounded transition-colors"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Examples */}
      <div className="mt-4 p-3 bg-blue-500/10 border border-blue-500/30 rounded-lg">
        <div className="text-sm font-medium text-blue-300 mb-2">Examples:</div>
        <ul className="text-xs text-blue-200 space-y-1">
          <li>• Match all PUMP assets: Select "PUMP" as Asset Type</li>
          <li>• Match centrifugal pumps only: Asset Type = PUMP, Add filter: pump_type == CENTRIFUGAL</li>
          <li>• Match all AREA nodes: Select "AREA" as Node Type</li>
          <li>• Match motors &gt; 100kW: Asset Type = MOTOR, Add filter: power &gt; 100</li>
        </ul>
      </div>
    </div>
  );
}
