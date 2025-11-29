/**
 * CommandPalette - Global Search & Navigation
 *
 * Features:
 * - Global search across all entities (assets, rules, cables, etc.)
 * - Fuzzy matching with auto-completion
 * - Quick navigation shortcuts
 * - Quick actions
 * - Keyboard-first navigation
 *
 * Shortcuts:
 * - Ctrl+K / Cmd+K: Open palette
 * - Escape: Close
 * - Arrow keys: Navigate
 * - Enter: Select
 */

import { useEffect, useState, useCallback, useMemo } from 'react';
import { Command } from 'cmdk';
import { useNavigate } from 'react-router-dom';
import {
  Search,
  FileText,
  Settings,
  Terminal,
  HelpCircle,
  Zap,
  FileSpreadsheet,
  ChevronRight,
  Box,
  GitBranch,
  Cable,
  MapPin,
  Upload,
  Download,
  Network,
  LayoutDashboard,
  Plus,
  Play,
  Sparkles,
  Loader2,
  Clock,
  ArrowRight
} from 'lucide-react';
import toast from 'react-hot-toast';
import apiClient from '../../services/apiClient';

// Icon mapping for dynamic results
const iconMap: Record<string, React.ElementType> = {
  LayoutDashboard,
  Box,
  GitBranch,
  Cable,
  MapPin,
  Upload,
  Download,
  Settings,
  Network,
  Plus,
  Play,
  Sparkles,
  Cpu: Box,
  FileText
};

interface SearchResult {
  id: string;
  type: 'asset' | 'rule' | 'cable' | 'location' | 'project' | 'action' | 'navigation';
  title: string;
  subtitle: string | null;
  icon: string | null;
  path: string | null;
  score: number;
  metadata?: Record<string, unknown>;
}

interface SearchResponse {
  query: string;
  total: number;
  results: SearchResult[];
  categories: Record<string, number>;
}

interface CommandPaletteProps {
  isOpen: boolean;
  onClose: () => void;
  onToggleDevConsole?: () => void;
}

export function CommandPalette({ isOpen, onClose, onToggleDevConsole }: CommandPaletteProps) {
  const [search, setSearch] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [recentSearches, setRecentSearches] = useState<string[]>([]);
  const navigate = useNavigate();

  // Debounced search
  useEffect(() => {
    if (!isOpen) return;

    const timer = setTimeout(async () => {
      setIsLoading(true);
      try {
        const response = await apiClient.get<SearchResponse>('/search/', {
          params: { q: search, limit: 15 }
        });
        setResults(response.data.results);
      } catch (error) {
        console.error('Search failed:', error);
        // Fallback to static results on error
        setResults([]);
      } finally {
        setIsLoading(false);
      }
    }, search ? 150 : 0); // Instant for empty, debounced for queries

    return () => clearTimeout(timer);
  }, [search, isOpen]);

  // Load recent searches from localStorage
  useEffect(() => {
    if (isOpen) {
      const recent = localStorage.getItem('synapse-recent-searches');
      if (recent) {
        setRecentSearches(JSON.parse(recent).slice(0, 5));
      }
    }
  }, [isOpen]);

  // Reset search when closed
  useEffect(() => {
    if (!isOpen) {
      setSearch('');
      setResults([]);
    }
  }, [isOpen]);

  const addToRecentSearches = useCallback((query: string) => {
    if (!query || query.length < 2) return;
    const recent = localStorage.getItem('synapse-recent-searches');
    const searches = recent ? JSON.parse(recent) : [];
    const updated = [query, ...searches.filter((s: string) => s !== query)].slice(0, 10);
    localStorage.setItem('synapse-recent-searches', JSON.stringify(updated));
  }, []);

  const handleSelect = useCallback((result: SearchResult) => {
    if (search) {
      addToRecentSearches(search);
    }

    // Handle different result types
    switch (result.type) {
      case 'navigation':
      case 'asset':
      case 'rule':
      case 'cable':
      case 'location':
        if (result.path) {
          navigate(result.path);
          toast.success(`Navigating to ${result.title}`);
        }
        break;

      case 'action':
        handleAction(result);
        break;

      default:
        if (result.path) {
          navigate(result.path);
        }
    }

    onClose();
  }, [navigate, onClose, search, addToRecentSearches]);

  const handleAction = (result: SearchResult) => {
    const action = result.metadata?.action;

    switch (action) {
      case 'create':
        navigate(result.path || '/');
        toast.success(`Creating new ${result.metadata?.entity}`);
        break;

      case 'execute':
        toast.success('Executing rules...');
        // TODO: Trigger rule execution
        break;

      case 'ai':
        toast.success('AI classification started...');
        // TODO: Trigger AI classification
        break;

      default:
        if (result.path) {
          navigate(result.path);
        }
    }
  };

  const handleCommand = (command: string) => {
    switch (command) {
      case 'toggle-devconsole':
        if (onToggleDevConsole) onToggleDevConsole();
        toast.success('Dev Console toggled');
        break;

      case 'show-shortcuts':
        toast('Press Ctrl+/ for shortcuts', { icon: '⌨️' });
        break;

      case 'show-docs':
        window.open('https://docs.synapse.com', '_blank');
        break;
    }

    onClose();
  };

  const getIcon = (iconName: string | null, type: string) => {
    if (iconName && iconMap[iconName]) {
      const Icon = iconMap[iconName];
      return <Icon size={16} />;
    }

    // Fallback icons by type
    switch (type) {
      case 'asset': return <Box size={16} />;
      case 'rule': return <GitBranch size={16} />;
      case 'cable': return <Cable size={16} />;
      case 'location': return <MapPin size={16} />;
      case 'navigation': return <ArrowRight size={16} />;
      case 'action': return <Zap size={16} />;
      default: return <FileText size={16} />;
    }
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'asset': return 'text-blue-400';
      case 'rule': return 'text-purple-400';
      case 'cable': return 'text-orange-400';
      case 'location': return 'text-green-400';
      case 'navigation': return 'text-slate-400';
      case 'action': return 'text-yellow-400';
      default: return 'text-slate-400';
    }
  };

  // Group results by type
  const groupedResults = useMemo(() => {
    const groups: Record<string, SearchResult[]> = {};

    results.forEach(result => {
      const group = result.type === 'navigation' ? 'Navigation' :
                    result.type === 'action' ? 'Actions' :
                    result.type === 'asset' ? 'Assets' :
                    result.type === 'rule' ? 'Rules' :
                    result.type === 'cable' ? 'Cables' :
                    result.type === 'location' ? 'Locations' : 'Other';

      if (!groups[group]) groups[group] = [];
      groups[group].push(result);
    });

    return groups;
  }, [results]);

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-start justify-center pt-[15vh] animate-in fade-in duration-150"
      onClick={onClose}
    >
      <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm" />

      <div
        className="relative w-full max-w-2xl bg-slate-900 border border-slate-700 rounded-xl shadow-2xl overflow-hidden animate-in zoom-in-95 slide-in-from-top-2 duration-200"
        onClick={(e) => e.stopPropagation()}
      >
        <Command className="w-full" shouldFilter={false}>
          {/* Search Input */}
          <div className="flex items-center border-b border-slate-800 px-4">
            {isLoading ? (
              <Loader2 className="mr-3 h-5 w-5 shrink-0 text-blue-400 animate-spin" />
            ) : (
              <Search className="mr-3 h-5 w-5 shrink-0 text-slate-400" />
            )}
            <Command.Input
              autoFocus
              value={search}
              onValueChange={setSearch}
              placeholder="Search anything... (assets, rules, cables, actions)"
              className="flex h-14 w-full bg-transparent py-3 text-base outline-none placeholder:text-slate-500 text-slate-200"
            />
            {search && (
              <kbd className="px-2 py-1 text-xs bg-slate-800 text-slate-400 rounded">
                ESC
              </kbd>
            )}
          </div>

          <Command.List className="max-h-[400px] overflow-y-auto overflow-x-hidden custom-scrollbar">
            {/* Empty state */}
            {!isLoading && search && results.length === 0 && (
              <div className="py-12 text-center">
                <Search className="mx-auto h-10 w-10 text-slate-600 mb-3" />
                <p className="text-slate-400">No results found for "{search}"</p>
                <p className="text-sm text-slate-500 mt-1">Try a different search term</p>
              </div>
            )}

            {/* Recent searches (when no query) */}
            {!search && recentSearches.length > 0 && (
              <Command.Group heading="Recent Searches" className="px-2 py-2">
                <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider px-2 py-1 mb-1 flex items-center gap-2">
                  <Clock size={12} />
                  Recent
                </div>
                {recentSearches.map((recent, idx) => (
                  <Command.Item
                    key={`recent-${idx}`}
                    value={`recent-${recent}`}
                    onSelect={() => setSearch(recent)}
                    className="flex items-center gap-3 px-3 py-2 rounded-lg cursor-pointer hover:bg-slate-800 text-slate-300 aria-selected:bg-slate-800 aria-selected:text-white"
                  >
                    <Clock size={14} className="text-slate-500" />
                    <span>{recent}</span>
                  </Command.Item>
                ))}
              </Command.Group>
            )}

            {/* Grouped results */}
            {Object.entries(groupedResults).map(([groupName, groupResults]) => (
              <Command.Group key={groupName} heading={groupName} className="px-2 py-2">
                <div className="text-xs font-semibold text-mining-teal uppercase tracking-wider px-2 py-1 mb-1">
                  {groupName}
                  <span className="ml-2 text-slate-500 normal-case">({groupResults.length})</span>
                </div>
                {groupResults.map((result) => (
                  <Command.Item
                    key={result.id}
                    value={`${result.type}-${result.id}-${result.title}`}
                    onSelect={() => handleSelect(result)}
                    className="flex items-center gap-3 px-3 py-2.5 rounded-lg cursor-pointer hover:bg-slate-800 text-slate-300 aria-selected:bg-slate-800 aria-selected:text-white group"
                  >
                    <span className={getTypeColor(result.type)}>
                      {getIcon(result.icon, result.type)}
                    </span>
                    <div className="flex-1 min-w-0">
                      <div className="font-medium truncate">{result.title}</div>
                      {result.subtitle && (
                        <div className="text-xs text-slate-500 truncate">{result.subtitle}</div>
                      )}
                    </div>
                    {result.score > 0 && search && (
                      <span className="text-xs text-slate-600 opacity-0 group-hover:opacity-100 transition-opacity">
                        {result.score}%
                      </span>
                    )}
                    <ChevronRight
                      size={14}
                      className="text-slate-600 opacity-0 group-hover:opacity-100 group-aria-selected:opacity-100 transition-opacity"
                    />
                  </Command.Item>
                ))}
              </Command.Group>
            ))}

            {/* Developer Tools (always visible) */}
            {(!search || search.toLowerCase().includes('dev') || search.toLowerCase().includes('console')) && (
              <Command.Group heading="Developer Tools" className="px-2 py-2">
                <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider px-2 py-1 mb-1">
                  Developer Tools
                </div>
                <Command.Item
                  value="toggle-devconsole"
                  onSelect={() => handleCommand('toggle-devconsole')}
                  className="flex items-center gap-3 px-3 py-2 rounded-lg cursor-pointer hover:bg-slate-800 text-slate-300 aria-selected:bg-slate-800"
                >
                  <Terminal size={16} className="text-green-400" />
                  <span>Toggle DevConsole</span>
                  <kbd className="ml-auto text-xs text-slate-500 bg-slate-800 px-1.5 py-0.5 rounded">Ctrl+`</kbd>
                </Command.Item>
                <Command.Item
                  value="show-shortcuts"
                  onSelect={() => handleCommand('show-shortcuts')}
                  className="flex items-center gap-3 px-3 py-2 rounded-lg cursor-pointer hover:bg-slate-800 text-slate-300 aria-selected:bg-slate-800"
                >
                  <HelpCircle size={16} className="text-blue-400" />
                  <span>Keyboard Shortcuts</span>
                  <kbd className="ml-auto text-xs text-slate-500 bg-slate-800 px-1.5 py-0.5 rounded">Ctrl+/</kbd>
                </Command.Item>
              </Command.Group>
            )}
          </Command.List>

          {/* Footer */}
          <div className="px-4 py-2.5 border-t border-slate-800 bg-slate-900/80 flex items-center justify-between text-xs text-slate-500">
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-1.5">
                <kbd className="px-1.5 py-0.5 bg-slate-800 rounded text-slate-400">↑↓</kbd>
                <span>Navigate</span>
              </div>
              <div className="flex items-center gap-1.5">
                <kbd className="px-1.5 py-0.5 bg-slate-800 rounded text-slate-400">↵</kbd>
                <span>Select</span>
              </div>
              <div className="flex items-center gap-1.5">
                <kbd className="px-1.5 py-0.5 bg-slate-800 rounded text-slate-400">esc</kbd>
                <span>Close</span>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-slate-600">Powered by</span>
              <span className="text-mining-teal font-medium">SYNAPSE Search</span>
            </div>
          </div>
        </Command>
      </div>
    </div>
  );
}
