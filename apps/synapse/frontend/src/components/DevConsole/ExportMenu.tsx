import { useState, useRef, useEffect } from 'react'
import { Download, Copy, Share2, FileText, FileJson } from 'lucide-react'
import { useDevConsoleStore } from '../../store/useDevConsoleStore'
import { exportUtils } from '../../utils/exportUtils'

export const ExportMenu = () => {
    const [isOpen, setIsOpen] = useState(false)
    const [copied, setCopied] = useState(false)
    const menuRef = useRef<HTMLDivElement>(null)

    const { getFilteredLogs } = useDevConsoleStore()

    // Close menu on outside click
    useEffect(() => {
        const handleClickOutside = (e: MouseEvent) => {
            if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
                setIsOpen(false)
            }
        }

        document.addEventListener('mousedown', handleClickOutside)
        return () => document.removeEventListener('mousedown', handleClickOutside)
    }, [])

    const handleExport = (type: 'json' | 'csv' | 'copyText' | 'copyJSON' | 'share') => {
        const logs = getFilteredLogs()

        switch (type) {
            case 'json':
                exportUtils.exportToJSON(logs, `logs-${new Date().toISOString()}.json`)
                break
            case 'csv':
                exportUtils.exportToCSV(logs, `logs-${new Date().toISOString()}.csv`)
                break
            case 'copyText':
                exportUtils.copyAsText(logs)
                setCopied(true)
                setTimeout(() => setCopied(false), 2000)
                break
            case 'copyJSON':
                exportUtils.copyAsJSON(logs)
                setCopied(true)
                setTimeout(() => setCopied(false), 2000)
                break
            case 'share':
                const url = exportUtils.generateShareURL(logs)
                navigator.clipboard.writeText(url)
                setCopied(true)
                setTimeout(() => setCopied(false), 2000)
                break
        }

        setIsOpen(false)
    }

    return (
        <div className="relative" ref={menuRef}>
            <button
                onClick={() => setIsOpen(!isOpen)}
                className="p-2 hover:bg-slate-700 rounded transition-colors flex items-center gap-1"
                title="Export logs"
            >
                <Download size={16} />
            </button>

            {isOpen && (
                <div className="absolute right-0 top-full mt-1 bg-slate-800 border border-slate-700 rounded-lg shadow-xl min-w-[200px] z-10">
                    <div className="p-2 space-y-1">
                        {/* Export JSON */}
                        <button
                            onClick={() => handleExport('json')}
                            className="w-full px-3 py-2 text-left text-sm hover:bg-slate-700 rounded flex items-center gap-2 transition-colors"
                        >
                            <FileJson size={14} />
                            Export as JSON
                        </button>

                        {/* Export CSV */}
                        <button
                            onClick={() => handleExport('csv')}
                            className="w-full px-3 py-2 text-left text-sm hover:bg-slate-700 rounded flex items-center gap-2 transition-colors"
                        >
                            <FileText size={14} />
                            Export as CSV
                        </button>

                        <div className="border-t border-slate-700 my-1" />

                        {/* Copy as Text */}
                        <button
                            onClick={() => handleExport('copyText')}
                            className="w-full px-3 py-2 text-left text-sm hover:bg-slate-700 rounded flex items-center gap-2 transition-colors"
                        >
                            <Copy size={14} />
                            {copied ? 'Copied!' : 'Copy as Text'}
                        </button>

                        {/* Copy as JSON */}
                        <button
                            onClick={() => handleExport('copyJSON')}
                            className="w-full px-3 py-2 text-left text-sm hover:bg-slate-700 rounded flex items-center gap-2 transition-colors"
                        >
                            <FileJson size={14} />
                            Copy as JSON
                        </button>

                        <div className="border-t border-slate-700 my-1" />

                        {/* Share URL */}
                        <button
                            onClick={() => handleExport('share')}
                            className="w-full px-3 py-2 text-left text-sm hover:bg-slate-700 rounded flex items-center gap-2 transition-colors"
                        >
                            <Share2 size={14} />
                            Copy Share URL
                        </button>
                    </div>
                </div>
            )}
        </div>
    )
}
