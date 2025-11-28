import { useState, useEffect } from 'react'
import { Clock, RotateCcw, ChevronDown, ChevronRight, AlertCircle } from 'lucide-react'
import { apiClient } from '../services/api'

interface AssetVersion {
    version: number
    created_at: string
    created_by: string | null
    change_source: string
    change_reason: string | null
    snapshot: Record<string, any>
}

interface VersionDiff {
    field: string
    old_value: any
    new_value: any
    change_type: 'added' | 'removed' | 'modified'
}

interface AssetHistoryProps {
    assetId: string
    projectId: string
}

export const AssetHistory = ({ assetId, projectId }: AssetHistoryProps) => {
    const [versions, setVersions] = useState<AssetVersion[]>([])
    const [selectedVersion, setSelectedVersion] = useState<number | null>(null)
    const [compareVersion, setCompareVersion] = useState<number | null>(null)
    const [diff, setDiff] = useState<VersionDiff[]>([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)
    const [expandedVersions, setExpandedVersions] = useState<Set<number>>(new Set())

    useEffect(() => {
        loadVersionHistory()
    }, [assetId])

    useEffect(() => {
        if (selectedVersion !== null && compareVersion !== null) {
            loadDiff()
        }
    }, [selectedVersion, compareVersion])

    const loadVersionHistory = async () => {
        try {
            setLoading(true)
            const response = await apiClient.get(`/api/v1/workflow/assets/${assetId}/versions`, {
                headers: { 'X-Project-ID': projectId }
            })
            setVersions(response.data.versions || [])
            setError(null)
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to load version history')
        } finally {
            setLoading(false)
        }
    }

    const loadDiff = async () => {
        if (selectedVersion === null || compareVersion === null) return

        try {
            const response = await apiClient.get(
                `/api/v1/workflow/assets/${assetId}/diff`,
                {
                    params: {
                        from_version: compareVersion,
                        to_version: selectedVersion
                    },
                    headers: { 'X-Project-ID': projectId }
                }
            )
            setDiff(response.data.changes || [])
        } catch (err: any) {
            console.error('Failed to load diff:', err)
        }
    }

    const handleRollback = async (version: number) => {
        if (!confirm(`Rollback to version ${version}? This will create a new version with the old data.`)) {
            return
        }

        try {
            await apiClient.post(
                `/api/v1/workflow/assets/${assetId}/rollback`,
                { target_version: version },
                { headers: { 'X-Project-ID': projectId } }
            )
            // Reload versions
            await loadVersionHistory()
            alert('Rollback successful!')
        } catch (err: any) {
            alert(err.response?.data?.detail || 'Rollback failed')
        }
    }

    const toggleVersion = (version: number) => {
        const newExpanded = new Set(expandedVersions)
        if (newExpanded.has(version)) {
            newExpanded.delete(version)
        } else {
            newExpanded.add(version)
        }
        setExpandedVersions(newExpanded)
    }

    const formatDate = (dateStr: string) => {
        return new Date(dateStr).toLocaleString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        })
    }

    const getChangeTypeColor = (type: string) => {
        switch (type) {
            case 'added': return 'text-green-400 bg-green-400/10'
            case 'removed': return 'text-red-400 bg-red-400/10'
            case 'modified': return 'text-yellow-400 bg-yellow-400/10'
            default: return 'text-slate-400 bg-slate-400/10'
        }
    }

    if (loading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="text-slate-400">Loading version history...</div>
            </div>
        )
    }

    if (error) {
        return (
            <div className="flex items-center gap-2 p-4 bg-red-500/10 border border-red-500/30 rounded text-red-400">
                <AlertCircle size={20} />
                <span>{error}</span>
            </div>
        )
    }

    if (versions.length === 0) {
        return (
            <div className="flex flex-col items-center justify-center h-64 text-slate-500">
                <Clock size={48} className="mb-3 opacity-30" />
                <div className="text-sm">No version history available</div>
            </div>
        )
    }

    return (
        <div className="flex flex-col h-full">
            {/* Header */}
            <div className="p-4 border-b border-slate-700">
                <h3 className="text-lg font-semibold text-white">Asset Version History</h3>
                <p className="text-sm text-slate-400 mt-1">
                    {versions.length} version{versions.length !== 1 ? 's' : ''} recorded
                </p>
            </div>

            {/* Diff View (if comparing) */}
            {selectedVersion !== null && compareVersion !== null && diff.length > 0 && (
                <div className="p-4 bg-slate-800/50 border-b border-slate-700">
                    <div className="text-sm font-semibold text-white mb-3">
                        Changes from v{compareVersion} → v{selectedVersion}
                    </div>
                    <div className="space-y-2">
                        {diff.map((change, idx) => (
                            <div
                                key={idx}
                                className={`p-2 rounded text-xs font-mono ${getChangeTypeColor(change.change_type)}`}
                            >
                                <div className="font-semibold mb-1">{change.field}</div>
                                <div className="flex gap-4">
                                    <div className="flex-1">
                                        <span className="opacity-60">Old: </span>
                                        <span>{JSON.stringify(change.old_value)}</span>
                                    </div>
                                    <div className="flex-1">
                                        <span className="opacity-60">New: </span>
                                        <span>{JSON.stringify(change.new_value)}</span>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Version List */}
            <div className="flex-1 overflow-y-auto p-4 space-y-2">
                {versions.map((version) => (
                    <div
                        key={version.version}
                        className="border border-slate-700 rounded-lg overflow-hidden hover:border-slate-600 transition-colors"
                    >
                        {/* Version Header */}
                        <div
                            className="flex items-center gap-3 p-3 cursor-pointer bg-slate-800/30 hover:bg-slate-800/50"
                            onClick={() => toggleVersion(version.version)}
                        >
                            {/* Expand Icon */}
                            <div className="flex-shrink-0">
                                {expandedVersions.has(version.version) ? (
                                    <ChevronDown size={16} className="text-slate-400" />
                                ) : (
                                    <ChevronRight size={16} className="text-slate-400" />
                                )}
                            </div>

                            {/* Version Badge */}
                            <div className="flex-shrink-0">
                                <div className="px-2 py-1 rounded bg-blue-500/20 text-blue-400 text-xs font-semibold">
                                    v{version.version}
                                </div>
                            </div>

                            {/* Info */}
                            <div className="flex-1 min-w-0">
                                <div className="text-sm text-white font-medium">
                                    {version.change_source}
                                </div>
                                <div className="text-xs text-slate-400 mt-0.5">
                                    {formatDate(version.created_at)}
                                    {version.created_by && ` • ${version.created_by}`}
                                </div>
                                {version.change_reason && (
                                    <div className="text-xs text-slate-500 mt-1 italic">
                                        "{version.change_reason}"
                                    </div>
                                )}
                            </div>

                            {/* Actions */}
                            <div className="flex gap-2">
                                <button
                                    className="px-3 py-1 rounded text-xs bg-slate-700 hover:bg-slate-600 text-white"
                                    onClick={(e) => {
                                        e.stopPropagation()
                                        setSelectedVersion(version.version)
                                        setCompareVersion(version.version > 1 ? version.version - 1 : null)
                                    }}
                                >
                                    Compare
                                </button>
                                {version.version < versions[0].version && (
                                    <button
                                        className="px-3 py-1 rounded text-xs bg-orange-500/20 hover:bg-orange-500/30 text-orange-400 flex items-center gap-1"
                                        onClick={(e) => {
                                            e.stopPropagation()
                                            handleRollback(version.version)
                                        }}
                                    >
                                        <RotateCcw size={12} />
                                        Rollback
                                    </button>
                                )}
                            </div>
                        </div>

                        {/* Expanded Snapshot */}
                        {expandedVersions.has(version.version) && (
                            <div className="p-3 bg-slate-900/50 border-t border-slate-700">
                                <div className="text-xs font-semibold text-slate-400 mb-2">Snapshot:</div>
                                <pre className="text-xs font-mono text-slate-300 overflow-x-auto bg-black/30 p-3 rounded">
                                    {JSON.stringify(version.snapshot, null, 2)}
                                </pre>
                            </div>
                        )}
                    </div>
                ))}
            </div>
        </div>
    )
}
