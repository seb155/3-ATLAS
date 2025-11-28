/**
 * Custom hook for Package Management & Export
 *
 * Provides:
 * - Package CRUD operations
 * - Asset assignment to packages
 * - Template-based export (IN-P040, CA-P040)
 * - Export preview
 */

import { useState, useCallback } from 'react'
import { apiClient } from '../services/api'

export interface Package {
    id: string
    name: string
    description?: string
    project_id: string
    status: 'OPEN' | 'ISSUED' | 'CLOSED'
    created_at: string
    updated_at: string
    asset_count: number
}

interface PackageAsset {
    id: string
    tag: string
    asset_type: string
    description: string
}

export const usePackages = (projectId: string) => {
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState<string | null>(null)

    // ==========================================================================
    // PACKAGE CRUD
    // ==========================================================================

    const listPackages = useCallback(async (filters?: {
        status?: string
        page?: number
        page_size?: number
    }): Promise<{ packages: Package[], total: number } | null> => {
        try {
            setLoading(true)
            setError(null)

            const response = await apiClient.get('/api/v1/packages', {
                params: filters,
                headers: { 'X-Project-ID': projectId }
            })

            return {
                packages: response.data.packages || [],
                total: response.data.total || 0
            }
        } catch (err: any) {
            const errorMsg = err.response?.data?.detail || 'Failed to fetch packages'
            setError(errorMsg)
            return null
        } finally {
            setLoading(false)
        }
    }, [projectId])

    const getPackage = useCallback(async (packageId: string): Promise<Package | null> => {
        try {
            setLoading(true)
            setError(null)

            const response = await apiClient.get(`/api/v1/packages/${packageId}`, {
                headers: { 'X-Project-ID': projectId }
            })

            return response.data
        } catch (err: any) {
            const errorMsg = err.response?.data?.detail || 'Failed to fetch package'
            setError(errorMsg)
            return null
        } finally {
            setLoading(false)
        }
    }, [projectId])

    const createPackage = useCallback(async (data: {
        name: string
        description?: string
        status?: string
    }): Promise<Package | null> => {
        try {
            setLoading(true)
            setError(null)

            const response = await apiClient.post('/api/v1/packages', data, {
                headers: { 'X-Project-ID': projectId }
            })

            return response.data
        } catch (err: any) {
            const errorMsg = err.response?.data?.detail || 'Failed to create package'
            setError(errorMsg)
            return null
        } finally {
            setLoading(false)
        }
    }, [projectId])

    const updatePackage = useCallback(async (
        packageId: string,
        data: {
            name?: string
            description?: string
            status?: string
        }
    ): Promise<Package | null> => {
        try {
            setLoading(true)
            setError(null)

            const response = await apiClient.patch(`/api/v1/packages/${packageId}`, data, {
                headers: { 'X-Project-ID': projectId }
            })

            return response.data
        } catch (err: any) {
            const errorMsg = err.response?.data?.detail || 'Failed to update package'
            setError(errorMsg)
            return null
        } finally {
            setLoading(false)
        }
    }, [projectId])

    const deletePackage = useCallback(async (packageId: string): Promise<boolean> => {
        try {
            setLoading(true)
            setError(null)

            await apiClient.delete(`/api/v1/packages/${packageId}`, {
                headers: { 'X-Project-ID': projectId }
            })

            return true
        } catch (err: any) {
            const errorMsg = err.response?.data?.detail || 'Failed to delete package'
            setError(errorMsg)
            return false
        } finally {
            setLoading(false)
        }
    }, [projectId])

    // ==========================================================================
    // PACKAGE ASSETS
    // ==========================================================================

    const getPackageAssets = useCallback(async (packageId: string): Promise<{
        package_id: string
        package_name: string
        asset_count: number
        assets: PackageAsset[]
    } | null> => {
        try {
            setLoading(true)
            setError(null)

            const response = await apiClient.get(`/api/v1/packages/${packageId}/assets`, {
                headers: { 'X-Project-ID': projectId }
            })

            return response.data
        } catch (err: any) {
            const errorMsg = err.response?.data?.detail || 'Failed to fetch package assets'
            setError(errorMsg)
            return null
        } finally {
            setLoading(false)
        }
    }, [projectId])

    const addAssetToPackage = useCallback(async (
        packageId: string,
        assetId: string
    ): Promise<boolean> => {
        try {
            setLoading(true)
            setError(null)

            await apiClient.post(`/api/v1/packages/${packageId}/assets/${assetId}`, {}, {
                headers: { 'X-Project-ID': projectId }
            })

            return true
        } catch (err: any) {
            const errorMsg = err.response?.data?.detail || 'Failed to add asset to package'
            setError(errorMsg)
            return false
        } finally {
            setLoading(false)
        }
    }, [projectId])

    const removeAssetFromPackage = useCallback(async (
        packageId: string,
        assetId: string
    ): Promise<boolean> => {
        try {
            setLoading(true)
            setError(null)

            await apiClient.delete(`/api/v1/packages/${packageId}/assets/${assetId}`, {
                headers: { 'X-Project-ID': projectId }
            })

            return true
        } catch (err: any) {
            const errorMsg = err.response?.data?.detail || 'Failed to remove asset from package'
            setError(errorMsg)
            return false
        } finally {
            setLoading(false)
        }
    }, [projectId])

    // ==========================================================================
    // EXPORT
    // ==========================================================================

    const exportPackage = useCallback(async (
        packageId: string,
        templateType: 'IN-P040' | 'CA-P040',
        format: 'xlsx' | 'pdf' = 'xlsx'
    ): Promise<boolean> => {
        try {
            setLoading(true)
            setError(null)

            const response = await apiClient.get(`/api/v1/packages/${packageId}/export`, {
                params: { template_type: templateType, format },
                headers: { 'X-Project-ID': projectId },
                responseType: 'blob' // Important for file download
            })

            // Extract filename from Content-Disposition header
            const contentDisposition = response.headers['content-disposition']
            const filenameMatch = contentDisposition?.match(/filename="(.+)"/)
            const filename = filenameMatch ? filenameMatch[1] : `package_${templateType}.${format}`

            // Create download link
            const url = window.URL.createObjectURL(new Blob([response.data]))
            const link = document.createElement('a')
            link.href = url
            link.setAttribute('download', filename)
            document.body.appendChild(link)
            link.click()
            link.remove()
            window.URL.revokeObjectURL(url)

            return true
        } catch (err: any) {
            const errorMsg = err.response?.data?.detail || 'Export failed'
            setError(errorMsg)
            return false
        } finally {
            setLoading(false)
        }
    }, [projectId])

    const previewExportData = useCallback(async (
        packageId: string,
        templateType: 'IN-P040' | 'CA-P040'
    ): Promise<any | null> => {
        try {
            setLoading(true)
            setError(null)

            const response = await apiClient.get(`/api/v1/packages/${packageId}/export/preview`, {
                params: { template_type: templateType },
                headers: { 'X-Project-ID': projectId }
            })

            return response.data
        } catch (err: any) {
            const errorMsg = err.response?.data?.detail || 'Failed to preview export data'
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

        // CRUD
        listPackages,
        getPackage,
        createPackage,
        updatePackage,
        deletePackage,

        // Assets
        getPackageAssets,
        addAssetToPackage,
        removeAssetFromPackage,

        // Export
        exportPackage,
        previewExportData
    }
}
