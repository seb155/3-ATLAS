import React, { useState } from 'react';
import { Filter, Save, Trash2, Download, Upload, RotateCcw, Plus } from 'lucide-react';
import { useFilterPresets, FilterPreset } from '../hooks/useFilterPresets';

interface FilterPresetsProps {
    pageName: string;
    gridApi?: any;
}

export function FilterPresets({ pageName, gridApi }: FilterPresetsProps) {
    const {
        savedPresets,
        applyFilter,
        applyQuickFilter,
        savePreset,
        deletePreset,
        clearAllFilters,
        exportPreset,
        importPreset,
        getCurrentFilter
    } = useFilterPresets({ pageName, gridApi });

    const [newPresetName, setNewPresetName] = useState('');
    const [isCreating, setIsCreating] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const fileInputRef = React.useRef<HTMLInputElement>(null);

    const handleSavePreset = () => {
        if (!newPresetName.trim()) {
            setError('Name is required');
            return;
        }

        const result = savePreset(newPresetName, 'User created preset');
        if (result.success) {
            setNewPresetName('');
            setIsCreating(false);
            setError(null);
        } else {
            setError(result.message || 'Failed to save preset');
        }
    };

    const handleImportClick = () => {
        fileInputRef.current?.click();
    };

    const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (!file) return;

        try {
            await importPreset(file);
            if (fileInputRef.current) fileInputRef.current.value = '';
        } catch (err) {
            console.error('Import failed', err);
            setError('Failed to import preset');
        }
    };

    return (
        <div className="h-full flex flex-col bg-slate-900">
            <input
                type="file"
                ref={fileInputRef}
                onChange={handleFileChange}
                className="hidden"
                accept=".json"
            />

            {/* Quick Filters */}
            <div className="p-4 border-b border-slate-800">
                <label className="text-xs font-semibold text-slate-500 uppercase tracking-wider block mb-3">
                    Quick Filters
                </label>
                <div className="grid grid-cols-2 gap-2">
                    <button
                        onClick={() => applyQuickFilter('all')}
                        className="px-3 py-2 text-sm bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-lg text-slate-300 transition-colors text-left"
                    >
                        Show All
                    </button>
                    <button
                        onClick={() => applyQuickFilter('motors')}
                        className="px-3 py-2 text-sm bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-lg text-slate-300 transition-colors text-left"
                    >
                        Motors Only
                    </button>
                    <button
                        onClick={() => applyQuickFilter('incomplete')}
                        className="px-3 py-2 text-sm bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-lg text-slate-300 transition-colors text-left"
                    >
                        Incomplete Data
                    </button>
                    <button
                        onClick={() => applyQuickFilter('600v')}
                        className="px-3 py-2 text-sm bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-lg text-slate-300 transition-colors text-left"
                    >
                        600V Equipment
                    </button>
                </div>
            </div>

            {/* Saved Presets */}
            <div className="flex-1 overflow-y-auto p-4 custom-scrollbar">
                <div className="flex items-center justify-between mb-3">
                    <label className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                        Saved Presets
                    </label>
                    <div className="flex gap-2">
                        <button
                            onClick={handleImportClick}
                            className="p-1 text-slate-400 hover:text-white transition-colors"
                            title="Import Preset"
                        >
                            <Upload size={14} />
                        </button>
                    </div>
                </div>

                <div className="space-y-2">
                    {savedPresets.length === 0 ? (
                        <div className="text-sm text-slate-500 italic text-center py-4">
                            No saved presets
                        </div>
                    ) : (
                        savedPresets.map(preset => (
                            <div
                                key={preset.id}
                                className="group flex items-center justify-between p-3 bg-slate-800/50 border border-slate-700/50 rounded-lg hover:bg-slate-800 transition-colors"
                            >
                                <button
                                    onClick={() => applyFilter(preset.filterModel)}
                                    className="flex-1 text-left text-sm text-slate-300 hover:text-white truncate"
                                >
                                    {preset.name}
                                </button>
                                <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                                    <button
                                        onClick={() => exportPreset(preset)}
                                        className="p-1.5 text-slate-400 hover:text-mining-teal transition-colors"
                                        title="Export"
                                    >
                                        <Download size={14} />
                                    </button>
                                    <button
                                        onClick={() => deletePreset(preset.id)}
                                        className="p-1.5 text-slate-400 hover:text-red-400 transition-colors"
                                        title="Delete"
                                    >
                                        <Trash2 size={14} />
                                    </button>
                                </div>
                            </div>
                        ))
                    )}
                </div>
            </div>

            {/* Create New Preset */}
            <div className="p-4 border-t border-slate-800 bg-slate-900/50">
                {isCreating ? (
                    <div className="space-y-3">
                        <input
                            type="text"
                            value={newPresetName}
                            onChange={(e) => setNewPresetName(e.target.value)}
                            placeholder="Preset name..."
                            className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-300 focus:ring-1 focus:ring-mining-teal focus:border-mining-teal outline-none"
                            autoFocus
                        />
                        {error && <p className="text-xs text-red-400">{error}</p>}
                        <div className="flex gap-2">
                            <button
                                onClick={handleSavePreset}
                                className="flex-1 py-1.5 text-sm bg-mining-teal text-slate-900 font-medium rounded-lg hover:bg-mining-teal/90 transition-colors"
                            >
                                Save
                            </button>
                            <button
                                onClick={() => {
                                    setIsCreating(false);
                                    setNewPresetName('');
                                    setError(null);
                                }}
                                className="flex-1 py-1.5 text-sm bg-slate-800 text-slate-400 rounded-lg hover:bg-slate-700 transition-colors"
                            >
                                Cancel
                            </button>
                        </div>
                    </div>
                ) : (
                    <div className="flex gap-2">
                        <button
                            onClick={() => setIsCreating(true)}
                            className="flex-1 flex items-center justify-center gap-2 py-2 text-sm bg-slate-800 border border-slate-700 rounded-lg text-slate-300 hover:bg-slate-700 transition-colors"
                        >
                            <Plus size={14} />
                            Save Current Filters
                        </button>
                        <button
                            onClick={clearAllFilters}
                            className="px-3 py-2 text-sm bg-slate-800 border border-slate-700 rounded-lg text-slate-300 hover:bg-slate-700 transition-colors"
                            title="Clear All Filters"
                        >
                            <RotateCcw size={14} />
                        </button>
                    </div>
                )}
            </div>
        </div>
    );
}
