import React from 'react';
import { AlertTriangle, Shield, AlertCircle, CheckCircle, ChevronRight } from 'lucide-react';
import { Card } from '../ui/Card';
import { Badge } from '../ui/Badge';

interface RuleConflict {
    winning_rule: {
        id: string;
        name: string;
        source: string;
        priority: number;
        is_enforced: boolean;
    };
    overridden_rule: {
        id: string;
        name: string;
        source: string;
        priority: number;
        is_enforced: boolean;
    };
    conflict_type: string;
    status: 'valid_override' | 'enforced_violation';
    condition: string;
    target_property: string;
}

interface EnforcementViolation {
    blocked_rule_id: string;
    blocked_rule_name: string;
    reason: string;
    enforced_rule_id: string;
}

interface RuleConflictsData {
    project_id: string;
    total_rules: number;
    conflicts_count: number;
    enforcement_violations_count: number;
    conflicts: RuleConflict[];
    enforcement_violations: EnforcementViolation[];
}

interface RuleConflictsProps {
    projectId: string;
    conflictsData: RuleConflictsData | null;
    isLoading: boolean;
    onRefresh: () => void;
}

export function RuleConflicts({ projectId, conflictsData, isLoading, onRefresh }: RuleConflictsProps) {
    if (isLoading) {
        return (
            <Card className="p-6">
                <div className="flex items-center justify-center">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-mining-teal"></div>
                    <span className="ml-3 text-slate-400">Analyzing rule conflicts...</span>
                </div>
            </Card>
        );
    }

    if (!conflictsData) {
        return (
            <Card className="p-6">
                <div className="text-center text-slate-400">
                    <AlertCircle className="w-12 h-12 mx-auto mb-3 opacity-50" />
                    <p>No conflict data available. Click "Check Conflicts" to analyze.</p>
                </div>
            </Card>
        );
    }

    const { conflicts, enforcement_violations, conflicts_count, enforcement_violations_count, total_rules } = conflictsData;

    // Summary Stats
    const hasIssues = conflicts_count > 0 || enforcement_violations_count > 0;

    return (
        <div className="space-y-4">
            {/* Summary Card */}
            <Card className="p-6 bg-slate-900/50 border-slate-700">
                <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-semibold text-slate-200">Conflict Analysis</h3>
                    <Badge variant={hasIssues ? 'warning' : 'success'}>
                        {hasIssues ? `${conflicts_count + enforcement_violations_count} Issues` : 'No Conflicts'}
                    </Badge>
                </div>

                <div className="grid grid-cols-3 gap-4">
                    <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700">
                        <div className="text-2xl font-bold text-mining-teal">{total_rules}</div>
                        <div className="text-sm text-slate-400">Total Rules</div>
                    </div>

                    <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700">
                        <div className="text-2xl font-bold text-amber-500">{conflicts_count}</div>
                        <div className="text-sm text-slate-400">Conflicts</div>
                    </div>

                    <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700">
                        <div className="text-2xl font-bold text-red-500">{enforcement_violations_count}</div>
                        <div className="text-sm text-slate-400">Violations</div>
                    </div>
                </div>
            </Card>

            {/* Enforcement Violations (Critical) */}
            {enforcement_violations_count > 0 && (
                <Card className="p-6 bg-red-950/20 border-red-800">
                    <div className="flex items-center gap-3 mb-4">
                        <Shield className="w-5 h-5 text-red-500" />
                        <h4 className="text-lg font-semibold text-red-400">
                            Enforcement Violations ({enforcement_violations_count})
                        </h4>
                    </div>

                    <div className="space-y-3">
                        {enforcement_violations.map((violation, idx) => (
                            <div
                                key={idx}
                                className="bg-red-950/40 border border-red-800/50 rounded-lg p-4"
                            >
                                <div className="flex items-start justify-between mb-2">
                                    <div>
                                        <div className="flex items-center gap-2 mb-1">
                                            <AlertTriangle className="w-4 h-4 text-red-500" />
                                            <span className="font-medium text-red-300">
                                                {violation.blocked_rule_name}
                                            </span>
                                            <Badge variant="error" className="text-xs">BLOCKED</Badge>
                                        </div>
                                        <p className="text-sm text-slate-400">{violation.reason}</p>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>

                    <div className="mt-4 bg-red-950/30 border border-red-800/30 rounded-lg p-3">
                        <div className="flex items-start gap-2 text-sm text-red-300">
                            <AlertCircle className="w-4 h-4 mt-0.5 flex-shrink-0" />
                            <p>
                                <strong>Enforced rules cannot be overridden.</strong> These are typically legal or safety requirements (e.g., electrical codes). The higher-priority rules listed above are blocked to ensure compliance.
                            </p>
                        </div>
                    </div>
                </Card>
            )}

            {/* Valid Overrides (Informational) */}
            {conflicts_count > 0 && (
                <Card className="p-6 bg-slate-900/50 border-slate-700">
                    <div className="flex items-center gap-3 mb-4">
                        <AlertTriangle className="w-5 h-5 text-amber-500" />
                        <h4 className="text-lg font-semibold text-amber-400">
                            Rule Conflicts ({conflicts_count})
                        </h4>
                    </div>

                    <div className="space-y-3">
                        {conflicts.map((conflict, idx) => {
                            const isViolation = conflict.status === 'enforced_violation';

                            return (
                                <div
                                    key={idx}
                                    className={`rounded-lg p-4 border ${isViolation
                                        ? 'bg-red-950/20 border-red-800/50'
                                        : 'bg-amber-950/20 border-amber-800/50'
                                        }`}
                                >
                                    {/* Conflict Flow */}
                                    <div className="flex items-center gap-3">
                                        {/* Losing Rule */}
                                        <div className="flex-1 bg-slate-800/50 rounded-lg p-3 border border-slate-700">
                                            <div className="flex items-center justify-between mb-1">
                                                <span className="text-sm font-medium text-slate-300">
                                                    {conflict.overridden_rule.name}
                                                </span>
                                                <Badge variant="default" className="text-xs">
                                                    {conflict.overridden_rule.source}
                                                </Badge>
                                            </div>
                                            <div className="flex items-center gap-2 text-xs text-slate-500">
                                                <span>Priority: {conflict.overridden_rule.priority}</span>
                                                {conflict.overridden_rule.is_enforced && (
                                                    <Badge variant="default" className="text-xs">
                                                        <Shield className="w-3 h-3 mr-1" />
                                                        Enforced
                                                    </Badge>
                                                )}
                                            </div>
                                        </div>

                                        {/* Arrow */}
                                        <div className="flex flex-col items-center">
                                            <ChevronRight className={`w-6 h-6 ${isViolation ? 'text-red-500' : 'text-amber-500'}`} />
                                            <span className="text-xs text-slate-500 mt-1">overridden by</span>
                                        </div>

                                        {/* Winning Rule */}
                                        <div className="flex-1 bg-mining-teal/10 rounded-lg p-3 border border-mining-teal/30">
                                            <div className="flex items-center justify-between mb-1">
                                                <span className="text-sm font-medium text-mining-teal">
                                                    {conflict.winning_rule.name}
                                                </span>
                                                <Badge variant="success" className="text-xs">
                                                    {conflict.winning_rule.source}
                                                </Badge>
                                            </div>
                                            <div className="flex items-center gap-2 text-xs text-slate-400">
                                                <span>Priority: {conflict.winning_rule.priority}</span>
                                                {conflict.winning_rule.is_enforced && (
                                                    <Badge variant="default" className="text-xs">
                                                        <Shield className="w-3 h-3 mr-1" />
                                                        Enforced
                                                    </Badge>
                                                )}
                                            </div>
                                        </div>
                                    </div>

                                    {/* Conflict Details */}
                                    <div className="mt-3 pt-3 border-t border-slate-700/50">
                                        <div className="flex items-center gap-4 text-xs text-slate-500">
                                            <span>Target: <span className="text-slate-400">{conflict.target_property}</span></span>
                                            <span>•</span>
                                            <span>Type: <span className="text-slate-400">{conflict.conflict_type}</span></span>
                                            <span>•</span>
                                            <Badge
                                                variant={isViolation ? 'error' : 'warning'}
                                                className="text-xs"
                                            >
                                                {conflict.status.replace('_', ' ')}
                                            </Badge>
                                        </div>
                                    </div>
                                </div>
                            );
                        })}
                    </div>

                    {conflicts.every(c => c.status === 'valid_override') && (
                        <div className="mt-4 bg-amber-950/20 border border-amber-800/30 rounded-lg p-3">
                            <div className="flex items-start gap-2 text-sm text-amber-300">
                                <CheckCircle className="w-4 h-4 mt-0.5 flex-shrink-0" />
                                <p>
                                    All conflicts shown above are <strong>valid overrides</strong> based on rule hierarchy (CLIENT &gt; PROJECT &gt; COUNTRY &gt; FIRM). Lower-priority rules are automatically disabled.
                                </p>
                            </div>
                        </div>
                    )}
                </Card>
            )}

            {/* No Conflicts */}
            {!hasIssues && (
                <Card className="p-6 bg-green-950/20 border-green-800">
                    <div className="flex items-center gap-3">
                        <CheckCircle className="w-6 h-6 text-green-500" />
                        <div>
                            <h4 className="font-semibold text-green-400 mb-1">No Conflicts Detected</h4>
                            <p className="text-sm text-slate-400">
                                All {total_rules} rules are compatible. No enforcement violations or priority conflicts found.
                            </p>
                        </div>
                    </div>
                </Card>
            )}
        </div>
    );
}
