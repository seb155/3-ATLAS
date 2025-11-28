import { useState, useEffect } from 'react';

export interface FilterPreset {
    id: string;
    name: string;
    description: string;
    filterModel: any; // AG Grid filter model
}

interface UseFilterPresetsProps {
    pageName: string;
    gridApi?: any;
}

export function useFilterPresets({ pageName, gridApi }: UseFilterPresetsProps) {
    const [savedPresets, setSavedPresets] = useState<FilterPreset[]>([]);

    // Load saved presets from localStorage
    useEffect(() => {
        const saved = localStorage.getItem(`synapse_filter_presets_${pageName}`);
        if (saved) {
            try {
                setSavedPresets(JSON.parse(saved));
            } catch (e) {
                console.error('Failed to load filter presets:', e);
            }
        }
    }, [pageName]);

    const applyFilter = (filterModel: any) => {
        if (!gridApi) return;
        gridApi.setFilterModel(filterModel);
    };

    const getCurrentFilter = () => {
        if (!gridApi) return null;
        return gridApi.getFilterModel();
    };

    const savePreset = (name: string, description: string) => {
        const filterModel = getCurrentFilter();
        if (!filterModel || Object.keys(filterModel).length === 0) {
            return { success: false, message: 'No active filters to save' };
        }

        const newPreset: FilterPreset = {
            id: `preset_${Date.now()}`,
            name,
            description,
            filterModel
        };

        const updated = [...savedPresets, newPreset];
        setSavedPresets(updated);
        localStorage.setItem(`synapse_filter_presets_${pageName}`, JSON.stringify(updated));

        return { success: true, preset: newPreset };
    };

    const deletePreset = (presetId: string) => {
        const updated = savedPresets.filter(p => p.id !== presetId);
        setSavedPresets(updated);
        localStorage.setItem(`synapse_filter_presets_${pageName}`, JSON.stringify(updated));
    };

    const clearAllFilters = () => {
        if (!gridApi) return;
        gridApi.setFilterModel(null);
    };

    // Quick filter definitions
    const applyQuickFilter = (filterType: string) => {
        let filterModel: any = {};

        switch (filterType) {
            case 'all':
                clearAllFilters();
                return;

            case 'motors':
                filterModel = {
                    type: {
                        filterType: 'text',
                        type: 'equals',
                        filter: 'MOTOR'
                    }
                };
                break;

            case 'incomplete':
                // Items missing description or critical fields
                filterModel = {
                    description: {
                        filterType: 'text',
                        type: 'blank'
                    }
                };
                break;

            case '600v':
                filterModel = {
                    'electrical.voltage': {
                        filterType: 'number',
                        type: 'equals',
                        filter: 600
                    }
                };
                break;

            case 'high_power':
                filterModel = {
                    'electrical.powerKW': {
                        filterType: 'number',
                        type: 'greaterThan',
                        filter: 50
                    }
                };
                break;
        }

        applyFilter(filterModel);
    };

    const exportPreset = (preset: FilterPreset) => {
        const dataStr = JSON.stringify(preset, null, 2);
        const dataUri = 'data:application/json;charset=utf-8,' + encodeURIComponent(dataStr);
        const exportFileDefaultName = `${preset.name.replace(/\s+/g, '_')}_preset.json`;

        const linkElement = document.createElement('a');
        linkElement.setAttribute('href', dataUri);
        linkElement.setAttribute('download', exportFileDefaultName);
        linkElement.click();
    };

    const importPreset = (file: File) => {
        return new Promise<FilterPreset>((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = (e) => {
                try {
                    const preset = JSON.parse(e.target?.result as string);
                    const imported: FilterPreset = {
                        ...preset,
                        id: `preset_${Date.now()}` // Generate new ID
                    };
                    const updated = [...savedPresets, imported];
                    setSavedPresets(updated);
                    localStorage.setItem(`synapse_filter_presets_${pageName}`, JSON.stringify(updated));
                    resolve(imported);
                } catch (error) {
                    reject(error);
                }
            };
            reader.readAsText(file);
        });
    };

    return {
        savedPresets,
        applyFilter,
        applyQuickFilter,
        savePreset,
        deletePreset,
        clearAllFilters,
        exportPreset,
        importPreset,
        getCurrentFilter
    };
}
