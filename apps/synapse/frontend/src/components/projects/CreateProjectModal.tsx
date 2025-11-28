import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { X, Loader2, Plus } from 'lucide-react';
import { useProjectStore } from '../../store/useProjectStore';
import { useAuthStore } from '../../store/useAuthStore';
import { API_URL } from '../../../config';
import { logger } from '../../services/logger';

interface CreateProjectModalProps {
    isOpen: boolean;
    onClose: () => void;
}

interface Client {
    id: string;
    name: string;
}

export const CreateProjectModal: React.FC<CreateProjectModalProps> = ({ isOpen, onClose }) => {
    const [name, setName] = useState('');
    const [description, setDescription] = useState('');
    const [clientId, setClientId] = useState('');
    const [clients, setClients] = useState<Client[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [isFetchingClients, setIsFetchingClients] = useState(false);
    const [error, setError] = useState('');

    const { token } = useAuthStore();
    const { setAllProjects, allProjects, setCurrentProject } = useProjectStore();

    useEffect(() => {
        if (isOpen && token) {
            fetchClients();
        }
    }, [isOpen, token]);

    const fetchClients = async () => {
        setIsFetchingClients(true);
        try {
            const response = await axios.get(`${API_URL}/api/v1/projects/clients`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            setClients(response.data);
            if (response.data.length > 0) {
                setClientId(response.data[0].id);
            }
        } catch (err) {
            logger.error('Failed to fetch clients', err);
            setError('Failed to load clients');
        } finally {
            setIsFetchingClients(false);
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!name || !clientId) {
            setError('Name and Client are required');
            return;
        }

        setIsLoading(true);
        setError('');

        try {
            const response = await axios.post(
                `${API_URL}/api/v1/projects/projects`,
                {
                    name,
                    description,
                    client_id: clientId,
                    status: 'ACTIVE'
                },
                {
                    headers: { Authorization: `Bearer ${token}` }
                }
            );

            const newProject = response.data;
            setAllProjects([...allProjects, newProject]);
            setCurrentProject(newProject);
            logger.success('Project created successfully');
            onClose();

            // Reset form
            setName('');
            setDescription('');
        } catch (err) {
            logger.error('Failed to create project', err);
            setError(err.response?.data?.detail || 'Failed to create project');
        } finally {
            setIsLoading(false);
        }
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm animate-in fade-in duration-200">
            <div className="w-full max-w-md bg-slate-900 border border-slate-800 rounded-xl shadow-2xl overflow-hidden animate-in zoom-in-95 duration-200">
                {/* Header */}
                <div className="flex items-center justify-between p-4 border-b border-slate-800 bg-slate-900/50">
                    <h2 className="text-lg font-semibold text-white flex items-center gap-2">
                        <Plus className="w-5 h-5 text-mining-teal" />
                        Create New Project
                    </h2>
                    <button
                        onClick={onClose}
                        className="p-1 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition-colors"
                    >
                        <X className="w-5 h-5" />
                    </button>
                </div>

                {/* Body */}
                <form onSubmit={handleSubmit} className="p-6 space-y-4">
                    {/* Name */}
                    <div>
                        <label className="block text-sm font-medium text-slate-300 mb-1">
                            Project Name
                        </label>
                        <input
                            type="text"
                            value={name}
                            onChange={(e) => setName(e.target.value)}
                            className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-mining-teal focus:border-transparent"
                            placeholder="e.g., Gold Mine Expansion"
                            required
                        />
                    </div>

                    {/* Description */}
                    <div>
                        <label className="block text-sm font-medium text-slate-300 mb-1">
                            Description
                        </label>
                        <textarea
                            value={description}
                            onChange={(e) => setDescription(e.target.value)}
                            className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-mining-teal focus:border-transparent h-24 resize-none"
                            placeholder="Optional project description..."
                        />
                    </div>

                    {/* Client */}
                    <div>
                        <label className="block text-sm font-medium text-slate-300 mb-1">
                            Client
                        </label>
                        {isFetchingClients ? (
                            <div className="flex items-center gap-2 text-sm text-slate-500 px-3 py-2">
                                <Loader2 className="w-4 h-4 animate-spin" />
                                Loading clients...
                            </div>
                        ) : (
                            <select
                                value={clientId}
                                onChange={(e) => setClientId(e.target.value)}
                                className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-mining-teal focus:border-transparent"
                                required
                            >
                                {clients.map((client) => (
                                    <option key={client.id} value={client.id}>
                                        {client.name}
                                    </option>
                                ))}
                            </select>
                        )}
                    </div>

                    {/* Error */}
                    {error && (
                        <div className="p-3 bg-red-900/20 border border-red-900/50 rounded-lg text-red-400 text-sm">
                            {error}
                        </div>
                    )}

                    {/* Footer */}
                    <div className="flex items-center justify-end gap-3 pt-4 mt-4 border-t border-slate-800">
                        <button
                            type="button"
                            onClick={onClose}
                            className="px-4 py-2 text-sm font-medium text-slate-300 hover:text-white hover:bg-slate-800 rounded-lg transition-colors"
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            disabled={isLoading || isFetchingClients}
                            className="px-4 py-2 text-sm font-medium bg-mining-teal hover:bg-teal-600 text-white rounded-lg shadow-lg shadow-mining-teal/20 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                        >
                            {isLoading ? (
                                <>
                                    <Loader2 className="w-4 h-4 animate-spin" />
                                    Creating...
                                </>
                            ) : (
                                'Create Project'
                            )}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};
