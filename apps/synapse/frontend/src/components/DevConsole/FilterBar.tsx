import { useDevConsoleStore } from '../../store/useDevConsoleStore'
import { Search, X } from 'lucide-react'

export const FilterBar = ({ searchInputRef }: { searchInputRef?: React.RefObject<HTMLInputElement> }) => {
    const { filters, setFilter, resetFilters } = useDevConsoleStore()

    const hasActiveFilters =
        filters.level !== 'ALL' ||
        filters.source !== 'ALL' ||
        filters.topic !== 'ALL' ||
        filters.timeRange !== 'ALL' ||
        filters.searchText !== '' ||
        filters.showOnlyWorkflows

    return (
        <div className="flex items-center gap-2 px-4 py-2 bg-slate-800/50 border-t border-slate-700">
            {/* Search */}
            <div className="relative flex-1 max-w-md">
                <Search size={14} className="absolute left-2 top-1/2 -translate-y-1/2 text-slate-500" />
                <input
                    ref={searchInputRef}
                    type="text"
                    placeholder="Search logs... (Ctrl+K)"
                    value={filters.searchText}
                    onChange={(e) => setFilter('searchText', e.target.value)}
                    className="w-full pl-8 pr-8 py-1.5 bg-slate-900 border border-slate-700 rounded text-sm text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
                />
                {filters.searchText && (
                    <button
                        onClick={() => setFilter('searchText', '')}
                        className="absolute right-2 top-1/2 -translate-y-1/2 text-slate-500 hover:text-white"
                    >
                        <X size={14} />
                    </button>
                )}
            </div>

            {/* Level Filter */}
            <select
                value={filters.level}
                onChange={(e) => setFilter('level', e.target.value)}
                className="px-3 py-1.5 bg-slate-900 border border-slate-700 rounded text-sm text-white focus:outline-none focus:border-blue-500"
            >
                <option value="ALL">All Levels</option>
                <option value="DEBUG">Debug</option>
                <option value="INFO">Info</option>
                <option value="WARNING">Warning</option>
                <option value="ERROR">Error</option>
            </select>

            {/* Source Filter */}
            <select
                value={filters.source}
                onChange={(e) => setFilter('source', e.target.value)}
                className="px-3 py-1.5 bg-slate-900 border border-slate-700 rounded text-sm text-white focus:outline-none focus:border-blue-500"
            >
                <option value="ALL">All Sources</option>
                <option value="FRONTEND">Frontend</option>
                <option value="BACKEND">Backend</option>
            </select>

            {/* Time Range */}
            <select
                value={filters.timeRange}
                onChange={(e) => setFilter('timeRange', e.target.value)}
                className="px-3 py-1.5 bg-slate-900 border border-slate-700 rounded text-sm text-white focus:outline-none focus:border-blue-500"
            >
                <option value="ALL">All Time</option>
                <option value="LAST_5MIN">Last 5 min</option>
                <option value="LAST_HOUR">Last hour</option>
                <option value="TODAY">Today</option>
            </select>

            {/* Workflow Toggle */}
            <button
                onClick={() => setFilter('showOnlyWorkflows', !filters.showOnlyWorkflows)}
                className={`px-3 py-1.5 rounded text-sm font-medium transition-colors ${filters.showOnlyWorkflows
                        ? 'bg-blue-500 text-white'
                        : 'bg-slate-900 border border-slate-700 text-slate-400 hover:text-white'
                    }`}
            >
                Workflows Only
            </button>

            {/* Reset */}
            {hasActiveFilters && (
                <button
                    onClick={resetFilters}
                    className="px-3 py-1.5 bg-slate-900 border border-slate-700 rounded text-sm text-slate-400 hover:text-white transition-colors flex items-center gap-1"
                    title="Reset all filters"
                >
                    <X size={14} />
                    Reset
                </button>
            )}
        </div>
    )
}
