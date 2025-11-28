import { describe, it, expect } from 'vitest'

/**
 * Import Validation Tests
 * 
 * Purpose: Ensure all components can be imported without errors
 * Prevents: 500 errors due to incorrect import paths
 */

describe('Component Imports', () => {
    it('should import DevConsoleV3 without errors', async () => {
        const module = await import('../components/DevConsoleV3')
        expect(module.DevConsoleV3).toBeDefined()
    })

    it('should import TimelinePanel without errors', async () => {
        const module = await import('../components/DevConsole/TimelinePanel')
        expect(module.TimelinePanel).toBeDefined()
    })

    it('should import FilterBar without errors', async () => {
        const module = await import('../components/DevConsole/FilterBar')
        expect(module.FilterBar).toBeDefined()
    })

    it('should import DetailsPanel without errors', async () => {
        const module = await import('../components/DevConsole/DetailsPanel')
        expect(module.DetailsPanel).toBeDefined()
    })
})

describe('Store Imports', () => {
    it('should import useDevConsoleStore without errors', async () => {
        const module = await import('../store/useDevConsoleStore')
        expect(module.useDevConsoleStore).toBeDefined()
    })
})

describe('Hook Imports', () => {
    it('should import useWebSocketConnection without errors', async () => {
        const module = await import('../hooks/useWebSocketConnection')
        expect(module.useWebSocketConnection).toBeDefined()
    })
})
