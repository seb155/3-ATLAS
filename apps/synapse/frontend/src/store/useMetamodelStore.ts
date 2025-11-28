import { create } from 'zustand';

interface MetamodelState {
    highlightedNodeId: string | null;
    setHighlightedNodeId: (id: string | null) => void;
}

export const useMetamodelStore = create<MetamodelState>((set) => ({
    highlightedNodeId: null,
    setHighlightedNodeId: (id) => set({ highlightedNodeId: id }),
}));
