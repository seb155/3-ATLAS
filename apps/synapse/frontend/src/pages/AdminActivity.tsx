import React, { useEffect, useState } from 'react';
import { Activity, RefreshCw, Download, Filter, Clock, Database, Zap } from 'lucide-react';
import axios from 'axios';
import { useAuthStore } from '../store/useAuthStore';
import { useProjectStore } from '../store/useProjectStore';

interface ActivityLog {
    id: string;
    type: 'action' | 'workflow';
    action_type: string;
    entity_type: string;
    entity_id: string | null;
    entity_tag?: string;
    description: string;
    details: Record<string, unknown>;
    timestamp: string;
    correlation_id?: string;
}

interface Stats {
    assets: number;
    cables: number;
    action_logs: number;
    workflow_events: number;
}

export const AdminActivity: React.FC = () => {
    const { token } = useAuthStore();
    const { currentProject } = useProjectStore();
    const [logs, setLogs] = useState<ActivityLog[]>([]);
    const [stats, setStats] = useState<Stats | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [filter, setFilter] = useState({
        hours: 24,
        actionType: '',
        entityType: '',
    });
    const [expandedLog, setExpandedLog] = useState<string | null>(null);

    const fetchData = async () => {
        if (!token || !currentProject) return;
        setLoading(true);
        setError(null);

        try {
            const [logsRes, statsRes] = await Promise.all([
                axios.get('/api/v1/admin/activity', {
                    headers: {
                        Authorization: `Bearer ${token}`,
                        'X-Project-ID': currentProject.id,
                    },
                    params: {
                        hours: filter.hours || undefined,
                        action_type: filter.actionType || undefined,
                        entity_type: filter.entityType || undefined,
                        limit: 200,
                    },
                }),
                axios.get('/api/v1/admin/stats', {
                    headers: {
                        Authorization: `Bearer ${token}`,
                        'X-Project-ID': currentProject.id,
                    },
                }),
            ]);
            setLogs(logsRes.data.logs);
            setStats(statsRes.data);
        } catch (err) {
            setError('Failed to load activity logs');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
    }, [token, currentProject, filter.hours]);

    const exportLogs = () => {
        const json = JSON.stringify(logs, null, 2);
        const blob = new Blob([json], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `activity-logs-${new Date().toISOString().split('T')[0]}.json`;
        a.click();
        URL.revokeObjectURL(url);
    };

    const formatTimestamp = (ts: string) => {
        const date = new Date(ts);
        return date.toLocaleString();
    };

    const getActionColor = (actionType: string) => {
        switch (actionType?.toUpperCase()) {
            case 'CREATE':
                return 'text-green-400 bg-green-500/10';
            case 'UPDATE':
                return 'text-blue-400 bg-blue-500/10';
            case 'DELETE':
                return 'text-red-400 bg-red-500/10';
            case 'RULE_EXECUTION':
                return 'text-purple-400 bg-purple-500/10';
            case 'IMPORT':
                return 'text-cyan-400 bg-cyan-500/10';
            case 'ERROR':
                return 'text-red-400 bg-red-500/10';
            default:
                return 'text-slate-400 bg-slate-500/10';
        }
    };

    return (
        <div className="p-6 space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <Activity className="w-8 h-8 text-cyan-400" />
                    <div>
                        <h1 className="text-2xl font-bold text-white">Activity Log</h1>
                        <p className="text-slate-400 text-sm">System activity and workflow history</p>
                    </div>
                </div>
                <div className="flex items-center gap-2">
                    <button
                        onClick={fetchData}
                        className="flex items-center gap-2 px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg text-white"
                    >
                        <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
                        Refresh
                    </button>
                    <button
                        onClick={exportLogs}
                        className="flex items-center gap-2 px-4 py-2 bg-cyan-600 hover:bg-cyan-500 rounded-lg text-white"
                    >
                        <Download size={16} />
                        Export JSON
                    </button>
                </div>
            </div>

            {/* Stats Cards */}
            {stats && (
                <div className="grid grid-cols-4 gap-4">
                    <div className="bg-slate-800 border border-slate-700 rounded-lg p-4">
                        <div className="text-3xl font-bold text-white">{stats.assets}</div>
                        <div className="text-sm text-slate-400">Assets</div>
                    </div>
                    <div className="bg-slate-800 border border-slate-700 rounded-lg p-4">
                        <div className="text-3xl font-bold text-white">{stats.cables}</div>
                        <div className="text-sm text-slate-400">Cables</div>
                    </div>
                    <div className="bg-slate-800 border border-slate-700 rounded-lg p-4">
                        <div className="text-3xl font-bold text-cyan-400">{stats.action_logs}</div>
                        <div className="text-sm text-slate-400">Action Logs</div>
                    </div>
                    <div className="bg-slate-800 border border-slate-700 rounded-lg p-4">
                        <div className="text-3xl font-bold text-purple-400">{stats.workflow_events}</div>
                        <div className="text-sm text-slate-400">Workflow Events</div>
                    </div>
                </div>
            )}

            {/* Filters */}
            <div className="flex items-center gap-4 bg-slate-800 border border-slate-700 rounded-lg p-4">
                <Filter size={18} className="text-slate-400" />
                <select
                    value={filter.hours}
                    onChange={(e) => setFilter({ ...filter, hours: parseInt(e.target.value) })}
                    className="bg-slate-700 border border-slate-600 rounded px-3 py-2 text-white"
                >
                    <option value={1}>Last hour</option>
                    <option value={6}>Last 6 hours</option>
                    <option value={24}>Last 24 hours</option>
                    <option value={72}>Last 3 days</option>
                    <option value={168}>Last week</option>
                </select>
                <select
                    value={filter.entityType}
                    onChange={(e) => setFilter({ ...filter, entityType: e.target.value })}
                    className="bg-slate-700 border border-slate-600 rounded px-3 py-2 text-white"
                >
                    <option value="">All Entity Types</option>
                    <option value="ASSET">Asset</option>
                    <option value="CABLE">Cable</option>
                    <option value="RULE">Rule</option>
                    <option value="IMPORT">Import</option>
                </select>
            </div>

            {/* Error */}
            {error && (
                <div className="bg-red-500/10 border border-red-500/50 rounded-lg p-4 text-red-400">
                    {error}
                </div>
            )}

            {/* Logs Table */}
            <div className="bg-slate-800 border border-slate-700 rounded-lg overflow-hidden">
                <table className="w-full">
                    <thead className="bg-slate-900">
                        <tr>
                            <th className="px-4 py-3 text-left text-xs font-medium text-slate-400 uppercase">Time</th>
                            <th className="px-4 py-3 text-left text-xs font-medium text-slate-400 uppercase">Type</th>
                            <th className="px-4 py-3 text-left text-xs font-medium text-slate-400 uppercase">Action</th>
                            <th className="px-4 py-3 text-left text-xs font-medium text-slate-400 uppercase">Entity</th>
                            <th className="px-4 py-3 text-left text-xs font-medium text-slate-400 uppercase">Description</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-700">
                        {loading ? (
                            <tr>
                                <td colSpan={5} className="px-4 py-8 text-center text-slate-400">
                                    Loading...
                                </td>
                            </tr>
                        ) : logs.length === 0 ? (
                            <tr>
                                <td colSpan={5} className="px-4 py-8 text-center text-slate-400">
                                    No activity logs found
                                </td>
                            </tr>
                        ) : (
                            logs.map((log) => (
                                <React.Fragment key={log.id}>
                                    <tr
                                        className="hover:bg-slate-700/50 cursor-pointer"
                                        onClick={() => setExpandedLog(expandedLog === log.id ? null : log.id)}
                                    >
                                        <td className="px-4 py-3 text-sm text-slate-300 whitespace-nowrap">
                                            <div className="flex items-center gap-2">
                                                <Clock size={14} className="text-slate-500" />
                                                {formatTimestamp(log.timestamp)}
                                            </div>
                                        </td>
                                        <td className="px-4 py-3">
                                            <span className={`inline-flex items-center gap-1 px-2 py-1 rounded text-xs ${log.type === 'workflow' ? 'text-purple-400 bg-purple-500/10' : 'text-cyan-400 bg-cyan-500/10'
                                                }`}>
                                                {log.type === 'workflow' ? <Zap size={12} /> : <Database size={12} />}
                                                {log.type}
                                            </span>
                                        </td>
                                        <td className="px-4 py-3">
                                            <span className={`px-2 py-1 rounded text-xs ${getActionColor(log.action_type)}`}>
                                                {log.action_type}
                                            </span>
                                        </td>
                                        <td className="px-4 py-3 text-sm text-slate-300">
                                            {log.entity_tag || log.entity_type || '-'}
                                        </td>
                                        <td className="px-4 py-3 text-sm text-slate-400 truncate max-w-md">
                                            {log.description}
                                        </td>
                                    </tr>
                                    {expandedLog === log.id && (
                                        <tr>
                                            <td colSpan={5} className="px-4 py-4 bg-slate-900">
                                                <pre className="text-xs text-slate-300 overflow-x-auto">
                                                    {JSON.stringify(log.details, null, 2)}
                                                </pre>
                                            </td>
                                        </tr>
                                    )}
                                </React.Fragment>
                            ))
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default AdminActivity;
