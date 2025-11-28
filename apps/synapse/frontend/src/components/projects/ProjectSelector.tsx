import React, { useEffect, useState } from 'react';
import { useProjectStore } from '../../store/useProjectStore';
import { useAuthStore } from '../../store/useAuthStore';
import axios from 'axios';

interface Project {
    id: string;
    name: string;
    client_id: string;
    description?: string;
    status?: string;
}

export const ProjectSelector: React.FC = () => {
    const { currentProject, setCurrentProject, allProjects, setAllProjects } = useProjectStore();
    const { token } = useAuthStore();
    const [isOpen, setIsOpen] = useState(false);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        // Load projects on mount
        const loadProjects = async () => {
            if (!token) return;

            setLoading(true);
            try {
                // Use relative path to leverage Nginx proxy
                const response = await axios.get('/api/v1/projects/projects', {
                    headers: { Authorization: `Bearer ${token}` }
                });
                setAllProjects(response.data);

                // Set first project as current if none selected
                if (!currentProject && response.data.length > 0) {
                    setCurrentProject(response.data[0]);
                }
            } catch (error) {
                console.error('Failed to load projects:', error);
            } finally {
                setLoading(false);
            }
        };

        loadProjects();
    }, [token, setAllProjects, currentProject, setCurrentProject]);

    const handleProjectSelect = (project: Project) => {
        setCurrentProject(project);
        setIsOpen(false);
        // Reload page to refresh data with new project
        window.location.reload();
    };

    if (loading) {
        return (
            <div className="px-4 py-2 text-slate-400 text-sm">
                Loading projects...
            </div>
        );
    }

    if (allProjects.length === 0) {
        return (
            <div className="px-4 py-2 text-amber-400 text-sm">
                ⚠️ No projects available
            </div>
        );
    }

    return (
        <div className="relative">
            {/* Selector Button */}
            <button
                onClick={() => setIsOpen(!isOpen)}
                className="flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 rounded-lg border border-slate-700 transition-colors"
            >
                <svg className="w-5 h-5 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
                </svg>
                <div className="text-left">
                    <div className="text-xs text-slate-400">Project</div>
                    <div className="text-sm font-medium text-white">
                        {currentProject?.name || 'Select Project'}
                    </div>
                </div>
                <svg className={`w-4 h-4 text-slate-400 transition-transform ${isOpen ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
            </button>

            {/* Dropdown Menu */}
            {isOpen && (
                <div className="absolute top-full mt-2 left-0 w-80 bg-slate-800 border border-slate-700 rounded-lg shadow-2xl z-50 max-h-96 overflow-y-auto">
                    <div className="p-2">
                        <div className="px-3 py-2 text-xs font-medium text-slate-400 uppercase tracking-wide">
                            Select Project ({allProjects.length})
                        </div>
                        {allProjects.map((project) => (
                            <button
                                key={project.id}
                                onClick={() => handleProjectSelect(project)}
                                className={`w-full text-left px-3 py-2 rounded-md transition-colors ${currentProject?.id === project.id
                                    ? 'bg-cyan-500/20 border border-cyan-500/50'
                                    : 'hover:bg-slate-700'
                                    }`}
                            >
                                <div className="flex items-start justify-between">
                                    <div className="flex-1 min-w-0">
                                        <div className="text-sm font-medium text-white truncate">
                                            {project.name}
                                        </div>
                                        {project.description && (
                                            <div className="text-xs text-slate-400 truncate mt-0.5">
                                                {project.description}
                                            </div>
                                        )}
                                        {project.status && (
                                            <div className="mt-1">
                                                <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${project.status === 'ACTIVE' ? 'bg-green-500/20 text-green-400' :
                                                    project.status === 'HOLD' ? 'bg-amber-500/20 text-amber-400' :
                                                        'bg-slate-500/20 text-slate-400'
                                                    }`}>
                                                    {project.status}
                                                </span>
                                            </div>
                                        )}
                                    </div>
                                    {currentProject?.id === project.id && (
                                        <svg className="w-5 h-5 text-cyan-400 flex-shrink-0 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                        </svg>
                                    )}
                                </div>
                            </button>
                        ))}
                    </div>
                </div>
            )}

            {/* Click outside to close */}
            {isOpen && (
                <div
                    className="fixed inset-0 z-40"
                    onClick={() => setIsOpen(false)}
                />
            )}
        </div>
    );
};
