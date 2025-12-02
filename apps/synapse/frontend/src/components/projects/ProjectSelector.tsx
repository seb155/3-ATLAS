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

type ModalType = 'none' | 'clearAssets' | 'deleteProject' | 'createProject';

export const ProjectSelector: React.FC = () => {
    const { currentProject, setCurrentProject, allProjects, setAllProjects } = useProjectStore();
    const { token } = useAuthStore();
    const [isOpen, setIsOpen] = useState(false);
    const [loading, setLoading] = useState(false);
    const [showSettings, setShowSettings] = useState(false);
    const [modalType, setModalType] = useState<ModalType>('none');
    const [actionLoading, setActionLoading] = useState(false);
    const [newProjectName, setNewProjectName] = useState('');

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

    const loadProjects = async () => {
        if (!token) return;
        try {
            const response = await axios.get('/api/v1/projects/projects', {
                headers: { Authorization: `Bearer ${token}` }
            });
            setAllProjects(response.data);
        } catch (error) {
            console.error('Failed to load projects:', error);
        }
    };

    const handleClearAssets = async () => {
        if (!currentProject || !token) return;
        setActionLoading(true);
        try {
            await axios.delete(`/api/v1/projects/projects/${currentProject.id}/assets`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            setModalType('none');
            window.location.reload();
        } catch (error) {
            console.error('Failed to clear assets:', error);
            alert('Failed to clear assets');
        } finally {
            setActionLoading(false);
        }
    };

    const handleDeleteProject = async () => {
        if (!currentProject || !token) return;
        setActionLoading(true);
        try {
            await axios.delete(`/api/v1/projects/projects/${currentProject.id}`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            setModalType('none');
            // Select another project or reload
            const remaining = allProjects.filter(p => p.id !== currentProject.id);
            if (remaining.length > 0) {
                setCurrentProject(remaining[0]);
            } else {
                setCurrentProject(null);
            }
            await loadProjects();
            window.location.reload();
        } catch (error) {
            console.error('Failed to delete project:', error);
            alert('Failed to delete project');
        } finally {
            setActionLoading(false);
        }
    };

    const handleCreateProject = async () => {
        if (!newProjectName.trim() || !token) return;
        setActionLoading(true);
        try {
            // Get first client or create default
            const clientsRes = await axios.get('/api/v1/projects/clients', {
                headers: { Authorization: `Bearer ${token}` }
            });
            let clientId = clientsRes.data[0]?.id;

            if (!clientId) {
                // Create default client
                const newClient = await axios.post('/api/v1/projects/clients',
                    { name: 'Default Client' },
                    { headers: { Authorization: `Bearer ${token}` } }
                );
                clientId = newClient.data.id;
            }

            const response = await axios.post('/api/v1/projects/projects',
                { name: newProjectName.trim(), client_id: clientId },
                { headers: { Authorization: `Bearer ${token}` } }
            );
            setModalType('none');
            setNewProjectName('');
            setCurrentProject(response.data);
            await loadProjects();
            window.location.reload();
        } catch (error) {
            console.error('Failed to create project:', error);
            alert('Failed to create project');
        } finally {
            setActionLoading(false);
        }
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
        <div className="relative flex items-center gap-2">
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

            {/* Settings Button */}
            <div className="relative">
                <button
                    onClick={() => setShowSettings(!showSettings)}
                    className="p-2 bg-slate-800 hover:bg-slate-700 rounded-lg border border-slate-700 transition-colors"
                    title="Project Settings"
                >
                    <svg className="w-5 h-5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    </svg>
                </button>

                {/* Settings Dropdown */}
                {showSettings && (
                    <div className="absolute top-full mt-2 right-0 w-48 bg-slate-800 border border-slate-700 rounded-lg shadow-2xl z-50">
                        <div className="p-1">
                            <button
                                onClick={() => { setModalType('createProject'); setShowSettings(false); }}
                                className="w-full flex items-center gap-2 px-3 py-2 text-sm text-green-400 hover:bg-slate-700 rounded"
                            >
                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                                </svg>
                                New Project
                            </button>
                            <button
                                onClick={() => { setModalType('clearAssets'); setShowSettings(false); }}
                                className="w-full flex items-center gap-2 px-3 py-2 text-sm text-amber-400 hover:bg-slate-700 rounded"
                                disabled={!currentProject}
                            >
                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                </svg>
                                Clear Assets
                            </button>
                            <div className="border-t border-slate-700 my-1"></div>
                            <button
                                onClick={() => { setModalType('deleteProject'); setShowSettings(false); }}
                                className="w-full flex items-center gap-2 px-3 py-2 text-sm text-red-400 hover:bg-red-500/20 rounded"
                                disabled={!currentProject}
                            >
                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                </svg>
                                Delete Project
                            </button>
                        </div>
                    </div>
                )}
            </div>

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
            {(isOpen || showSettings) && (
                <div
                    className="fixed inset-0 z-40"
                    onClick={() => { setIsOpen(false); setShowSettings(false); }}
                />
            )}

            {/* Confirmation Modals */}
            {modalType !== 'none' && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
                    <div className="bg-slate-800 border border-slate-700 rounded-lg shadow-2xl p-6 w-96">
                        {modalType === 'clearAssets' && (
                            <>
                                <h3 className="text-lg font-semibold text-amber-400 mb-2">Clear All Assets</h3>
                                <p className="text-slate-300 mb-4">
                                    This will delete all assets from <strong>{currentProject?.name}</strong>.
                                    This action cannot be undone.
                                </p>
                                <div className="flex gap-3 justify-end">
                                    <button
                                        onClick={() => setModalType('none')}
                                        className="px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded text-white"
                                        disabled={actionLoading}
                                    >
                                        Cancel
                                    </button>
                                    <button
                                        onClick={handleClearAssets}
                                        className="px-4 py-2 bg-amber-500 hover:bg-amber-600 rounded text-white"
                                        disabled={actionLoading}
                                    >
                                        {actionLoading ? 'Clearing...' : 'Clear Assets'}
                                    </button>
                                </div>
                            </>
                        )}

                        {modalType === 'deleteProject' && (
                            <>
                                <h3 className="text-lg font-semibold text-red-400 mb-2">Delete Project</h3>
                                <p className="text-slate-300 mb-4">
                                    This will permanently delete <strong>{currentProject?.name}</strong> and all its data.
                                    This action cannot be undone.
                                </p>
                                <div className="flex gap-3 justify-end">
                                    <button
                                        onClick={() => setModalType('none')}
                                        className="px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded text-white"
                                        disabled={actionLoading}
                                    >
                                        Cancel
                                    </button>
                                    <button
                                        onClick={handleDeleteProject}
                                        className="px-4 py-2 bg-red-500 hover:bg-red-600 rounded text-white"
                                        disabled={actionLoading}
                                    >
                                        {actionLoading ? 'Deleting...' : 'Delete Project'}
                                    </button>
                                </div>
                            </>
                        )}

                        {modalType === 'createProject' && (
                            <>
                                <h3 className="text-lg font-semibold text-green-400 mb-4">Create New Project</h3>
                                <input
                                    type="text"
                                    value={newProjectName}
                                    onChange={(e) => setNewProjectName(e.target.value)}
                                    placeholder="Project name"
                                    className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded text-white placeholder-slate-400 mb-4"
                                    autoFocus
                                />
                                <div className="flex gap-3 justify-end">
                                    <button
                                        onClick={() => { setModalType('none'); setNewProjectName(''); }}
                                        className="px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded text-white"
                                        disabled={actionLoading}
                                    >
                                        Cancel
                                    </button>
                                    <button
                                        onClick={handleCreateProject}
                                        className="px-4 py-2 bg-green-500 hover:bg-green-600 rounded text-white"
                                        disabled={actionLoading || !newProjectName.trim()}
                                    >
                                        {actionLoading ? 'Creating...' : 'Create Project'}
                                    </button>
                                </div>
                            </>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
};
