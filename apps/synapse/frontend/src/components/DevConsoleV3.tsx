import { useEffect, useRef } from 'react'
import { useDevConsoleStore } from '../store/useDevConsoleStore'
import { useWebSocketConnection } from '../hooks/useWebSocketConnection'
import { Terminal, X, Trash2, Wifi, WifiOff } from 'lucide-react'
import { TimelinePanel } from './DevConsole/TimelinePanel'
import { FilterBar } from './DevConsole/FilterBar'
import { DetailsPanel } from './DevConsole/DetailsPanel'
import { ExportMenu } from './DevConsole/ExportMenu'
import { exportUtils } from '../utils/exportUtils'

// Animation styles
const slideUpAnimation = `
@keyframes slideUp {
  from {
    transform: translateY(100%);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}
.animate-slide-up {
  animation: slideUp 0.3s ease-out;
}
`

export const DevConsoleV3 = () => {
    const {
        isPanelOpen,
        togglePanel,
        clearLogs,
        isConnected,
        getFilteredLogs,
        selectedLog,
        logs,
    } = useDevConsoleStore()

    const searchInputRef = useRef<HTMLInputElement>(null)

    // Connect to WebSocket
    useWebSocketConnection()

    // Keyboard shortcuts - ONLY when panel is open to avoid conflicts
    useEffect(() => {
        const handleKeyboard = (e: KeyboardEvent) => {
            // Ctrl+` - Toggle panel (works globally)
            if (e.ctrlKey && e.key === '`') {
                e.preventDefault()
                e.stopPropagation()
                togglePanel()
                return
            }

            // All other shortcuts ONLY work when panel is open
            if (!isPanelOpen) return

            // Check if we're in an input
            const target = e.target as HTMLElement
            const isInput = target.tagName === 'INPUT' || target.tagName === 'TEXTAREA'

            // Escape - Close panel
            if (e.key === 'Escape') {
                e.preventDefault()
                e.stopPropagation()
                togglePanel()
                return
            }

            // Ctrl+K - Focus search (even in inputs)
            if (e.ctrlKey && e.key === 'k') {
                e.preventDefault()
                e.stopPropagation()
                searchInputRef.current?.focus()
                return
            }

            // Ctrl+E - Export logs
            if (e.ctrlKey && e.key === 'e') {
                e.preventDefault()
                e.stopPropagation()
                const logs = getFilteredLogs()
                exportUtils.exportToJSON(logs)
                return
            }

            // Ctrl+C - Copy selected log (only if not in input)
            if (e.ctrlKey && e.key === 'c' && !isInput && selectedLog) {
                e.preventDefault()
                e.stopPropagation()
                exportUtils.copyAsJSON([selectedLog])
                return
            }
        }

        window.addEventListener('keydown', handleKeyboard)
        return () => window.removeEventListener('keydown', handleKeyboard)
    }, [isPanelOpen, togglePanel, selectedLog, getFilteredLogs])

    // Inject animation styles
    useEffect(() => {
        const styleId = 'devconsole-animations'
        if (!document.getElementById(styleId)) {
            const style = document.createElement('style')
            style.id = styleId
            style.textContent = slideUpAnimation
            document.head.appendChild(style)
        }
    }, [])

    if (!isPanelOpen) {
        return (
            <button
                onClick={togglePanel}
                className="fixed bottom-4 right-4 bg-slate-800 text-white p-3 rounded-lg shadow-lg hover:bg-slate-700 transition-colors z-50"
                title="Open DevConsole (Ctrl+`)"
            >
                <Terminal size={20} />
            </button>
        )
    }

    return (
        <div className="fixed inset-0 z-50 pointer-events-none">
            {/* Overlay */}
            <div
                className="absolute inset-0 bg-black/20 pointer-events-auto"
                onClick={togglePanel}
            />

            {/* Console Panel */}
            <div className="absolute bottom-0 left-0 right-0 h-[70vh] bg-slate-900 text-white shadow-2xl pointer-events-auto flex flex-col animate-slide-up">
                {/* Header */}
                <div className="flex items-center justify-between px-4 py-2 bg-slate-800 border-b border-slate-700">
                    <div className="flex items-center gap-3">
                        <Terminal size={18} />
                        <h2 className="font-semibold">DevConsole V3</h2>

                        {/* Log Count Badge */}
                        <span className="px-2 py-0.5 bg-blue-500/20 text-blue-400 text-xs font-mono rounded border border-blue-500/30">
                            {logs.length} logs
                        </span>

                        {/* Connection Status */}
                        <div className="flex items-center gap-2 text-sm">
                            {isConnected ? (
                                <>
                                    <Wifi size={14} className="text-green-400" />
                                    <span className="text-green-400">Connected</span>
                                </>
                            ) : (
                                <>
                                    <WifiOff size={14} className="text-red-400" />
                                    <span className="text-red-400">Disconnected</span>
                                </>
                            )}
                        </div>

                        {/* Keyboard Shortcuts Hint */}
                        <div className="text-xs text-slate-500 ml-4">
                            <kbd className="px-1.5 py-0.5 bg-slate-700 rounded">Ctrl+K</kbd> Search •{' '}
                            <kbd className="px-1.5 py-0.5 bg-slate-700 rounded">Ctrl+E</kbd> Export •{' '}
                            <kbd className="px-1.5 py-0.5 bg-slate-700 rounded">Esc</kbd> Close
                        </div>
                    </div>

                    <div className="flex items-center gap-2">
                        {/* Export Menu */}
                        <ExportMenu />

                        {/* Clear Logs */}
                        <button
                            onClick={clearLogs}
                            className="p-2 hover:bg-slate-700 rounded transition-colors"
                            title="Clear logs"
                        >
                            <Trash2 size={16} />
                        </button>

                        {/* Close */}
                        <button
                            onClick={togglePanel}
                            className="p-2 hover:bg-slate-700 rounded transition-colors"
                            title="Close (Ctrl+` or  Esc)"
                        >
                            <X size={16} />
                        </button>
                    </div>
                </div>

                {/* Filter Bar */}
                <FilterBar searchInputRef={searchInputRef} />

                {/* Content - Two Panel Layout */}
                <div className="flex-1 flex overflow-hidden">
                    {/* Timeline Panel */}
                    <div className="flex-1 border-r border-slate-700 overflow-hidden">
                        <TimelinePanel />
                    </div>

                    {/* Details Panel */}
                    <div className="w-96 overflow-hidden">
                        <DetailsPanel />
                    </div>
                </div>
            </div>
        </div>
    )
}
