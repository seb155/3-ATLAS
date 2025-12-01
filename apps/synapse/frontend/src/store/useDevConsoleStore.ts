import { create } from 'zustand'

// DevConsole V3 Types
export interface LogEntry {
    id: string
    timestamp: string
    level: 'DEBUG' | 'INFO' | 'WARNING' | 'ERROR'
    message: string
    source: 'FRONTEND' | 'BACKEND'

    // DevConsole V3: Workflow fields
    actionId?: string
    actionType?: string
    actionSummary?: string
    actionStatus?: 'RUNNING' | 'COMPLETED' | 'FAILED'
    actionStats?: Record<string, any>

    // User context
    userId?: string
    userName?: string

    // Categorization
    topic?: string
    discipline?: string
    entityId?: string
    entityType?: string
    entityTag?: string
    entityRoute?: string

    // Performance
    responseTime?: number

    // Context data
    context?: Record<string, any>
    parentId?: string
}

export interface WorkflowGroup {
    actionId: string
    actionType: string
    summary: string
    status: 'RUNNING' | 'COMPLETED' | 'FAILED'
    startTime: string
    endTime?: string
    logs: LogEntry[]
    stats?: Record<string, any>
    userId?: string
    userName?: string
}

export interface DevConsoleFilters {
    level: 'ALL' | 'DEBUG' | 'INFO' | 'WARNING' | 'ERROR'
    source: 'ALL' | 'FRONTEND' | 'BACKEND'
    topic: 'ALL' | string
    discipline: 'ALL' | string
    timeRange: 'ALL' | 'LAST_5MIN' | 'LAST_HOUR' | 'TODAY'
    searchText: string
    showOnlyWorkflows: boolean
}

interface DevConsoleState {
    // Connection
    isConnected: boolean
    connectionError: string | null

    // Logs
    logs: LogEntry[]
    workflows: WorkflowGroup[]
    maxLogs: number

    // Filters
    filters: DevConsoleFilters

    // UI State
    isPanelOpen: boolean
    selectedLog: LogEntry | null
    selectedWorkflow: WorkflowGroup | null
    expandedWorkflows: Set<string>

    // Actions
    addLog: (log: LogEntry) => void
    clearLogs: () => void
    setFilter: (key: keyof DevConsoleFilters, value: any) => void
    resetFilters: () => void
    togglePanel: () => void
    selectLog: (log: LogEntry | null) => void
    selectWorkflow: (workflow: WorkflowGroup | null) => void
    toggleWorkflow: (actionId: string) => void
    setConnected: (connected: boolean) => void
    setConnectionError: (error: string | null) => void

    // Computed
    getFilteredLogs: () => LogEntry[]
    getFilteredWorkflows: () => WorkflowGroup[]
}

const defaultFilters: DevConsoleFilters = {
    level: 'ALL',
    source: 'ALL',
    topic: 'ALL',
    discipline: 'ALL',
    timeRange: 'ALL',
    searchText: '',
    showOnlyWorkflows: false,
}

export const useDevConsoleStore = create<DevConsoleState>((set, get) => ({
    // Initial state
    isConnected: false,
    connectionError: null,
    logs: [],
    workflows: [],
    maxLogs: 1000,
    filters: defaultFilters,
    isPanelOpen: false,
    selectedLog: null,
    selectedWorkflow: null,
    expandedWorkflows: new Set(),

    // Actions
    addLog: (log: LogEntry) => {
        set((state) => {
            const newLogs = [...state.logs, log]

            // Trim to maxLogs
            if (newLogs.length > state.maxLogs) {
                newLogs.shift()
            }

            // Update workflows if this log has an actionId
            const newWorkflows = [...state.workflows]
            if (log.actionId) {
                const existingWorkflow = newWorkflows.find(w => w.actionId === log.actionId)

                if (existingWorkflow) {
                    // Update existing workflow
                    existingWorkflow.logs.push(log)
                    if (log.actionStatus) {
                        existingWorkflow.status = log.actionStatus
                    }
                    if (log.actionStats) {
                        existingWorkflow.stats = log.actionStats
                    }
                    if (log.actionStatus === 'COMPLETED' || log.actionStatus === 'FAILED') {
                        existingWorkflow.endTime = log.timestamp
                    }
                } else if (log.actionType && log.actionSummary) {
                    // Create new workflow
                    newWorkflows.push({
                        actionId: log.actionId,
                        actionType: log.actionType,
                        summary: log.actionSummary,
                        status: log.actionStatus || 'RUNNING',
                        startTime: log.timestamp,
                        logs: [log],
                        stats: log.actionStats,
                        userId: log.userId,
                        userName: log.userName,
                    })
                }
            }

            return { logs: newLogs, workflows: newWorkflows }
        })
    },

    clearLogs: () => set({ logs: [], workflows: [], selectedLog: null, selectedWorkflow: null }),

    setFilter: (key, value) => set((state) => ({
        filters: { ...state.filters, [key]: value }
    })),

    resetFilters: () => set({ filters: defaultFilters }),

    togglePanel: () => set((state) => ({ isPanelOpen: !state.isPanelOpen })),

    selectLog: (log) => set({ selectedLog: log }),

    selectWorkflow: (workflow) => set({ selectedWorkflow: workflow }),

    toggleWorkflow: (actionId) => set((state) => {
        const newExpanded = new Set(state.expandedWorkflows)
        if (newExpanded.has(actionId)) {
            newExpanded.delete(actionId)
        } else {
            newExpanded.add(actionId)
        }
        return { expandedWorkflows: newExpanded }
    }),

    setConnected: (connected) => set({ isConnected: connected }),

    setConnectionError: (error) => set({ connectionError: error }),

    // Computed getters
    getFilteredLogs: () => {
        const { logs, filters } = get()

        return logs.filter((log) => {
            // Level filter
            if (filters.level !== 'ALL' && log.level !== filters.level) return false

            // Source filter
            if (filters.source !== 'ALL' && log.source !== filters.source) return false

            // Topic filter
            if (filters.topic !== 'ALL' && log.topic !== filters.topic) return false

            // Discipline filter
            if (filters.discipline !== 'ALL' && log.discipline !== filters.discipline) return false

            // Search text
            if (filters.searchText && !log.message.toLowerCase().includes(filters.searchText.toLowerCase())) {
                return false
            }

            // Time range filter
            if (filters.timeRange !== 'ALL') {
                const logTime = new Date(log.timestamp).getTime()
                const now = Date.now()

                switch (filters.timeRange) {
                    case 'LAST_5MIN':
                        if (now - logTime > 5 * 60 * 1000) return false
                        break
                    case 'LAST_HOUR':
                        if (now - logTime > 60 * 60 * 1000) return false
                        break
                    case 'TODAY': {
                        const today = new Date().setHours(0, 0, 0, 0)
                        if (logTime < today) return false
                        break
                    }
                }
            }

            // Workflow filter
            if (filters.showOnlyWorkflows && !log.actionId) return false

            return true
        })
    },

    getFilteredWorkflows: () => {
        const { workflows, filters } = get()

        return workflows.filter((workflow) => {
            // Topic filter
            if (filters.topic !== 'ALL') {
                const hasMatchingLog = workflow.logs.some(log => log.topic === filters.topic)
                if (!hasMatchingLog) return false
            }

            // Search text
            if (filters.searchText) {
                const searchLower = filters.searchText.toLowerCase()
                const matchesSummary = workflow.summary.toLowerCase().includes(searchLower)
                const matchesLog = workflow.logs.some(log =>
                    log.message.toLowerCase().includes(searchLower)
                )
                if (!matchesSummary && !matchesLog) return false
            }

            // Time range
            if (filters.timeRange !== 'ALL') {
                const workflowTime = new Date(workflow.startTime).getTime()
                const now = Date.now()

                switch (filters.timeRange) {
                    case 'LAST_5MIN':
                        if (now - workflowTime > 5 * 60 * 1000) return false
                        break
                    case 'LAST_HOUR':
                        if (now - workflowTime > 60 * 60 * 1000) return false
                        break
                    case 'TODAY': {
                        const todayStart = new Date().setHours(0, 0, 0, 0)
                        if (workflowTime < todayStart) return false
                        break
                    }
                }
            }

            return true
        })
    },
}))
