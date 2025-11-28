import { describe, it, expect, beforeEach } from 'vitest'
import { useDevConsoleStore } from '../store/useDevConsoleStore'

describe('useLogStore', () => {
    beforeEach(() => {
        useDevConsoleStore.getState().clearLogs()
        useDevConsoleStore.getState().resetFilters()
    })

    it('should have initial state', () => {
        const state = useDevConsoleStore.getState()

        expect(state.logs).toEqual([])
        expect(state.isConnected).toBe(false)
        expect(state.filters.level).toBe('ALL')
    })

    it('should add log to store', () => {
        const store = useDevConsoleStore.getState()

        const testLog: any = {
            id: '1',
            timestamp: new Date().toISOString(),
            level: 'INFO',
            message: 'Test message',
            source: 'FRONTEND'
        }

        store.addLog(testLog)

        const state = useDevConsoleStore.getState()
        expect(state.logs).toHaveLength(1)
        expect(state.logs[0].message).toBe('Test message')
    })

    it('should filter logs by level', () => {
        const store = useDevConsoleStore.getState()

        // Add test logs
        store.addLog({
            id: '1',
            timestamp: new Date().toISOString(),
            level: 'INFO',
            message: 'Info message',
            source: 'FRONTEND'
        } as any)

        store.addLog({
            id: '2',
            timestamp: new Date().toISOString(),
            level: 'ERROR',
            message: 'Error message',
            source: 'FRONTEND'
        } as any)

        // Set filter
        store.setFilter('level', 'ERROR')

        const filtered = store.getFilteredLogs()
        expect(filtered).toHaveLength(1)
        expect(filtered[0].level).toBe('ERROR')
    })
})
