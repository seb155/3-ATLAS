import React, { useEffect, useState, useRef } from 'react';
import { useLogStore, type LogLevel, type LogEntry, type DisciplineType, type ActionStatus, type LogTopic, type TimeFilter, type UserFilter } from '../store/useLogStore';
import { useAppStore } from '../store/useAppStore';
import { useMetamodelStore } from '../store/useMetamodelStore';
import { FilterChip } from './FilterChip';
import {
  X, Search, Download, Trash2, ChevronUp, ChevronDown, Copy,
  PanelBottom, PanelLeft, Filter, RotateCcw, ChevronRight,
  Activity, Network, AlertCircle, Terminal, MousePointerClick,
  FileJson, Edit, Wrench, User
} from 'lucide-react';

const LOG_LEVEL_COLORS: Record<LogLevel, string> = {
  DEBUG: 'bg-gray-600 text-gray-100',
  INFO: 'bg-blue-600 text-blue-100',
  WARN: 'bg-yellow-600 text-yellow-100',
  ERROR: 'bg-red-600 text-red-100',
};

const LOG_LEVEL_TEXT_COLORS: Record<LogLevel, string> = {
  DEBUG: 'text-gray-400',
  INFO: 'text-blue-400',
  WARN: 'text-yellow-400',
  ERROR: 'text-red-400',
};

const DISCIPLINE_COLORS: Record<DisciplineType, string> = {
  PROCESS: 'text-green-400 border-green-800 bg-green-900/20',
  ELECTRICAL: 'text-yellow-400 border-yellow-800 bg-yellow-900/20',
  AUTOMATION: 'text-blue-400 border-blue-800 bg-blue-900/20',
  MECHANICAL: 'text-orange-400 border-orange-800 bg-orange-900/20',
  PROJECT: 'text-purple-400 border-purple-800 bg-purple-900/20',
  PROCUREMENT: 'text-pink-400 border-pink-800 bg-pink-900/20',
};

// Recursive Tree Item Component
const TraceLogItem = ({ log, depth = 0, onShowDetails }: { log: LogEntry; depth?: number; onShowDetails: (log: LogEntry) => void }) => {
  const [isExpanded, setIsExpanded] = useState(true);
  const { rollbackAction } = useLogStore();
  const { setCurrentView, setSelectedRuleId } = useAppStore();
  const { setHighlightedNodeId } = useMetamodelStore();

  const hasChildren = log.children && log.children.length > 0;
  const isRollbackable = log.actionType === 'CREATE' && log.status !== 'ROLLED_BACK';
  const hasEntity = log.entityId && log.entityType;
  const isRuleExecution = log.actionType === 'RULE_EXECUTION';
  const ruleId = log.context?.rule_id || (isRuleExecution && log.context?.priority ? undefined : undefined); // Try to extract rule ID if available

  const handleGraphSync = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (log.entityId) {
      setHighlightedNodeId(log.entityId);
      setCurrentView('metamodel');
    }
  };

  const handleEditRule = (e: React.MouseEvent) => {
    e.stopPropagation();
    // If we have a rule_id in details, use it. 
    // Note: Top level RULE_EXECUTION logs might not have rule_id directly if they are just "Starting..." 
    // But "Applying rule: X" logs should have it if we logged it.
    // Let's check if we can find the rule ID from the message or details.
    // For now, we rely on details.rule_id being present.
    if (log.context?.rule_id) {
      setSelectedRuleId(log.context.rule_id);
      setCurrentView('rules');
    }
  };

  return (
    <div className="flex flex-col">
      <div
        className={`flex items-center gap-2 hover:bg-gray-800 px-2 py-1 rounded group text-xs font-mono border-l-2 ${log.status === 'ROLLED_BACK' ? 'border-gray-600 opacity-50' :
          log.status === 'FAILED' ? 'border-red-500' : 'border-transparent'
          }`}
        style={{ marginLeft: `${depth * 12}px` }}
      >
        {/* Expand/Collapse */}
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className={`p-0.5 rounded hover:bg-gray-700 ${hasChildren ? 'visible' : 'invisible'}`}
        >
          {isExpanded ? <ChevronDown className="w-3 h-3 text-gray-500" /> : <ChevronRight className="w-3 h-3 text-gray-500" />}
        </button>

        {/* Timestamp */}
        <span className="text-gray-500 whitespace-nowrap">
          {new Date(log.timestamp).toLocaleTimeString()}
        </span>

        {/* Action Type Badge */}
        {log.actionType && (
          <span className={`px-1.5 py-0.5 rounded text-[10px] font-semibold border ${log.actionType === 'ERROR' ? 'border-red-800 bg-red-900/20 text-red-400' :
            log.actionType === 'RULE_EXECUTION' ? 'border-purple-800 bg-purple-900/20 text-purple-400' :
              'border-gray-700 bg-gray-800 text-gray-300'
            }`}>
            {log.actionType}
          </span>
        )}

        {/* Discipline Badge */}
        {log.discipline && (
          <span className={`px-1.5 py-0.5 rounded text-[10px] border ${DISCIPLINE_COLORS[log.discipline]}`}>
            {log.discipline.charAt(0)}
          </span>
        )}

        {/* Message */}
        <span
          className={`flex-1 truncate cursor-pointer hover:underline ${log.status === 'ROLLED_BACK' ? 'line-through text-gray-500' :
            log.level === 'ERROR' ? 'text-red-400' : 'text-gray-300'
            }`}
          onClick={hasEntity ? handleGraphSync : undefined}
          title={hasEntity ? `Click to locate: ${log.message}` : log.message}
        >
          {log.message}
        </span>

        {/* Actions Group */}
        <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">

          {/* Details Button */}
          <button
            onClick={(e) => {
              e.stopPropagation();
              onShowDetails(log);
            }}
            className="text-gray-400 hover:text-white"
            title="View Details"
          >
            <FileJson className="w-3 h-3" />
          </button>

          {/* Graph Sync Icon */}
          {hasEntity && (
            <button
              onClick={handleGraphSync}
              className="text-blue-400 hover:text-blue-300"
              title="Locate in Graph"
            >
              <MousePointerClick className="w-3 h-3" />
            </button>
          )}

          {/* Edit Rule Icon */}
          {/* We show this if we have a rule_id in details */}
          {log.context?.rule_id && (
            <button
              onClick={handleEditRule}
              className="text-purple-400 hover:text-purple-300"
              title="Edit Rule"
            >
              <Edit className="w-3 h-3" />
            </button>
          )}

          {/* Rollback Button */}
          {isRollbackable && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                if (confirm('Are you sure you want to rollback this action?')) {
                  rollbackAction(log.id);
                }
              }}
              className="text-yellow-500 hover:text-yellow-400 flex items-center gap-1"
              title="Rollback Action"
            >
              <RotateCcw className="w-3 h-3" />
            </button>
          )}
        </div>
      </div>

      {/* Children */}
      {isExpanded && hasChildren && (
        <div className="flex flex-col">
          {log.children!.map(child => (
            <TraceLogItem key={child.id} log={child} depth={depth + 1} onShowDetails={onShowDetails} />
          ))}
        </div>
      )}
    </div>
  );
};

export function DevConsole() {
  const {
    isConsoleOpen,
    toggleConsole,
    dockPosition,
    setDockPosition,
    consoleSize,
    setConsoleSize,
    filterLevel,
    setFilterLevel,
    searchQuery,
    setSearchQuery,
    activeTab,
    setActiveTab,
    getFilteredLogs,
    getTraceTree,
    clearLogs,
    fetchBackendLogs,
    selectedDisciplines,
    toggleDisciplineFilter,
    // V2: New Filters
    devMode,
    toggleDevMode,
    userFilter,
    setUserFilter,
    timeFilter,
    setTimeFilter,
    selectedTopics,
    toggleTopicFilter,
    wsState,
    connectWebSocket,
    disconnectWebSocket
  } = useLogStore();

  const [isResizing, setIsResizing] = useState(false);
  const [detailsLog, setDetailsLog] = useState<LogEntry | null>(null); // State for Details Modal
  const consoleRef = useRef<HTMLDivElement>(null);
  const logsEndRef = useRef<HTMLDivElement>(null);

  // WebSocket connection management
  useEffect(() => {
    if (isConsoleOpen) {
      connectWebSocket();
      // Initial fetch for historical logs
      fetchBackendLogs();
    }
    return () => {
      // Don't disconnect on unmount - keep connection for background logs
    };
  }, [isConsoleOpen, connectWebSocket, fetchBackendLogs]);

  // Keyboard shortcut
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.ctrlKey && e.key === '`') {
        e.preventDefault();
        toggleConsole();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [toggleConsole]);

  // Resizing Logic
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!isResizing) return;

      if (dockPosition === 'bottom') {
        const newHeight = window.innerHeight - e.clientY;
        setConsoleSize(Math.max(150, Math.min(newHeight, window.innerHeight - 100)));
      } else {
        const newWidth = window.innerWidth - e.clientX;
        setConsoleSize(Math.max(300, Math.min(newWidth, window.innerWidth - 100)));
      }
    };

    const handleMouseUp = () => setIsResizing(false);

    if (isResizing) {
      window.addEventListener('mousemove', handleMouseMove);
      window.addEventListener('mouseup', handleMouseUp);
    }
    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isResizing, dockPosition, setConsoleSize]);

  // Auto-scroll
  useEffect(() => {
    if (isConsoleOpen && activeTab === 'logs') {
      logsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [getFilteredLogs().length, isConsoleOpen, activeTab]);

  const filteredLogs = getFilteredLogs();
  const traceTree = getTraceTree();
  const errorLogs = filteredLogs.filter((log) => log.level === 'ERROR');
  const networkLogs = filteredLogs.filter((log) => log.source === 'NETWORK');

  const handleExport = () => {
    const data = JSON.stringify(filteredLogs, null, 2);
    const blob = new Blob([data], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `logs-${new Date().toISOString()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleCopyLog = (log: LogEntry) => {
    const text = `[${new Date(log.timestamp).toLocaleTimeString()}] [${log.level}] ${log.message}`;
    navigator.clipboard.writeText(text);
  };

  const logLevels: Array<LogLevel | 'ALL'> = ['ALL', 'DEBUG', 'INFO', 'WARN', 'ERROR'];
  const disciplines: DisciplineType[] = ['PROCESS', 'ELECTRICAL', 'AUTOMATION', 'MECHANICAL', 'PROJECT', 'PROCUREMENT'];

  // V2: New filter constants
  const topics: LogTopic[] = ['ASSETS', 'RULES', 'AUTH', 'PROJECT', 'IMPORT', 'SYSTEM', 'CABLES', 'IO_LISTS'];
  const timeFilters: TimeFilter[] = ['ALL', '5M', '15M', '1H'];
  const userFilters: UserFilter[] = ['MY', 'ALL'];

  if (!isConsoleOpen) {
    return null;
  }

  const containerStyle = dockPosition === 'bottom'
    ? { height: `${consoleSize}px`, bottom: 0, left: 0, right: 0, borderTopWidth: 1 }
    : { width: `${consoleSize}px`, top: 0, bottom: 0, right: 0, borderLeftWidth: 1 };

  return (
    <>
      <div
        ref={consoleRef}
        className={`fixed bg-gray-900 border-gray-700 shadow-2xl z-50 flex flex-col transition-all duration-75 ease-out`}
        style={containerStyle}
      >
        {/* Resize Handle */}
        <div
          className={`absolute bg-transparent hover:bg-blue-500/50 transition-colors z-10 ${dockPosition === 'bottom'
            ? 'top-0 left-0 right-0 h-1 cursor-ns-resize'
            : 'left-0 top-0 bottom-0 w-1 cursor-ew-resize'
            }`}
          onMouseDown={() => setIsResizing(true)}
        />

        {/* Toolbar */}
        <div className="flex items-center justify-between px-2 py-1.5 border-b border-gray-700 bg-gray-900 shrink-0">
          <div className="flex items-center gap-2 overflow-x-auto no-scrollbar">
            {/* Tabs */}
            <div className="flex bg-gray-800 rounded p-0.5">
              <button
                onClick={() => setActiveTab('logs')}
                className={`px-2 py-1 rounded text-xs font-medium flex items-center gap-1.5 ${activeTab === 'logs' ? 'bg-gray-700 text-white shadow-sm' : 'text-gray-400 hover:text-gray-200'
                  }`}
              >
                <Terminal className="w-3.5 h-3.5" />
                Logs
              </button>
              <button
                onClick={() => setActiveTab('trace')}
                className={`px-2 py-1 rounded text-xs font-medium flex items-center gap-1.5 ${activeTab === 'trace' ? 'bg-gray-700 text-white shadow-sm' : 'text-gray-400 hover:text-gray-200'
                  }`}
              >
                <Activity className="w-3.5 h-3.5" />
                Trace
              </button>
              <button
                onClick={() => setActiveTab('errors')}
                className={`px-2 py-1 rounded text-xs font-medium flex items-center gap-1.5 ${activeTab === 'errors' ? 'bg-gray-700 text-white shadow-sm' : 'text-gray-400 hover:text-gray-200'
                  }`}
              >
                <AlertCircle className="w-3.5 h-3.5" />
                Errors
                {errorLogs.length > 0 && (
                  <span className="bg-red-500 text-white text-[10px] px-1 rounded-full">{errorLogs.length}</span>
                )}
              </button>
              <button
                onClick={() => setActiveTab('network')}
                className={`px-2 py-1 rounded text-xs font-medium flex items-center gap-1.5 ${activeTab === 'network' ? 'bg-gray-700 text-white shadow-sm' : 'text-gray-400 hover:text-gray-200'
                  }`}
              >
                <Network className="w-3.5 h-3.5" />
                Network
              </button>
            </div>

            <div className="w-px h-4 bg-gray-700 mx-1" />

            {/* Search */}
            <div className="relative group">
              <Search className="absolute left-2 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-gray-500 group-focus-within:text-blue-400" />
              <input
                type="text"
                placeholder="Search..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-7 pr-2 py-1 bg-gray-800 text-white rounded text-xs border border-gray-700 focus:border-blue-500 focus:outline-none w-32 focus:w-48 transition-all"
              />
            </div>
          </div>

          <div className="flex items-center gap-1">
            {/* Dock Position */}
            <button
              onClick={() => setDockPosition(dockPosition === 'bottom' ? 'right' : 'bottom')}
              className="p-1.5 text-gray-400 hover:text-white hover:bg-gray-800 rounded"
              title={dockPosition === 'bottom' ? "Dock Right" : "Dock Bottom"}
            >
              {dockPosition === 'bottom' ? <PanelLeft className="w-4 h-4" /> : <PanelBottom className="w-4 h-4" />}
            </button>

            {/* WebSocket Status */}
            <div className="flex items-center gap-1.5 px-2">
              <div
                className={`w-2 h-2 rounded-full ${wsState === 'connected' ? 'bg-green-500' :
                  wsState === 'connecting' ? 'bg-yellow-500 animate-pulse' :
                    wsState === 'error' ? 'bg-red-500' : 'bg-gray-500'
                  }`}
                title={`WebSocket: ${wsState}`}
              />
              <span className="text-[10px] text-gray-500">
                {wsState === 'connected' ? 'Live' : wsState === 'connecting' ? '...' : 'Offline'}
              </span>
            </div>

            <div className="w-px h-4 bg-gray-700 mx-1" />

            {/* Clear & Close */}
            <button onClick={clearLogs} className="p-1.5 text-gray-400 hover:text-red-400 hover:bg-gray-800 rounded" title="Clear Logs">
              <Trash2 className="w-4 h-4" />
            </button>
            <button onClick={handleExport} className="p-1.5 text-gray-400 hover:text-blue-400 hover:bg-gray-800 rounded" title="Export Logs">
              <Download className="w-4 h-4" />
            </button>
            <button onClick={toggleConsole} className="p-1.5 text-gray-400 hover:text-white hover:bg-gray-800 rounded" title="Close">
              <ChevronDown className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Filters Bar (Conditional) - V2 Enhanced */}
        {(activeTab === 'trace' || activeTab === 'logs') && (
          <div className="flex flex-col border-b border-gray-800 bg-gray-900/50">
            {/* Row 1: Mode Toggle + User Scope + Time */}
            <div className="flex items-center gap-2 px-2 py-1.5 border-b border-gray-800/50">
              {/* Mode Toggle */}
              <button
                onClick={toggleDevMode}
                className={`px-2 py-1 rounded text-xs font-medium flex items-center gap-1.5 transition-colors ${devMode
                    ? 'bg-orange-600 text-white hover:bg-orange-500'
                    : 'bg-blue-600 text-white hover:bg-blue-500'
                  }`}
                title={devMode ? 'Switch to User Mode' : 'Switch to Dev Mode'}
              >
                {devMode ? <Wrench className="w-3 h-3" /> : <User className="w-3 h-3" />}
                {devMode ? 'Dev' : 'User'}
              </button>

              <div className="w-px h-4 bg-gray-700" />

              {/* User Scope */}
              <div className="flex items-center gap-1">
                <span className="text-[10px] text-gray-500">SCOPE:</span>
                {userFilters.map((filter) => (
                  <FilterChip
                    key={filter}
                    label={filter}
                    active={userFilter === filter}
                    onClick={() => setUserFilter(filter)}
                    variant={userFilter === filter ? 'primary' : 'default'}
                  />
                ))}
              </div>

              <div className="w-px h-4 bg-gray-700" />

              {/* Time Filter */}
              <div className="flex items-center gap-1">
                <span className="text-[10px] text-gray-500">TIME:</span>
                {timeFilters.map((filter) => (
                  <FilterChip
                    key={filter}
                    label={filter}
                    active={timeFilter === filter}
                    onClick={() => setTimeFilter(filter)}
                    variant={timeFilter === filter ? 'success' : 'default'}
                  />
                ))}
              </div>
            </div>

            {/* Row 2: Topics + Levels + Disciplines */}
            <div className="flex items-center gap-2 px-2 py-1.5 overflow-x-auto no-scrollbar">
              <Filter className="w-3 h-3 text-gray-500 shrink-0" />

              {/* Topic Filters */}
              <div className="flex items-center gap-1 shrink-0">
                <span className="text-[10px] text-gray-500">TOPICS:</span>
                <div className="flex gap-0.5">
                  {topics.map((topic) => (
                    <FilterChip
                      key={topic}
                      label={topic}
                      active={selectedTopics.includes(topic)}
                      onClick={() => toggleTopicFilter(topic)}
                      variant={selectedTopics.includes(topic) ? 'primary' : 'default'}
                    />
                  ))}
                </div>
              </div>

              <div className="w-px h-3 bg-gray-700 shrink-0" />

              {/* Level Filters */}
              <div className="flex items-center gap-1 shrink-0">
                <span className="text-[10px] text-gray-500">LEVEL:</span>
                <div className="flex gap-0.5">
                  {logLevels.map((level) => (
                    <FilterChip
                      key={level}
                      label={level}
                      active={filterLevel === level}
                      onClick={() => setFilterLevel(level)}
                      variant={
                        level === 'ERROR' ? 'danger' :
                          level === 'WARN' ? 'warning' :
                            filterLevel === level ? 'primary' : 'default'
                      }
                    />
                  ))}
                </div>
              </div>

              <div className="w-px h-3 bg-gray-700 shrink-0" />

              {/* Discipline Filters */}
              <div className="flex items-center gap-1 shrink-0">
                <span className="text-[10px] text-gray-500">DISCIPLINE:</span>
                <div className="flex gap-0.5">
                  {disciplines.map((d) => (
                    <FilterChip
                      key={d}
                      label={d.charAt(0) + d.slice(1, 3).toLowerCase()}
                      active={selectedDisciplines.includes(d)}
                      onClick={() => toggleDisciplineFilter(d)}
                      variant={selectedDisciplines.includes(d) ? 'success' : 'default'}
                    />
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Content Area */}
        <div className="flex-1 overflow-y-auto p-2 font-mono text-xs bg-gray-900">

          {/* TRACE TAB */}
          {activeTab === 'trace' && (
            <div className="space-y-0.5">
              {traceTree.length === 0 ? (
                <div className="text-gray-500 text-center py-8 italic">No trace data available</div>
              ) : (
                traceTree.map(log => (
                  <TraceLogItem key={log.id} log={log} onShowDetails={setDetailsLog} />
                ))
              )}
            </div>
          )}

          {/* LOGS TAB */}
          {activeTab === 'logs' && (
            <div className="space-y-0.5">
              {filteredLogs.length === 0 ? (
                <div className="text-gray-500 text-center py-8 italic">No logs to display</div>
              ) : (
                filteredLogs.map((log) => (
                  <div key={log.id} className="flex gap-2 hover:bg-gray-800 px-2 py-1 rounded group items-start">
                    <span className="text-gray-500 whitespace-nowrap shrink-0">
                      {new Date(log.timestamp).toLocaleTimeString()}
                    </span>
                    <span className={`px-1.5 py-0.5 rounded text-[10px] font-bold whitespace-nowrap shrink-0 ${LOG_LEVEL_COLORS[log.level]}`}>
                      {log.level}
                    </span>
                    <span className="text-gray-500 whitespace-nowrap shrink-0 w-16 truncate" title={log.source}>
                      [{log.source}]
                    </span>
                    <div className="flex-1 min-w-0">
                      <span className={`${LOG_LEVEL_TEXT_COLORS[log.level]} break-words`}>
                        {log.message}
                      </span>
                      {log.context && (
                        <pre className="mt-1 text-[10px] text-gray-500 bg-gray-950/50 p-1.5 rounded overflow-x-auto">
                          {JSON.stringify(log.context, null, 2)}
                        </pre>
                      )}
                    </div>
                    <button
                      onClick={() => handleCopyLog(log)}
                      className="opacity-0 group-hover:opacity-100 text-gray-500 hover:text-white transition-opacity shrink-0"
                      title="Copy"
                    >
                      <Copy className="w-3 h-3" />
                    </button>
                  </div>
                ))
              )}
              <div ref={logsEndRef} />
            </div>
          )}

          {/* ERRORS TAB */}
          {activeTab === 'errors' && (
            <div className="space-y-2">
              {errorLogs.map((log) => (
                <div key={log.id} className="bg-red-900/10 border border-red-900/30 rounded p-2 group">
                  <div className="flex justify-between items-start">
                    <span className="text-red-400 font-semibold">{log.message}</span>
                    <span className="text-gray-500">{new Date(log.timestamp).toLocaleTimeString()}</span>
                  </div>
                  {log.stack && (
                    <pre className="mt-2 text-[10px] text-red-300/70 bg-gray-950 p-2 rounded overflow-x-auto whitespace-pre-wrap">
                      {log.stack}
                    </pre>
                  )}
                </div>
              ))}
            </div>
          )}

          {/* NETWORK TAB */}
          {activeTab === 'network' && (
            <div className="space-y-0.5">
              {networkLogs.map((log) => (
                <div key={log.id} className="flex gap-2 hover:bg-gray-800 px-2 py-1 rounded">
                  <span className="text-gray-500">{new Date(log.timestamp).toLocaleTimeString()}</span>
                  <span className="text-purple-400">{log.message}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Details Modal */}
      {detailsLog && (
        <div className="fixed inset-0 bg-black/50 z-[60] flex items-center justify-center p-4">
          <div className="bg-gray-900 border border-gray-700 rounded-lg shadow-2xl w-full max-w-2xl max-h-[80vh] flex flex-col">
            <div className="flex items-center justify-between p-4 border-b border-gray-800">
              <h3 className="text-lg font-semibold text-white flex items-center gap-2">
                <FileJson className="w-5 h-5 text-blue-400" />
                Log Details
              </h3>
              <button
                onClick={() => setDetailsLog(null)}
                className="text-gray-400 hover:text-white"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="p-4 overflow-y-auto font-mono text-xs text-gray-300">
              <div className="mb-4 grid grid-cols-2 gap-4">
                <div>
                  <span className="text-gray-500 block mb-1">Timestamp</span>
                  {new Date(detailsLog.timestamp).toLocaleString()}
                </div>
                <div>
                  <span className="text-gray-500 block mb-1">Level</span>
                  <span className={`px-1.5 py-0.5 rounded font-bold ${LOG_LEVEL_COLORS[detailsLog.level]}`}>
                    {detailsLog.level}
                  </span>
                </div>
                <div>
                  <span className="text-gray-500 block mb-1">Action Type</span>
                  {detailsLog.actionType || '-'}
                </div>
                <div>
                  <span className="text-gray-500 block mb-1">Entity ID</span>
                  {detailsLog.entityId || '-'}
                </div>
              </div>

              <div className="mb-2">
                <span className="text-gray-500 block mb-1">Message</span>
                <div className="bg-gray-950 p-2 rounded border border-gray-800">
                  {detailsLog.message}
                </div>
              </div>

              {detailsLog.context && (
                <div>
                  <span className="text-gray-500 block mb-1">Details Payload</span>
                  <pre className="bg-gray-950 p-2 rounded border border-gray-800 overflow-x-auto">
                    {JSON.stringify(detailsLog.context, null, 2)}
                  </pre>
                </div>
              )}
            </div>
            <div className="p-4 border-t border-gray-800 flex justify-end">
              <button
                onClick={() => setDetailsLog(null)}
                className="px-4 py-2 bg-gray-800 hover:bg-gray-700 text-white rounded"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
