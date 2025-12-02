import React, { useState } from 'react';
import { Wrench, Database, Zap, Trash2, AlertTriangle, CheckCircle, Loader2 } from 'lucide-react';
import axios from 'axios';
import { useAuthStore } from '../store/useAuthStore';
import { useProjectStore } from '../store/useProjectStore';

interface ActionResult {
    status: 'success' | 'error';
    message: string;
    details?: Record<string, unknown>;
}

export const AdminTools: React.FC = () => {
    const { token } = useAuthStore();
    const { currentProject } = useProjectStore();
    const [loading, setLoading] = useState<string | null>(null);
    const [result, setResult] = useState<ActionResult | null>(null);
    const [showConfirmClear, setShowConfirmClear] = useState(false);

    const runAction = async (action: string, method: 'post' | 'delete' = 'post', params?: Record<string, unknown>) => {
        if (!token || !currentProject) return;
        setLoading(action);
        setResult(null);

        try {
            const response = await axios({
                method,
                url: `/api/v1/admin/${action}`,
                headers: {
                    Authorization: `Bearer ${token}`,
                    'X-Project-ID': currentProject.id,
                },
                params,
            });
            setResult({
                status: 'success',
                message: response.data.message || `${action} completed successfully`,
                details: response.data,
            });
        } catch (err: unknown) {
            const error = err as { response?: { data?: { message?: string } } };
            setResult({
                status: 'error',
                message: error.response?.data?.message || `Failed to run ${action}`,
            });
        } finally {
            setLoading(null);
        }
    };

    const handleClearData = () => {
        runAction('clear-data', 'delete', { confirm: true });
        setShowConfirmClear(false);
    };

    return (
        <div className="p-6 space-y-6">
            {/* Header */}
            <div className="flex items-center gap-3">
                <Wrench className="w-8 h-8 text-amber-400" />
                <div>
                    <h1 className="text-2xl font-bold text-white">Admin Tools</h1>
                    <p className="text-slate-400 text-sm">Debug and administrative actions</p>
                </div>
            </div>

            {/* Result Banner */}
            {result && (
                <div className={`flex items-center gap-3 p-4 rounded-lg border ${result.status === 'success'
                        ? 'bg-green-500/10 border-green-500/50 text-green-400'
                        : 'bg-red-500/10 border-red-500/50 text-red-400'
                    }`}>
                    {result.status === 'success' ? <CheckCircle size={20} /> : <AlertTriangle size={20} />}
                    <div className="flex-1">
                        <div className="font-medium">{result.message}</div>
                        {result.details && (
                            <pre className="mt-2 text-xs text-slate-400 overflow-x-auto">
                                {JSON.stringify(result.details, null, 2)}
                            </pre>
                        )}
                    </div>
                    <button
                        onClick={() => setResult(null)}
                        className="text-slate-400 hover:text-white"
                    >
                        &times;
                    </button>
                </div>
            )}

            {/* Action Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {/* Seed Demo Data */}
                <div className="bg-slate-800 border border-slate-700 rounded-lg p-6 space-y-4">
                    <div className="flex items-center gap-3">
                        <div className="p-3 bg-green-500/10 rounded-lg">
                            <Database className="w-6 h-6 text-green-400" />
                        </div>
                        <div>
                            <h3 className="text-lg font-semibold text-white">Seed Demo Data</h3>
                            <p className="text-sm text-slate-400">Add sample assets and rules</p>
                        </div>
                    </div>
                    <p className="text-slate-300 text-sm">
                        Creates demonstration data including pumps, motors, transmitters, and example rules for testing.
                    </p>
                    <button
                        onClick={() => runAction('seed-demo')}
                        disabled={loading !== null}
                        className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-500 disabled:bg-green-600/50 rounded-lg text-white font-medium transition-colors"
                    >
                        {loading === 'seed-demo' ? (
                            <Loader2 size={18} className="animate-spin" />
                        ) : (
                            <Database size={18} />
                        )}
                        Seed Demo Data
                    </button>
                </div>

                {/* Execute All Rules */}
                <div className="bg-slate-800 border border-slate-700 rounded-lg p-6 space-y-4">
                    <div className="flex items-center gap-3">
                        <div className="p-3 bg-purple-500/10 rounded-lg">
                            <Zap className="w-6 h-6 text-purple-400" />
                        </div>
                        <div>
                            <h3 className="text-lg font-semibold text-white">Execute All Rules</h3>
                            <p className="text-sm text-slate-400">Run rule engine on all assets</p>
                        </div>
                    </div>
                    <p className="text-slate-300 text-sm">
                        Executes all active rules against current assets. Creates child assets and cables based on rule definitions.
                    </p>
                    <button
                        onClick={() => runAction('execute-rules')}
                        disabled={loading !== null}
                        className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-purple-600 hover:bg-purple-500 disabled:bg-purple-600/50 rounded-lg text-white font-medium transition-colors"
                    >
                        {loading === 'execute-rules' ? (
                            <Loader2 size={18} className="animate-spin" />
                        ) : (
                            <Zap size={18} />
                        )}
                        Execute Rules
                    </button>
                </div>

                {/* Clear All Data */}
                <div className="bg-slate-800 border border-red-500/30 rounded-lg p-6 space-y-4">
                    <div className="flex items-center gap-3">
                        <div className="p-3 bg-red-500/10 rounded-lg">
                            <Trash2 className="w-6 h-6 text-red-400" />
                        </div>
                        <div>
                            <h3 className="text-lg font-semibold text-white">Clear All Data</h3>
                            <p className="text-sm text-red-400">Danger zone - Cannot be undone</p>
                        </div>
                    </div>
                    <p className="text-slate-300 text-sm">
                        Deletes all assets, cables, and logs from the current project. Rules are preserved.
                    </p>
                    <button
                        onClick={() => setShowConfirmClear(true)}
                        disabled={loading !== null}
                        className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-red-600 hover:bg-red-500 disabled:bg-red-600/50 rounded-lg text-white font-medium transition-colors"
                    >
                        {loading === 'clear-data' ? (
                            <Loader2 size={18} className="animate-spin" />
                        ) : (
                            <Trash2 size={18} />
                        )}
                        Clear Project Data
                    </button>
                </div>
            </div>

            {/* Confirm Clear Modal */}
            {showConfirmClear && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
                    <div className="bg-slate-800 border border-red-500/50 rounded-lg p-6 w-96 space-y-4">
                        <div className="flex items-center gap-3 text-red-400">
                            <AlertTriangle size={24} />
                            <h3 className="text-lg font-semibold">Confirm Delete All</h3>
                        </div>
                        <p className="text-slate-300">
                            This will permanently delete all assets, cables, and logs from
                            <strong className="text-white"> {currentProject?.name}</strong>.
                        </p>
                        <p className="text-sm text-slate-400">
                            Rules will be preserved. This action cannot be undone.
                        </p>
                        <div className="flex gap-3 justify-end">
                            <button
                                onClick={() => setShowConfirmClear(false)}
                                className="px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded text-white"
                            >
                                Cancel
                            </button>
                            <button
                                onClick={handleClearData}
                                className="px-4 py-2 bg-red-600 hover:bg-red-500 rounded text-white font-medium"
                            >
                                Delete Everything
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default AdminTools;
