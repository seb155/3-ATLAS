import React, { useEffect, useState } from 'react';
import { useLogStore, type LogEntry } from '../store/useLogStore';
import { useAppStore } from '../store/useAppStore';
import { useMetamodelStore } from '../store/useMetamodelStore';
import {
  ChevronDown, ChevronRight, RotateCcw, MousePointerClick,
  FileJson, Edit, X, Trash2
} from 'lucide-react';

const DISCIPLINE_COLORS: Record<string, string> = {
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

  const handleGraphSync = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (log.entityId) {
      setHighlightedNodeId(log.entityId);
      setCurrentView('metamodel');
    }
  };

  const handleEditRule = (e: React.MouseEvent) => {
    e.stopPropagation();
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
          {new Date(log.timestamp.endsWith('Z') ? log.timestamp : log.timestamp + 'Z').toLocaleTimeString()}
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

        {/* Actions Group - Positioned before message for visibility */}
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

export function TraceView() {
  const { getTraceTree, fetchBackendLogs, clearLogs } = useLogStore();
  const [detailsLog, setDetailsLog] = useState<LogEntry | null>(null);

  // Poll for logs
  useEffect(() => {
    const interval = setInterval(() => {
      fetchBackendLogs();
    }, 2000);
    return () => clearInterval(interval);
  }, [fetchBackendLogs]);

  const traceTree = getTraceTree();

  return (
    <>
      <div className="flex flex-col h-full">
        {/* Header */}
        <div className="p-4 border-b border-slate-800 bg-slate-900/50 flex items-center justify-between shrink-0">
          <h3 className="font-bold text-slate-300 flex items-center gap-2 text-sm">
            Execution Trace
          </h3>
          <button
            onClick={clearLogs}
            className="text-xs text-slate-500 hover:text-white transition-colors flex items-center gap-1"
            title="Clear Logs"
          >
            <Trash2 className="w-3 h-3" />
            Clear
          </button>
        </div>

        {/* Trace Tree */}
        <div className="flex-1 p-4 font-mono text-xs overflow-y-auto bg-black/50">
          {traceTree.length === 0 ? (
            <div className="text-gray-500 text-center py-8 italic">No trace data available</div>
          ) : (
            <div className="space-y-0.5">
              {traceTree.map(log => (
                <TraceLogItem key={log.id} log={log} onShowDetails={setDetailsLog} />
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
                  {new Date(detailsLog.timestamp.endsWith('Z') ? detailsLog.timestamp : detailsLog.timestamp + 'Z').toLocaleString()}
                </div>
                <div>
                  <span className="text-gray-500 block mb-1">Level</span>
                  <span className="px-1.5 py-0.5 rounded font-bold bg-blue-600 text-blue-100">
                    {detailsLog.level}
                  </span>
                </div>
                <div>
                  <span className="text-gray-500 block mb-1">Action Type</span>
                  {detailsLog.actionType || '-'}
                </div>
                <div>
                  <span className="text-gray-500 block mb-1">Entity ID</span>
                  <span className="text-xs break-all">{detailsLog.entityId || '-'}</span>
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
