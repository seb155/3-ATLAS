import React, { useState } from 'react';
import { X, Check, Columns3, RotateCcw } from 'lucide-react';
import { ColDef } from 'ag-grid-community';
import { useColumnPresets, ColumnPreset } from '../hooks/useColumnPresets';

interface ColumnManagerProps {
    pageName: string;
    columnDefs: ColDef[];
    gridApi?: any;
    onClose: () => void;
}

export function ColumnManager({ pageName, columnDefs, gridApi, onClose }: ColumnManagerProps) {
    const {
        currentPreset,
        visibleColumns,
        applyPreset,
        toggleColumn,
        selectAll,
        deselectAll,
        reset,
        presets
    } = useColumnPresets({ pageName, columnDefs, gridApi });

    // Get all column fields with labels
    const getAllColumns = () => {
        const columns: Array<{ field: string; label: string; group?: string }> = [];

        const extractColumns = (defs: ColDef[], group?: string) => {
            defs.forEach(def => {
                if (def.field) {
                    columns.push({
                        field: def.field,
                        label: def.headerName || def.field,
                        group
                    });
                }
                // @ts-ignore - ColDef children property exists but not in type definition
                if (def.children) {
                    // @ts-ignore
                    extractColumns(def.children, def.headerName);
                }
            });
        };

        extractColumns(columnDefs);
        return columns;
    };

    const columns = getAllColumns();

    // Group columns by their group name
    const groupedColumns = columns.reduce((acc, col) => {
        const group = col.group || 'General';
        if (!acc[group]) acc[group] = [];
        acc[group].push(col);
        return acc;
    }, {} as Record<string, typeof columns>);

    return (
        <div className="h-full flex flex-col bg-slate-900">
            {/* Preset Selector */}
            <div className="p-4 border-b border-slate-800 bg-slate-900/50">
                <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-2">
                    Presets
                </label>
                <select
                    value={currentPreset}
                    onChange={(e) => applyPreset(e.target.value)}
                    className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-300 focus:ring-1 focus:ring-mining-teal focus:border-mining-teal outline-none"
                >
                    {presets.map(preset => (
                        <option key={preset.id} value={preset.id}>
                            {preset.name} - {preset.description}
                        </option>
                    ))}
                    <option value="custom">Custom</option>
                </select>
            </div>

            {/* Column List */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4 custom-scrollbar">
                {Object.entries(groupedColumns).map(([groupName, cols]) => (
                    <div key={groupName} className="space-y-2">
                        <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider px-2">
                            {groupName}
                        </div>
                        {cols.map(col => {
                            const isVisible = visibleColumns.has(col.field);
                            return (
                                <button
                                    key={col.field}
                                    onClick={() => toggleColumn(col.field)}
                                    className={`w-full flex items-center justify-between px-3 py-2 rounded-lg transition-colors ${isVisible
                                        ? 'bg-mining-teal/10 border border-mining-teal/30 text-white'
                                        : 'bg-slate-800/50 border border-slate-700/50 text-slate-400 hover:bg-slate-800 hover:border-slate-600'
                                        }`}
                                >
                                    <span className="text-sm font-medium">{col.label}</span>
                                    {isVisible && (
                                        <Check size={16} className="text-mining-teal" />
                                    )}
                                </button>
                            );
                        })}
                    </div>
                ))}
            </div>

            {/* Footer Actions */}
            <div className="p-4 border-t border-slate-800 flex items-center justify-between gap-2">
                <div className="flex gap-2">
                    <button
                        onClick={selectAll}
                        className="px-3 py-1.5 text-sm bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-lg text-slate-300 transition-colors"
                    >
                        Select All
                    </button>
                    <button
                        onClick={deselectAll}
                        className="px-3 py-1.5 text-sm bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-lg text-slate-300 transition-colors"
                    >
                        Deselect All
                    </button>
                </div>
                <button
                    onClick={reset}
                    className="flex items-center gap-2 px-3 py-1.5 text-sm bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-lg text-slate-300 transition-colors"
                    title="Reset to default"
                >
                    <RotateCcw size={14} />
                    Reset
                </button>
            </div>
        </div>
    );
}
