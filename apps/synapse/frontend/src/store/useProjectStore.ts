import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface Project {
    id: string;
    name: string;
    client_id: string;
    description?: string;
    status?: string;
}

interface Client {
    id: string;
    name: string;
    projects: Project[];
}

interface ProjectState {
    currentProject: Project | null;
    currentClient: Client | null;
    allProjects: Project[];
    allClients: Client[];
    setCurrentProject: (project: Project) => void;
    setCurrentClient: (client: Client) => void;
    setAllProjects: (projects: Project[]) => void;
    setAllClients: (clients: Client[]) => void;
    clearProject: () => void;
}

export const useProjectStore = create<ProjectState>()(
    persist(
        (set) => ({
            currentProject: null,
            currentClient: null,
            allProjects: [],
            allClients: [],
            setCurrentProject: (project) => set({ currentProject: project }),
            setCurrentClient: (client) => set({ currentClient: client }),
            setAllProjects: (projects) => set({ allProjects: projects }),
            setAllClients: (clients) => set({ allClients: clients }),
            clearProject: () => set({ currentProject: null, currentClient: null }),
        }),
        {
            name: 'project-storage',
        }
    )
);
