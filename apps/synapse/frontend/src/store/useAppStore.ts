import { create } from 'zustand';
import axios from 'axios';
import { Asset, PhysicalLocation, Cable } from '../types';
import { useAuthStore } from './useAuthStore';
import { useProjectStore } from './useProjectStore';

interface AppState {
    instruments: Asset[];
    locations: PhysicalLocation[];
    cables: Cable[];
    currentView: string;
    setInstruments: (instruments: Asset[]) => void;
    setCurrentView: (view: string) => void;
    selectedRuleId: string | null;
    setSelectedRuleId: (id: string | null) => void;
    fetchData: () => Promise<void>;
    refreshData: () => Promise<void>;
    refreshCables: () => Promise<void>;
}

import { API_URL } from '@/config';

export const useAppStore = create<AppState>((set) => ({
    instruments: [],
    locations: [],
    cables: [],
    currentView: 'dashboard',
    selectedRuleId: null,
    setInstruments: (instruments) => set({ instruments }),
    setCurrentView: (view) => set({ currentView: view }),
    setSelectedRuleId: (id) => set({ selectedRuleId: id }),
    fetchData: async () => {
        const { token } = useAuthStore.getState();
        const { currentProject } = useProjectStore.getState();

        if (!token || !currentProject) return;

        const config = {
            headers: {
                Authorization: `Bearer ${token}`,
                'X-Project-ID': currentProject.id
            }
        };

        try {
            console.log("Fetching data for project:", currentProject.id);

            // Fetch Assets, Locations, and Cables
            const [assetsRes, locationsRes, cablesRes] = await Promise.all([
                axios.get(`${API_URL}/api/v1/assets/`, config),
                axios.get(`${API_URL}/api/v1/locations/`, config),
                axios.get(`${API_URL}/api/v1/cables/`, config)
            ]);

            // Defensive normalization: ALWAYS ensure arrays
            const rawAssets = Array.isArray(assetsRes.data) ? assetsRes.data : [];
            const locations = Array.isArray(locationsRes.data) ? locationsRes.data : [];
            const cables = Array.isArray(cablesRes.data) ? cablesRes.data : [];

            // Map snake_case to camelCase for package_id
            const assets = rawAssets.map((a: any) => ({
                ...a,
                packageId: a.package_id || a.packageId,
                locationId: a.location_id || a.locationId,
            }));

            console.log("Mapped Assets:", assets.length);
            set({ instruments: assets, locations: locations, cables: cables });
        } catch (error) {
            console.error("Failed to fetch data:", error);
        }
    },
    refreshData: async () => {
        const { fetchData } = useAppStore.getState();
        return fetchData();
    },
    refreshCables: async () => {
        // For now, just refresh everything to keep it simple
        const { fetchData } = useAppStore.getState();
        return fetchData();
    }
}));
