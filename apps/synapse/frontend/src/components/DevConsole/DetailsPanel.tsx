import { useDevConsoleStore } from '../../store/useDevConsoleStore'
import { X, Copy, Check, ChevronRight, Package, Code, AlertTriangle, Clock } from 'lucide-react'
import { useState } from 'react'

export const DetailsPanel = () => {
    const { selectedLog, selectedWorkflow, selectLog, selectWorkflow } = useDevConsoleStore()

    if (selectedWorkflow) {
        return <WorkflowDetails workflow={selectedWorkflow} onClose={() => selectWorkflow(null)} />
    }

    if (selectedLog) {
        return <LogDetails log={selectedLog} onClose={() => selectLog(null)} />
    }

    return <EmptyDetails />
}

const LogDetails = ({ log, onClose }: { log: any; onClose: () => void }) => {
    const [activeTab, setActiveTab] = useState<'overview' | 'payload' | 'stack' | 'timeline'>('overview')
    const [copied, setCopied] = useState(false)

    const copyToClipboard = (text: string) => {
        navigator.clipboard.writeText(text)
        setCopied(true)
        setTimeout(() => setCopied(false), 2000)
    }

    const tabs = [
        { id: 'overview', label: 'Overview', icon: Package },
        { id: 'payload', label: 'Payload', icon: Code },
        { id: 'stack', label: 'Stack', icon: AlertTriangle },
        { id: 'timeline', label: 'Timeline', icon: Clock },
    ] as const

    return (
        <div className="h-full flex flex-col bg-slate-900">
            {/* Header */}
            <div className="flex items-center justify-between p-3 border-b border-slate-700">
                <h3 className="font-semibold text-sm">Log Details</h3>
                <button
                    onClick={onClose}
                    className="p-1 hover:bg-slate-800 rounded transition-colors"
                >
                    <X size={16} />
                </button>
            </div>

            {/* Tabs */}
            <div className="flex border-b border-slate-700 bg-slate-800/50">
                {tabs.map((tab) => {
                    const Icon = tab.icon
                    const isActive = activeTab === tab.id

                    return (
                        <button
                            key={tab.id}
                            onClick={() => setActiveTab(tab.id)}
                            className={`flex items-center gap-2 px-4 py-2 text-sm font-medium transition-colors border-b-2 ${isActive
                                ? 'border-blue-500 text-white bg-slate-900'
                                : 'border-transparent text-slate-400 hover:text-white hover:bg-slate-800'
                                }`}
                        >
                            <Icon size={14} />
                            {tab.label}
                        </button>
                    )
                })}
            </div>

            {/* Tab Content */}
            <div className="flex-1 overflow-y-auto">
                {activeTab === 'overview' && <OverviewTab log={log} onCopy={copyToClipboard} copied={copied} />}
                {activeTab === 'payload' && <PayloadTab log={log} />}
                {activeTab === 'stack' && <StackTab log={log} />}
                {activeTab === 'timeline' && <TimelineTab log={log} />}
            </div>
        </div>
    )
}

const OverviewTab = ({ log, onCopy, copied }: { log: any; onCopy: (text: string) => void; copied: boolean }) => {
    return (
        <div className="p-4 space-y-4 text-sm">
            {/* Message */}
            <Section title="Message">
                <div className="p-3 bg-slate-800 rounded font-mono text-xs break-all leading-relaxed">
                    {log.message}
                </div>
            </Section>

            {/* Metadata Grid */}
            <Section title="Metadata">
                <div className="grid grid-cols-2 gap-3 text-xs">
                    <MetaCard label="Level" value={log.level} color={getLevelColor(log.level)} />
                    <MetaCard label="Source" value={log.source} />
                    <MetaCard label="Topic" value={log.topic || 'N/A'} />
                    <MetaCard label="Discipline" value={log.discipline || 'N/A'} />

                    {log.responseTime && (
                        <MetaCard
                            label="Response Time"
                            value={`${log.responseTime.toFixed(2)}ms`}
                            highlight={log.responseTime > 1000}
                        />
                    )}

                    {log.userId && (
                        <MetaCard label="User" value={log.userName || log.userId} />
                    )}
                </div>
            </Section>

            {/* Timestamp */}
            <Section title="Timestamp">
                <div className="text-xs text-slate-400">
                    {new Date(log.timestamp).toLocaleString('en-US', {
                        timeZone: 'America/Montreal',
                        dateStyle: 'full',
                        timeStyle: 'long'
                    })}
                </div>
            </Section>

            {/* Entity Info */}
            {log.entityId && (
                <Section title="Entity">
                    <div className="space-y-2 text-xs">
                        <MetaRow label="Type" value={log.entityType || 'N/A'} />
                        <MetaRow label="ID" value={log.entityId} />
                        {log.entityTag && <MetaRow label="Tag" value={log.entityTag} />}
                        {log.entityRoute && (
                            <div className="flex items-center gap-2">
                                <span className="text-slate-500">Route:</span>
                                <a
                                    href={log.entityRoute}
                                    className="text-blue-400 hover:text-blue-300 flex items-center gap-1"
                                >
                                    {log.entityRoute}
                                    <ChevronRight size={12} />
                                </a>
                            </div>
                        )}
                    </div>
                </Section>
            )}

            {/* Actions */}
            <div className="pt-2 space-y-2">
                <button
                    onClick={() => onCopy(JSON.stringify(log, null, 2))}
                    className="w-full px-3 py-2 bg-slate-800 hover:bg-slate-700 rounded text-sm flex items-center justify-center gap-2 transition-colors"
                >
                    {copied ? <Check size={14} /> : <Copy size={14} />}
                    {copied ? 'Copied!' : 'Copy as JSON'}
                </button>

                <button
                    onClick={() => onCopy(log.message)}
                    className="w-full px-3 py-2 bg-slate-800 hover:bg-slate-700 rounded text-sm flex items-center justify-center gap-2 transition-colors"
                >
                    <Copy size={14} />
                    Copy Message
                </button>
            </div>
        </div>
    )
}

const PayloadTab = ({ log }: { log: any }) => {
    if (!log.context || Object.keys(log.context).length === 0) {
        return <EmptyTab message="No payload data available" />
    }

    return (
        <div className="p-4">
            <div className="p-3 bg-slate-800 rounded font-mono text-xs overflow-x-auto leading-relaxed">
                <SmartJsonViewer data={log.context} />
            </div>
        </div>
    )
}

const StackTab = ({ log }: { log: any }) => {
    if (!log.context?.stack && !log.context?.error) {
        return <EmptyTab message="No stack trace available" />
    }

    return (
        <div className="p-4">
            {log.context?.error && (
                <div className="mb-4 p-3 bg-red-900/20 border border-red-500/30 rounded">
                    <div className="text-red-400 font-semibold text-sm mb-1">Error</div>
                    <div className="text-red-300 text-xs font-mono">{log.context.error}</div>
                </div>
            )}

            {log.context?.stack && (
                <pre className="p-3 bg-slate-800 rounded font-mono text-xs overflow-x-auto leading-relaxed text-slate-300">
                    {log.context.stack}
                </pre>
            )}
        </div>
    )
}

const TimelineTab = ({ log }: { log: any }) => {
    const { logs } = useDevConsoleStore()

    // Find related logs (same actionId or within 1 second)
    const relatedLogs = logs.filter((l) => {
        if (l.id === log.id) return true
        if (l.actionId && l.actionId === log.actionId) return true

        const timeDiff = Math.abs(new Date(l.timestamp).getTime() - new Date(log.timestamp).getTime())
        return timeDiff < 1000
    }).sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime())

    if (relatedLogs.length === 0) {
        return <EmptyTab message="No related logs found" />
    }

    return (
        <div className="p-4 space-y-2">
            {relatedLogs.map((relatedLog) => {
                const isCurrentLog = relatedLog.id === log.id

                return (
                    <div
                        key={relatedLog.id}
                        className={`p-2 rounded text-xs ${isCurrentLog
                            ? 'bg-blue-500/20 border border-blue-500/30'
                            : 'bg-slate-800 hover:bg-slate-700'
                            }`}
                    >
                        <div className="flex items-center justify-between mb-1">
                            <span className="text-slate-500 font-mono">
                                {new Date(relatedLog.timestamp).toLocaleTimeString('en-US', { timeZone: 'America/Montreal' })}
                            </span>
                            <span className={`px-2 py-0.5 rounded font-semibold ${getLevelBadge(relatedLog.level)}`}>
                                {relatedLog.level}
                            </span>
                        </div>
                        <div className="text-slate-200">{relatedLog.message}</div>
                    </div>
                )
            })}
        </div>
    )
}

const WorkflowDetails = ({ workflow, onClose }: { workflow: any; onClose: () => void }) => {
    const [activeTab, setActiveTab] = useState<'overview' | 'logs'>('overview')

    return (
        <div className="h-full flex flex-col bg-slate-900">
            {/* Header */}
            <div className="flex items-center justify-between p-3 border-b border-slate-700">
                <h3 className="font-semibold text-sm">Workflow Details</h3>
                <button onClick={onClose} className="p-1 hover:bg-slate-800 rounded">
                    <X size={16} />
                </button>
            </div>

            {/* Tabs */}
            <div className="flex border-b border-slate-700 bg-slate-800/50">
                <button
                    onClick={() => setActiveTab('overview')}
                    className={`px-4 py-2 text-sm font-medium border-b-2 ${activeTab === 'overview'
                        ? 'border-blue-500 text-white'
                        : 'border-transparent text-slate-400 hover:text-white'
                        }`}
                >
                    Overview
                </button>
                <button
                    onClick={() => setActiveTab('logs')}
                    className={`px-4 py-2 text-sm font-medium border-b-2 ${activeTab === 'logs'
                        ? 'border-blue-500 text-white'
                        : 'border-transparent text-slate-400 hover:text-white'
                        }`}
                >
                    Logs ({workflow.logs.length})
                </button>
            </div>

            {/* Content */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4 text-sm">
                {activeTab === 'overview' ? (
                    <>
                        <Section title="Summary">
                            <div className="font-medium">{workflow.summary}</div>
                            <div className="text-xs text-slate-500 mt-1">{workflow.actionType}</div>
                        </Section>

                        <Section title="Status">
                            <div className={`inline-block px-2 py-1 rounded text-xs font-semibold ${workflow.status === 'COMPLETED' ? 'bg-green-400/10 text-green-400 border border-green-400/30' :
                                workflow.status === 'FAILED' ? 'bg-red-400/10 text-red-400 border border-red-400/30' :
                                    'bg-blue-400/10 text-blue-400 border border-blue-400/30'
                                }`}>
                                {workflow.status}
                            </div>
                        </Section>

                        <Section title="Timeline">
                            <div className="space-y-1 text-xs">
                                <MetaRow label="Started" value={new Date(workflow.startTime).toLocaleString('en-US', { timeZone: 'America/Montreal' })} />
                                {workflow.endTime && (
                                    <MetaRow label="Ended" value={new Date(workflow.endTime).toLocaleString('en-US', { timeZone: 'America/Montreal' })} />
                                )}
                                {workflow.endTime && (
                                    <MetaRow
                                        label="Duration"
                                        value={`${Math.round((new Date(workflow.endTime).getTime() - new Date(workflow.startTime).getTime()) / 1000)}s`}
                                    />
                                )}
                            </div>
                        </Section>

                        {workflow.stats && Object.keys(workflow.stats).length > 0 && (
                            <Section title="Statistics">
                                <div className="grid grid-cols-2 gap-2">
                                    {Object.entries(workflow.stats).map(([key, value]) => (
                                        <MetaCard key={key} label={key} value={String(value)} />
                                    ))}
                                </div>
                            </Section>
                        )}
                    </>
                ) : (
                    <div className="space-y-2">
                        {workflow.logs.map((log: any) => (
                            <div key={log.id} className="p-2 bg-slate-800 rounded text-xs">
                                <div className="flex items-center justify-between mb-1">
                                    <span className="text-slate-500 font-mono">
                                        {new Date(log.timestamp).toLocaleTimeString('en-US', { timeZone: 'America/Montreal' })}
                                    </span>
                                    <span className={`px-2 py-0.5 rounded font-semibold ${getLevelBadge(log.level)}`}>
                                        {log.level}
                                    </span>
                                </div>
                                <div className="text-slate-200">{log.message}</div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    )
}

const EmptyDetails = () => {
    return (
        <div className="h-full flex items-center justify-center text-slate-500 text-sm p-4 text-center">
            <div>
                <div className="mb-2">No selection</div>
                <div className="text-xs">Click on a log or workflow to see details</div>
            </div>
        </div>
    )
}

const EmptyTab = ({ message }: { message: string }) => {
    return (
        <div className="h-full flex items-center justify-center text-slate-500 text-sm p-4 text-center">
            {message}
        </div>
    )
}

const Section = ({ title, children }: { title: string; children: React.ReactNode }) => {
    return (
        <div>
            <div className="text-xs font-semibold text-slate-400 mb-2">{title}</div>
            {children}
        </div>
    )
}

const MetaRow = ({ label, value }: { label: string; value: string }) => {
    return (
        <div className="flex justify-between">
            <span className="text-slate-500">{label}:</span>
            <span className="text-white font-mono">{value}</span>
        </div>
    )
}

const MetaCard = ({
    label,
    value,
    color,
    highlight = false
}: {
    label: string;
    value: string;
    color?: string;
    highlight?: boolean;
}) => {
    return (
        <div className={`p-2 rounded ${highlight ? 'bg-yellow-500/10 border border-yellow-500/30' : 'bg-slate-800'}`}>
            <div className="text-slate-500 text-xs mb-1">{label}</div>
            <div className={`font-mono text-sm ${color || 'text-white'}`}>{value}</div>
        </div>
    )
}

const getLevelColor = (level: string) => {
    const colors = {
        DEBUG: 'text-slate-400',
        INFO: 'text-blue-400',
        WARNING: 'text-yellow-400',
        ERROR: 'text-red-400',
    }
    return colors[level as keyof typeof colors] || 'text-white'
}

const getLevelBadge = (level: string) => {
    const badges = {
        DEBUG: 'bg-slate-400/10 text-slate-400',
        INFO: 'bg-blue-400/10 text-blue-400',
        WARNING: 'bg-yellow-400/10 text-yellow-400',
        ERROR: 'bg-red-400/10 text-red-400',
    }
    return badges[level as keyof typeof badges] || 'bg-slate-400/10 text-slate-400'
}

// Smart JSON Viewer Component
const SmartJsonViewer = ({ data }: { data: any }) => {
    if (typeof data !== 'object' || data === null) {
        return <SmartValue value={data} />
    }

    return (
        <div className="font-mono text-xs space-y-1">
            {Object.entries(data).map(([key, value]) => (
                <div key={key} className="flex items-start gap-2 hover:bg-white/5 p-0.5 rounded transition-colors">
                    <span className="text-blue-400 flex-shrink-0 font-semibold">{key}:</span>
                    <div className="flex-1 min-w-0">
                        <SmartValue value={value} fieldKey={key} />
                    </div>
                </div>
            ))}
        </div>
    )
}

const SmartValue = ({ value, fieldKey }: { value: any, fieldKey?: string }) => {
    if (value === null) return <span className="text-slate-500 italic">null</span>
    if (typeof value === 'boolean') return <span className="text-yellow-400 font-bold">{String(value)}</span>
    if (typeof value === 'number') return <span className="text-green-400">{value}</span>

    if (typeof value === 'string') {
        // UUID Detection
        const isUUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(value)
        if (isUUID) {
            return (
                <span
                    className="text-orange-400 hover:underline cursor-pointer hover:text-orange-300 transition-colors bg-orange-400/10 px-1 rounded"
                    title="UUID - Click to copy"
                    onClick={(e) => {
                        e.stopPropagation();
                        navigator.clipboard.writeText(value);
                    }}
                >
                    {value}
                </span>
            )
        }
        // Date Detection
        if (!isNaN(Date.parse(value)) && value.length > 10) {
            return <span className="text-teal-300">"{value}"</span>
        }
        return <span className="text-orange-200 break-all">"{value}"</span>
    }

    if (Array.isArray(value)) {
        if (value.length === 0) return <span className="text-slate-500">[]</span>
        return (
            <div className="pl-4 border-l-2 border-slate-700 my-1">
                {value.map((item, i) => (
                    <div key={i} className="my-0.5">
                        <SmartValue value={item} />
                    </div>
                ))}
            </div>
        )
    }

    if (typeof value === 'object') {
        if (Object.keys(value).length === 0) return <span className="text-slate-500">{"{}"}</span>
        return (
            <div className="pl-4 border-l-2 border-slate-700 my-1">
                <SmartJsonViewer data={value} />
            </div>
        )
    }

    return <span>{String(value)}</span>
}
