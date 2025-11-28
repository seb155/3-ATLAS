import { useDevConsoleStore, WorkflowGroup, LogEntry } from '../../store/useDevConsoleStore'
import { ChevronRight, ChevronDown, CheckCircle2, XCircle, Loader2, Clock } from 'lucide-react'

export const TimelinePanel = () => {
    const { filters, getFilteredLogs, getFilteredWorkflows } = useDevConsoleStore()

    const logs = getFilteredLogs()
    const workflows = getFilteredWorkflows()

    if (filters.showOnlyWorkflows) {
        return (
            <div className="h-full overflow-y-auto p-3 space-y-2">
                {workflows.length > 0 ? (
                    workflows.map((workflow) => (
                        <WorkflowCard key={workflow.actionId} workflow={workflow} />
                    ))
                ) : (
                    <EmptyState message="No workflows found" />
                )}
            </div>
        )
    }

    return (
        <div className="h-full overflow-y-auto p-3 space-y-1">
            {logs.length > 0 ? (
                logs.map((log) => (
                    <LogRow key={log.id} log={log} />
                ))
            ) : (
                <EmptyState message="No logs to display" />
            )}
        </div>
    )
}

const WorkflowCard = ({ workflow }: { workflow: WorkflowGroup }) => {
    const { expandedWorkflows, toggleWorkflow, selectWorkflow } = useDevConsoleStore()
    const isExpanded = expandedWorkflows.has(workflow.actionId)

    const statusConfig = {
        RUNNING: {
            icon: Loader2,
            color: 'text-blue-400 bg-blue-400/10 border-blue-400/30',
            iconClass: 'animate-spin'
        },
        COMPLETED: {
            icon: CheckCircle2,
            color: 'text-green-400 bg-green-400/10 border-green-400/30',
            iconClass: ''
        },
        FAILED: {
            icon: XCircle,
            color: 'text-red-400 bg-red-400/10 border-red-400/30',
            iconClass: ''
        },
    }

    const config = statusConfig[workflow.status]
    const Icon = config.icon

    const duration = workflow.endTime
        ? Math.round((new Date(workflow.endTime).getTime() - new Date(workflow.startTime).getTime()) / 1000)
        : null

    return (
        <div className={`border rounded-lg overflow-hidden ${config.color}`}>
            {/* Header */}
            <div
                className="flex items-center gap-3 p-3 cursor-pointer hover:bg-white/5 transition-colors"
                onClick={() => toggleWorkflow(workflow.actionId)}
            >
                {/* Expand Icon */}
                <div className="flex-shrink-0">
                    {isExpanded ? (
                        <ChevronDown size={16} className="text-slate-400" />
                    ) : (
                        <ChevronRight size={16} className="text-slate-400" />
                    )}
                </div>

                {/* Status Icon */}
                <Icon size={18} className={`flex-shrink-0 ${config.iconClass}`} />

                {/* Summary */}
                <div className="flex-1 min-w-0">
                    <div className="font-semibold text-sm truncate">{workflow.summary}</div>
                    <div className="text-xs text-slate-500 flex items-center gap-2 mt-0.5">
                        <span>{workflow.actionType}</span>
                        {workflow.userName && <span>• {workflow.userName}</span>}
                        {duration !== null && (
                            <span className="flex items-center gap-1">
                                • <Clock size={10} /> {duration}s
                            </span>
                        )}
                    </div>
                </div>

                {/* Badge */}
                <div className="flex-shrink-0">
                    <div className="px-2 py-0.5 rounded text-xs font-medium bg-slate-700/50">
                        {workflow.logs.length} logs
                    </div>
                </div>
            </div>

            {/* Expanded Logs */}
            {isExpanded && (
                <div className="border-t border-slate-700/50 bg-slate-900/50">
                    <div className="p-2 space-y-1">
                        {workflow.logs.map((log) => (
                            <LogRow key={log.id} log={log} compact />
                        ))}
                    </div>

                    {/* Stats Footer */}
                    {workflow.stats && Object.keys(workflow.stats).length > 0 && (
                        <div className="border-t border-slate-700/50 p-2 text-xs">
                            <div className="text-slate-400 font-medium mb-1">Stats:</div>
                            <div className="flex gap-3">
                                {Object.entries(workflow.stats).map(([key, value]) => (
                                    <div key={key}>
                                        <span className="text-slate-500">{key}:</span>{' '}
                                        <span className="text-white font-mono">{String(value)}</span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            )}
        </div>
    )
}

const LogRow = ({ log, compact = false }: { log: LogEntry; compact?: boolean }) => {
    const { selectLog } = useDevConsoleStore()

    const levelConfig = {
        DEBUG: { color: 'text-slate-400', bg: 'bg-slate-400/10' },
        INFO: { color: 'text-blue-400', bg: 'bg-blue-400/10' },
        WARNING: { color: 'text-yellow-400', bg: 'bg-yellow-400/10' },
        ERROR: { color: 'text-red-400', bg: 'bg-red-400/10' },
    }

    const config = levelConfig[log.level]
    const time = new Date(log.timestamp).toLocaleTimeString('en-US', {
        hour12: false,
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        fractionalSecondDigits: 3
    })

    if (compact) {
        return (
            <div
                className="flex items-start gap-2 px-2 py-1 rounded hover:bg-slate-800/50 cursor-pointer text-xs font-mono"
                onClick={() => selectLog(log)}
            >
                <span className="text-slate-600">{time}</span>
                <span className={`px-1.5 py-0.5 rounded font-semibold ${config.bg} ${config.color}`}>
                    {log.level}
                </span>
                <span className="text-slate-300 flex-1 break-all">{log.message}</span>
            </div>
        )
    }

    return (
        <div
            className="flex items-start gap-3 px-3 py-2 rounded hover:bg-slate-800/50 cursor-pointer transition-colors group"
            onClick={() => selectLog(log)}
        >
            {/* Timestamp */}
            <span className="text-slate-500 text-xs font-mono flex-shrink-0 w-24">
                {time}
            </span>

            {/* Level Badge */}
            <span className={`px-2 py-0.5 rounded text-xs font-semibold flex-shrink-0 ${config.bg} ${config.color}`}>
                {log.level}
            </span>

            {/* Source */}
            <span className="text-slate-600 text-xs font-mono flex-shrink-0 w-16">
                {log.source}
            </span>

            {/* Message */}
            <span className="text-slate-200 text-sm flex-1 break-all group-hover:text-white transition-colors">
                {log.message}
            </span>

            {/* Response Time (if available) */}
            {log.responseTime && (
                <span className="text-slate-500 text-xs font-mono flex-shrink-0">
                    {log.responseTime.toFixed(0)}ms
                </span>
            )}
        </div>
    )
}

const EmptyState = ({ message }: { message: string }) => {
    return (
        <div className="flex flex-col items-center justify-center h-full text-slate-500">
            <div className="text-sm">{message}</div>
            <div className="text-xs mt-2">Logs will appear here in real-time</div>
        </div>
    )
}
