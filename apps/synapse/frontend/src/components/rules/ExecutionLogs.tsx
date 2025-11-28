import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { API_URL } from '../../../config';
import { useAuthStore } from '../../store/useAuthStore';
import { CheckCircle, XCircle, Clock, Loader2 } from 'lucide-react';

interface ExecutionLog {
    id: string;
    rule_id: string;
    action_type: string;
    action_taken: string;
    condition_matched: boolean;
    timestamp: string;
    execution_time_ms: number | null;
    error_message: string | null;
}

interface ExecutionLogsProps {
    projectId: string | undefined;
}

export function ExecutionLogs({ projectId }: ExecutionLogsProps) {
    const [logs, setLogs] = useState<ExecutionLog[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const { token } = useAuthStore();

    useEffect(() => {
        if (projectId) {
            fetchLogs();
        }
    }, [projectId]);

    const fetchLogs = async () => {
        if (!projectId) return;

        setIsLoading(true);
        try {
            const response = await axios.get(
                `${API_URL}/api/v1/rules/executions/logs`,
                {
                    headers: { 'Authorization': `Bearer ${token}` },
                    params: { project_id: projectId, limit: 50 }
                }
            );
            setLogs(response.data.logs || []);
        } catch (error) {
            console.error('Failed to fetch execution logs:', error);
            setLogs([]);
        } finally {
            setIsLoading(false);
        }
    };

    const getActionIcon = (actionType: string, hasError: boolean) => {
        if (hasError) return <XCircle className="w-4 h-4 text-red-400" />;

        switch (actionType) {
            case 'CREATE':
            case 'UPDATE':
            case 'LINK':
                return <CheckCircle className="w-4 h-4 text-green-400" />;
            case 'SKIP':
                return <Clock className="w-4 h-4 text-slate-500" />;
            case 'ERROR':
                return <XCircle className="w-4 h-4 text-red-400" />;
            default:
                return <Clock className="w-4 h-4 text-slate-400" />;
        }
    };

    if (isLoading) {
        return (
            <div className="p-6 flex items-center justify-center">
                <div className="flex items-center gap-2 text-slate-400">
                    <Loader2 className="w-5 h-5 animate-spin" />
                    <span className="text-sm">Loading logs...</span>
                </div>
            </div>
        );
    }

    if (!projectId) {
        return (
            <div className="p-6 text-center text-slate-500 text-sm">
                Select a project to view execution logs
            </div>
        );
    }

    if (logs.length === 0) {
        return (
            <div className="p-6 text-center text-slate-500 text-sm">
                No execution logs yet. Execute some rules to see logs here.
            </div>
        );
    }

    return (
        <div className="divide-y divide-slate-800 max-h-[500px] overflow-y-auto">
            {logs.map((log) => (
                <div key={log.id} className="p-3 hover:bg-slate-800/50 transition-colors">
                    <div className="flex items-start gap-3">
                        <div className="flex-shrink-0 mt-0.5">
                            {getActionIcon(log.action_type, !!log.error_message)}
                        </div>
                        <div className="flex-1 min-w-0">
                            <div className="text-xs text-white">
                                {log.action_taken}
                            </div>
                            {log.error_message && (
                                <div className="text-xs text-red-400 mt-1">
                                    Error: {log.error_message}
                                </div>
                            )}
                            <div className="flex items-center gap-2 mt-1 text-xs text-slate-500">
                                <span>{new Date(log.timestamp).toLocaleTimeString()}</span>
                                {log.execution_time_ms && (
                                    <>
                                        <span>•</span>
                                        <span>{log.execution_time_ms}ms</span>
                                    </>
                                )}
                            </div>
                        </div>
                    </div>
                </div>
            ))}
        </div>
    );
}
