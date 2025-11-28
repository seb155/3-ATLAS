import React, { useEffect, useState } from 'react';
import { useAppStore } from '../store/useAppStore';
import { useProjectStore } from '../store/useProjectStore';
import {
    LayoutDashboard, Database, Network, FileJson, BookOpen, Zap,
    Activity, ArrowUpRight, Layers, Box, Cable, AlertCircle, CheckCircle2
} from 'lucide-react';
import axios from 'axios';
import ValidationResultsModal from '../components/ValidationResultsModal';

export const Dashboard = () => {
    const { instruments, locations, setCurrentView } = useAppStore();
    const { currentProject, currentClient } = useProjectStore();
    const [cableCount, setCableCount] = useState<number>(0);
    const [ruleCount, setRuleCount] = useState<number>(0);
    const [loading, setLoading] = useState(true);
    const [showValidationModal, setShowValidationModal] = useState(false);
    const [validationResults, setValidationResults] = useState<any[]>([]);
    const [validationSummary, setValidationSummary] = useState({ total: 0, pass: 0, warning: 0, error: 0 });

    useEffect(() => {
        const fetchMetrics = async () => {
            if (!currentProject) return;

            try {
                // Fetch cables count
                const cablesRes = await axios.get('/api/v1/cables/');
                setCableCount(cablesRes.data.length);

                // Fetch rules count
                const rulesRes = await axios.get('/api/v1/rules');
                setRuleCount(rulesRes.data.length);
            } catch (error) {
                console.error("Failed to fetch dashboard metrics:", error);
            } finally {
                setLoading(false);
            }
        };

        fetchMetrics();
    }, [currentProject]);

    if (!currentProject) return null;

    // Calculate stats
    const instrumentsArray = Array.isArray(instruments) ? instruments : [];
    const unlinkedTags = instrumentsArray.filter(i => !i.locationId).length;
    const lbsCoverage = instrumentsArray.length > 0
        ? Math.round(((instrumentsArray.length - unlinkedTags) / instrumentsArray.length) * 100)
        : 0;

    const StatCard = ({ title, value, icon: Icon, color, subtext }: any) => (
        <div className="bg-slate-800/50 backdrop-blur-sm p-6 rounded-xl border border-slate-700/50 shadow-lg hover:border-slate-600 transition-all group">
            <div className="flex justify-between items-start mb-4">
                <div className={`p-3 rounded-lg bg-${color}-500/10 text-${color}-400 group-hover:bg-${color}-500/20 transition-colors`}>
                    <Icon size={24} />
                </div>
                {subtext && (
                    <span className={`text-xs font-medium px-2 py-1 rounded-full bg-${color}-500/10 text-${color}-400`}>
                        {subtext}
                    </span>
                )}
            </div>
            <h3 className="text-slate-400 text-sm font-medium mb-1">{title}</h3>
            <p className="text-3xl font-bold text-white tracking-tight">{value}</p>
        </div>
    );

    const QuickAction = ({ title, icon: Icon, view, color, desc, onClick }: any) => (
        <button
            onClick={onClick || (() => setCurrentView(view))}
            className="flex items-center p-4 bg-slate-800/30 hover:bg-slate-800 border border-slate-700/50 hover:border-slate-600 rounded-xl transition-all text-left group w-full"
        >
            <div className={`p-3 rounded-lg bg-${color}-500/10 text-${color}-400 mr-4 group-hover:scale-110 transition-transform`}>
                <Icon size={20} />
            </div>
            <div>
                <h4 className="text-white font-medium group-hover:text-cyan-400 transition-colors">{title}</h4>
                <p className="text-xs text-slate-500 mt-0.5">{desc}</p>
            </div>
            <ArrowUpRight size={16} className="ml-auto text-slate-600 group-hover:text-cyan-400 opacity-0 group-hover:opacity-100 transition-all" />
        </button>
    );

    const validateProject = async () => {
        if (!currentProject) return;

        setLoading(true);
        try {
            const response = await axios.post(`/api/v1/projects/${currentProject.id}/validate`);
            setValidationResults(response.data.validation_results);
            setValidationSummary(response.data.summary);
            setShowValidationModal(true);
        } catch (error) {
            console.error("Validation failed:", error);
            alert("Failed to validate project. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="space-y-8 p-6 max-w-7xl mx-auto">
            {/* Header */}
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <div className="flex items-center gap-2 text-slate-400 text-sm mb-1">
                        <span>{currentClient?.name || 'Client'}</span>
                        <span>/</span>
                        <span>{currentProject.name}</span>
                    </div>
                    <h1 className="text-3xl font-bold text-white tracking-tight">Project Overview</h1>
                    <p className="text-slate-400 mt-2 max-w-2xl">
                        {currentProject.description || 'Manage your engineering assets, cables, and automation rules.'}
                    </p>
                </div>
                <div className="flex items-center gap-3">
                    <span className="px-3 py-1 rounded-full bg-green-500/10 text-green-400 text-xs font-medium border border-green-500/20">
                        {currentProject.status || 'ACTIVE'}
                    </span>
                    <span className="text-xs text-slate-500 font-mono">
                        ID: {currentProject.id.split('-')[0]}...
                    </span>
                </div>
            </div>

            {/* Metrics Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <StatCard
                    title="Total Assets"
                    value={instrumentsArray.length}
                    icon={Database}
                    color="cyan"
                    subtext="+12 this week"
                />
                <StatCard
                    title="Cables Generated"
                    value={cableCount}
                    icon={Cable}
                    color="purple"
                />
                <StatCard
                    title="Active Rules"
                    value={ruleCount}
                    icon={BookOpen}
                    color="amber"
                />
                <StatCard
                    title="LBS Coverage"
                    value={`${lbsCoverage}%`}
                    icon={Layers}
                    color={lbsCoverage > 80 ? "green" : "red"}
                    subtext={unlinkedTags + " unlinked"}
                />
            </div>

            {/* Quick Actions & Recent Activity */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Quick Actions */}
                <div className="lg:col-span-2 space-y-6">
                    <h3 className="text-lg font-semibold text-white flex items-center gap-2">
                        <Zap size={18} className="text-yellow-400" />
                        Quick Actions
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <QuickAction
                            title="Engineering Explorer"
                            desc="Manage assets and hierarchy"
                            icon={Network}
                            view="engineering"
                            color="cyan"
                        />
                        <QuickAction
                            title="Cable Schedule"
                            desc="View and export cable lists"
                            icon={FileJson}
                            view="cables"
                            color="purple"
                        />
                        <QuickAction
                            title="Rules Management"
                            desc="Configure automation logic"
                            icon={BookOpen}
                            view="rules"
                            color="amber"
                        />
                        <QuickAction
                            title="Data Ingestion"
                            desc="Import new engineering data"
                            icon={Database}
                            view="modern-ingestion"
                            color="blue"
                        />
                        <QuickAction
                            title="Validate Project"
                            desc="Check data quality and rules"
                            icon={CheckCircle2}
                            view="validate"
                            color="green"
                            onClick={validateProject}
                        />
                    </div>
                </div>

                {/* Recent Activity (Mock) */}
                <div className="space-y-6">
                    <h3 className="text-lg font-semibold text-white flex items-center gap-2">
                        <Activity size={18} className="text-blue-400" />
                        Recent Activity
                    </h3>
                    <div className="bg-slate-800/30 rounded-xl border border-slate-700/50 p-4 space-y-4">
                        {[1, 2, 3].map((_, i) => (
                            <div key={i} className="flex gap-3 items-start pb-4 border-b border-slate-700/50 last:border-0 last:pb-0">
                                <div className="w-2 h-2 mt-2 rounded-full bg-cyan-400" />
                                <div>
                                    <p className="text-sm text-slate-300">
                                        <span className="font-medium text-white">Admin</span> updated
                                        <span className="text-cyan-400"> 12 assets</span> in
                                        <span className="text-slate-400"> Area 02</span>
                                    </p>
                                    <p className="text-xs text-slate-500 mt-1">2 hours ago</p>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            <ValidationResultsModal
                isOpen={showValidationModal}
                onClose={() => setShowValidationModal(false)}
                results={validationResults}
                summary={validationSummary}
            />
        </div>
    );
};

export default Dashboard;
