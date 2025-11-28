/**
 * Custom hook for Workflow & Traceability API
 *
 * Provides easy access to:
 * - Workflow events query
 * - Asset version history
 * - Version diff comparison
 * - Rollback operations
 * - Batch operations
 */

import { useState, useCallback } from 'react'
import { apiClient } from '../services/api'

interface WorkflowEvent {
    id: string
    timestamp: string
    level: string
    source: string
    action_type: string
    message: string
    entity_type?: string
    entity_id?: string
    entity_tag?: string
    correlation_id?: string
}

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

interface BatchOperation {
    id: string
    operation_type: string
    description: string
    created_at: string
    asset_count: number
    status: string
}

export const useWorkflowAPI = (projectId: string) => {
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState<string | null>(null)

    // ==========================================================================
    // WORKFLOW EVENTS
    // ==========================================================================

    const getWorkflowEvents = useCallback(async (filters?: {
        start_date?: string
        end_date?: string
        level?: string
        source?: string
        action_type?: string
        entity_type?: string
        entity_id?: string
        correlation_id?: string
        page?: number
        page_size?: number
    }): Promise<{ events: WorkflowEvent[], total: number } | null> => {
        try {
            setLoading(true)
            setError(null)

            const response = await apiClient.get('/api/v1/workflow/events', {
                params: filters,
                headers: { 'X-Project-ID': projectId }
            })

            return {
                events: response.data.events || [],
                total: response.data.total || 0
            }
        } catch (err: any) {
            const errorMsg = err.response?.data?.detail || 'Failed to fetch workflow events'
            setError(errorMsg)
            return null
        } finally {
            setLoading(false)
        }
    }, [projectId])

    const getTimeline = useCallback(async (filters?: {
        hours?: number
        entity_id?: string
        correlation_id?: string
    }): Promise<any[] | null> => {
        try {
            setLoading(true)
            setError(null)

            const response = await apiClient.get('/api/v1/workflow/timeline', {
                params: filters,
                headers: { 'X-Project-ID': projectId }
            })

            return response.data.events || []
        } catch (err: any) {
            const errorMsg = err.response?.data?.detail || 'Failed to fetch timeline'
            setError(errorMsg)
            return null
        } finally {
            setLoading(false)
        }
    }, [projectId])

    // ==========================================================================
    // ASSET VERSIONS
    // ==========================================================================

    const getAssetVersions = useCallback(async (assetId: string): Promise<AssetVersion[] | null> => {
        try {
            setLoading(true)
            setError(null)

            const response = await apiClient.get(`/api/v1/workflow/assets/${assetId}/versions`, {
                headers: { 'X-Project-ID': projectId }
            })

            return response.data.versions || []
        } catch (err: any) {
            const errorMsg = err.response?.data?.detail || 'Failed to fetch asset versions'
            setError(errorMsg)
            return null
        } finally {
            setLoading(false)
        }
    }, [projectId])

    const getVersionDiff = useCallback(async (
        assetId: string,
        fromVersion: number,
        toVersion: number
    ): Promise<VersionDiff[] | null> => {
        try {
            setLoading(true)
            setError(null)

            const response = await apiClient.get(`/api/v1/workflow/assets/${assetId}/diff`, {
                params: {
                    from_version: fromVersion,
                    to_version: toVersion
                },
                headers: { 'X-Project-ID': projectId }
            })

            return response.data.changes || []
        } catch (err: any) {
            const errorMsg = err.response?.data?.detail || 'Failed to fetch version diff'
            setError(errorMsg)
            return null
        } finally {
            setLoading(false)
        }
    }, [projectId])

    const rollbackAsset = useCallback(async (
        assetId: string,
        targetVersion: number
    ): Promise<boolean> => {
        try {
            setLoading(true)
            setError(null)

            await apiClient.post(
                `/api/v1/workflow/assets/${assetId}/rollback`,
                { target_version: targetVersion },
                { headers: { 'X-Project-ID': projectId } }
            )

            return true
        } catch (err: any) {
            const errorMsg = err.response?.data?.detail || 'Rollback failed'
            setError(errorMsg)
            return false
        } finally {
            setLoading(false)
        }
    }, [projectId])

    // ==========================================================================
    // BATCH OPERATIONS
    // ==========================================================================

    const getBatchOperations = useCallback(async (filters?: {
        operation_type?: string
        page?: number
        page_size?: number
    }): Promise<{ batches: BatchOperation[], total: number } | null> => {
        try {
            setLoading(true)
            setError(null)

            const response = await apiClient.get('/api/v1/workflow/batches', {
                params: filters,
                headers: { 'X-Project-ID': projectId }
            })

            return {
                batches: response.data.batches || [],
                total: response.data.total || 0
            }
        } catch (err: any) {
            const errorMsg = err.response?.data?.detail || 'Failed to fetch batch operations'
            setError(errorMsg)
            return null
        } finally {
            setLoading(false)
        }
    }, [projectId])

    const rollbackBatch = useCallback(async (batchId: string): Promise<boolean> => {
        try {
            setLoading(true)
            setError(null)

            await apiClient.post(
                `/api/v1/workflow/batches/${batchId}/rollback`,
                {},
                { headers: { 'X-Project-ID': projectId } }
            )

            return true
        } catch (err: any) {
            const errorMsg = err.response?.data?.detail || 'Batch rollback failed'
            setError(errorMsg)
            return false
        } finally {
            setLoading(false)
        }
    }, [projectId])

    const getWorkflowStats = useCallback(async (): Promise<any | null> => {
        try {
            setLoading(true)
            setError(null)

            const response = await apiClient.get('/api/v1/workflow/stats', {
                headers: { 'X-Project-ID': projectId }
            })

            return response.data
        } catch (err: any) {
            const errorMsg = err.response?.data?.detail || 'Failed to fetch workflow stats'
            setError(errorMsg)
            return null
        } finally {
            setLoading(false)
        }
    }, [projectId])

    return {
        // State
        loading,
        error,

        // Workflow Events
        getWorkflowEvents,
        getTimeline,

        // Asset Versions
        getAssetVersions,
        getVersionDiff,
        rollbackAsset,

        // Batch Operations
        getBatchOperations,
        rollbackBatch,
        getWorkflowStats
    }
}
