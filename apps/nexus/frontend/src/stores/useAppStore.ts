import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface AppState {
  sidebarOpen: boolean;
  currentView: string;
  toggleSidebar: () => void;
  setView: (view: string) => void;
}

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      sidebarOpen: true,
      currentView: 'dashboard',
      toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
      setView: (view) => set({ currentView: view }),
    }),
    {
      name: 'nexus-app-storage',
      partialize: (state) => ({
        sidebarOpen: state.sidebarOpen,
        currentView: state.currentView,
      }),
    },
  ),
);
