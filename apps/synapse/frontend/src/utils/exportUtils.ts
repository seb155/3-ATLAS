import { LogEntry } from '../store/useDevConsoleStore'

export const exportUtils = {
    /**
     * Export logs to JSON
     */
    exportToJSON: (logs: LogEntry[], filename = 'logs.json') => {
        const dataStr = JSON.stringify(logs, null, 2)
        const dataBlob = new Blob([dataStr], { type: 'application/json' })
        const url = URL.createObjectURL(dataBlob)

        const link = document.createElement('a')
        link.href = url
        link.download = filename
        link.click()

        URL.revokeObjectURL(url)
    },

    /**
     * Export logs to CSV
     */
    exportToCSV: (logs: LogEntry[], filename = 'logs.csv') => {
        // CSV headers
        const headers = ['Timestamp', 'Level', 'Source', 'Message', 'Topic', 'User', 'Response Time']

        // CSV rows
        const rows = logs.map(log => [
            new Date(log.timestamp).toISOString(),
            log.level,
            log.source,
            `"${log.message.replace(/"/g, '""')}"`, // Escape quotes
            log.topic || '',
            log.userName || log.userId || '',
            log.responseTime?.toFixed(2) || ''
        ])

        // Combine
        const csvContent = [
            headers.join(','),
            ...rows.map(row => row.join(','))
        ].join('\n')

        const dataBlob = new Blob([csvContent], { type: 'text/csv' })
        const url = URL.createObjectURL(dataBlob)

        const link = document.createElement('a')
        link.href = url
        link.download = filename
        link.click()

        URL.revokeObjectURL(url)
    },

    /**
     * Copy logs to clipboard as text
     */
    copyAsText: (logs: LogEntry[]) => {
        const text = logs.map(log => {
            const timestamp = new Date(log.timestamp).toLocaleString()
            return `[${timestamp}] [${log.level}] [${log.source}] ${log.message}`
        }).join('\n')

        navigator.clipboard.writeText(text)
    },

    /**
     * Copy logs to clipboard as JSON
     */
    copyAsJSON: (logs: LogEntry[]) => {
        const json = JSON.stringify(logs, null, 2)
        navigator.clipboard.writeText(json)
    },

    /**
     * Generate shareable URL (future feature)
     */
    generateShareURL: (logs: LogEntry[]): string => {
        // For now, just encode first 10 logs
        const limitedLogs = logs.slice(0, 10)
        const encoded = btoa(JSON.stringify(limitedLogs))
        return `${window.location.origin}/logs?data=${encoded}`
    }
}
