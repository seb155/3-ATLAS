import React from 'react';
import { Play, AlertCircle } from 'lucide-react';
import { Badge } from '../ui/Badge';
import { Card } from '../ui/Card';

interface Rule {
    id: string;
    name: string;
    description: string | null;
    source: 'FIRM' | 'COUNTRY' | 'PROJECT' | 'CLIENT';
    priority: number;
    discipline: string | null;
    action_type: string;
    is_active: boolean;
}

interface Asset {
    id: string;
    name: string;
    type: string;
}

interface RulesSidebarProps {
    rules: Rule[];
    selectedAssets: Asset[];
    isExecuting: boolean;
    onExecuteRule: (ruleId: string) => void;
}

export function RulesSidebar({
    rules,
    selectedAssets,
    isExecuting,
    onExecuteRule
}: RulesSidebarProps) {
    const activeRules = rules.filter(r => r.is_active);

    const getSourceBadgeColor = (source: string) => {
        const colors: Record<string, string> = {
            FIRM: 'bg-blue-500/20 text-blue-300 border-blue-500/30',
            COUNTRY: 'bg-green-500/20 text-green-300 border-green-500/30',
            PROJECT: 'bg-yellow-500/20 text-yellow-300 border-yellow-500/30',
            CLIENT: 'bg-purple-500/20 text-purple-300 border-purple-500/30',
        };
        return colors[source] || 'bg-slate-700 text-slate-300 border-slate-600';
    };

    if (activeRules.length === 0) {
        return (
            <div className="p-6 text-center">
                <AlertCircle className="w-12 h-12 text-slate-600 mx-auto mb-3" />
                <div className="text-slate-400 text-sm">No active rules available</div>
            </div>
        );
    }

    return (
        <div className="divide-y divide-slate-800">
            {activeRules.map((rule) => (
                <div key={rule.id} className="p-4 hover:bg-slate-800/50 transition-colors">
                    <div className="flex items-start justify-between gap-3 mb-2">
                        <div className="flex-1 min-w-0">
                            <div className="text-sm font-medium text-white truncate">
                                {rule.name}
                            </div>
                            {rule.description && (
                                <div className="text-xs text-slate-400 mt-1 line-clamp-2">
                                    {rule.description}
                                </div>
                            )}
                        </div>
                    </div>

                    <div className="flex items-center gap-2 mb-3">
                        <Badge
                            variant="outline"
                            className={`border text-xs ${getSourceBadgeColor(rule.source)}`}
                        >
                            {rule.source}
                        </Badge>
                        <span className="text-xs text-slate-500">P{rule.priority}</span>
                        {rule.discipline && (
                            <span className="text-xs text-slate-500">{rule.discipline}</span>
                        )}
                    </div>

                    <button
                        onClick={() => onExecuteRule(rule.id)}
                        disabled={isExecuting}
                        className="w-full px-3 py-1.5 bg-green-600/20 hover:bg-green-600/30 disabled:opacity-50 disabled:cursor-not-allowed border border-green-500/30 rounded text-green-300 text-xs font-medium flex items-center justify-center gap-2 transition-colors"
                    >
                        <Play className="w-3 h-3" />
                        {selectedAssets.length > 0
                            ? `Apply to ${selectedAssets.length} selected`
                            : 'Apply to all assets'
                        }
                    </button>
                </div>
            ))}
        </div>
    );
}
