import { useState, useEffect } from 'react';
import { ColDef } from 'ag-grid-community';

export interface ColumnPreset {
    id: string;
    name: string;
    description: string;
    visibleFields: string[];
}

export const DEFAULT_PRESETS: ColumnPreset[] = [
    {
        id: 'essential',
        name: 'Essential',
        description: 'Core identification fields',
        visibleFields: ['tag', 'type', 'description', 'area', 'system', 'location']
    },
    {
        id: 'full',
        name: 'Full',
        description: 'All available columns',
        visibleFields: [] // Empty means show all
    },
    {
        id: 'electrical',
        name: 'Electrical',
        description: 'Electrical engineering focus',
        visibleFields: ['tag', 'type', 'description', 'electrical.voltage', 'electrical.powerKW', 'electrical.loadType', 'location']
    },
    {
        id: 'process',
        name: 'Process',
        description: 'Process engineering focus',
        visibleFields: ['tag', 'type', 'description', 'process.fluid', 'process.minRange', 'process.maxRange', 'process.units', 'location']
    },
    {
        id: 'procurement',
        name: 'Procurement',
        description: 'Purchasing and package info',
        visibleFields: ['tag', 'type', 'description', 'manufacturerPartId', 'purchasing.workPackageId', 'purchasing.status', 'location']
    }
];

interface UseColumnPresetsProps {
    pageName: string;
    columnDefs: ColDef[];
    gridApi?: any;
}

export function useColumnPresets({ pageName, columnDefs, gridApi }: UseColumnPresetsProps) {
    const [currentPreset, setCurrentPreset] = useState<string>('full');
    const [visibleColumns, setVisibleColumns] = useState<Set<string>>(new Set());

    // Load saved state from localStorage
    useEffect(() => {
        const saved = localStorage.getItem(`synapse_columns_${pageName}`);
        if (saved) {
            try {
                const { presetId, visible } = JSON.parse(saved);
                setCurrentPreset(presetId);
                setVisibleColumns(new Set(visible));
            } catch (e) {
                console.error('Failed to load column preset:', e);
            }
        } else {
            // Default: show all columns
            const allFields = getAllColumnFields(columnDefs);
            setVisibleColumns(new Set(allFields));
        }
    }, [pageName, columnDefs]);

    // Apply column visibility to grid
    useEffect(() => {
        if (!gridApi) return;

        try {
            // Extract all field names from columnDefs instead of using gridApi.getColumns()
            const allFields = getAllColumnFields(columnDefs);

            allFields.forEach((field: string) => {
                const shouldBeVisible = visibleColumns.has(field);
                gridApi.setColumnsVisible([field], shouldBeVisible);
            });
        } catch (error) {
            console.error('Error applying column visibility:', error);
        }
    }, [gridApi, visibleColumns, columnDefs]);

    const getAllColumnFields = (colDefs: ColDef[]): string[] => {
        const fields: string[] = [];

        const extractFields = (defs: ColDef[]) => {
            defs.forEach(def => {
                if (def.field) {
                    fields.push(def.field);
                }
                if (def.children) {
                    extractFields(def.children);
                }
            });
        };

        extractFields(colDefs);
        return fields;
    };

    const applyPreset = (presetId: string) => {
        const preset = DEFAULT_PRESETS.find(p => p.id === presetId);
        if (!preset) return;

        const allFields = getAllColumnFields(columnDefs);

        // If preset has no visibleFields (Full preset), show all
        const newVisible = preset.visibleFields.length === 0
            ? new Set(allFields)
            : new Set(preset.visibleFields);

        setCurrentPreset(presetId);
        setVisibleColumns(newVisible);
        saveState(presetId, Array.from(newVisible));
    };

    const toggleColumn = (field: string) => {
        const newVisible = new Set(visibleColumns);
        if (newVisible.has(field)) {
            newVisible.delete(field);
        } else {
            newVisible.add(field);
        }
        setVisibleColumns(newVisible);
        setCurrentPreset('custom');
        saveState('custom', Array.from(newVisible));
    };

    const selectAll = () => {
        const allFields = getAllColumnFields(columnDefs);
        const newVisible = new Set(allFields);
        setVisibleColumns(newVisible);
        setCurrentPreset('full');
        saveState('full', allFields);
    };

    const deselectAll = () => {
        setVisibleColumns(new Set());
        setCurrentPreset('custom');
        saveState('custom', []);
    };

    const saveState = (presetId: string, visible: string[]) => {
        localStorage.setItem(
            `synapse_columns_${pageName}`,
            JSON.stringify({ presetId, visible })
        );
    };

    const reset = () => {
        localStorage.removeItem(`synapse_columns_${pageName}`);
        applyPreset('full');
    };

    return {
        currentPreset,
        visibleColumns,
        applyPreset,
        toggleColumn,
        selectAll,
        deselectAll,
        reset,
        presets: DEFAULT_PRESETS
    };
}
