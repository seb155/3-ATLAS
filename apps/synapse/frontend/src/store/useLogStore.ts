import { create } from 'zustand';
import { API_URL, WS_URL } from '../../config';
import { toast } from 'sonner';

export type LogLevel = 'DEBUG' | 'INFO' | 'WARN' | 'ERROR';
export type LogSource = 'FRONTEND' | 'BACKEND' | 'NETWORK';
export type ActionType = 'RULE_EXECUTION' | 'CREATE' | 'UPDATE' | 'LINK' | 'ERROR';
export type ActionStatus = 'COMPLETED' | 'ROLLED_BACK' | 'FAILED';
export type DisciplineType = 'PROCESS' | 'ELECTRICAL' | 'AUTOMATION' | 'MECHANICAL' | 'PROJECT' | 'PROCUREMENT';

// V2: New Filter Types
export type TimeFilter = 'ALL' | '5M' | '15M' | '1H';
export type LogTopic = 'ASSETS' | 'RULES' | 'AUTH' | 'PROJECT' | 'SYSTEM' | 'IMPORT' | 'CABLES' | 'IO_LISTS';
export type UserFilter = 'MY' | 'ALL';

// WebSocket connection state
type WebSocketState = 'disconnected' | 'connecting' | 'connected' | 'error';

interface BackendAction {
  id: string;
  timestamp: string;
  action_type: string;
  description: string;
  details?: Record<string, unknown>;
  parent_id?: string;
  entity_type?: string;
  entity_id?: string;
  discipline?: DisciplineType;
  status?: ActionStatus;
}

// WebSocket log format from backend
interface WsLogEntry {
  id: string;
  timestamp: string;
  level: LogLevel;
  message: string;
  source?: string;
  actionType?: ActionType;
  entityId?: string;
  entityType?: string;
  discipline?: DisciplineType;
  context?: Record<string, unknown>;
  parentId?: string;
  status?: ActionStatus;
}

export interface LogEntry {
  id: string;
  timestamp: string;
  level: LogLevel;
  source: LogSource;
  message: string;
  context?: Record<string, unknown>;
  stack?: string;

  // Action Log specific fields
  actionType?: ActionType;
  parentId?: string;
  entityType?: string;
  entityId?: string;
  discipline?: DisciplineType;
  status?: ActionStatus;
  children?: LogEntry[]; // For tree view

  // V2: Topic & Entity Navigation
  topic?: LogTopic;
  entityTag?: string;      // Human-readable tag (e.g., "P-101")
  userId?: string;         // Who triggered this action
}

interface LogStore {
  logs: LogEntry[];
  isConsoleOpen: boolean;
  dockPosition: 'bottom' | 'right';
  consoleSize: number; // Height for bottom, Width for right
  filterLevel: LogLevel | 'ALL';
  searchQuery: string;
  activeTab: 'logs' | 'trace' | 'errors' | 'network' | 'performance';

  // V2: New Filters
  timeFilter: TimeFilter;
  selectedTopics: LogTopic[];
  userFilter: UserFilter;
  devMode: boolean;

  // WebSocket
  wsState: WebSocketState;
  wsConnection: WebSocket | null;

  // Filters
  selectedDisciplines: DisciplineType[];

  // Actions
  addLog: (log: Omit<LogEntry, 'id' | 'timestamp'> & { id?: string; timestamp?: string }) => void;
  clearLogs: () => void;
  toggleConsole: () => void;
  setDockPosition: (position: 'bottom' | 'right') => void;
  setConsoleSize: (size: number) => void;
  setFilterLevel: (level: LogLevel | 'ALL') => void;
  setSearchQuery: (query: string) => void;
  setActiveTab: (tab: 'logs' | 'trace' | 'errors' | 'network' | 'performance') => void;
  toggleDisciplineFilter: (discipline: DisciplineType) => void;

  // V2: New Actions
  setTimeFilter: (filter: TimeFilter) => void;
  toggleTopicFilter: (topic: LogTopic) => void;
  setUserFilter: (filter: UserFilter) => void;
  toggleDevMode: () => void;

  // WebSocket Actions
  connectWebSocket: () => void;
  disconnectWebSocket: () => void;

  // API Actions
  fetchBackendLogs: () => Promise<void>;
  rollbackAction: (actionId: string) => Promise<void>;

  // Getters
  getFilteredLogs: () => LogEntry[];
  getTraceTree: () => LogEntry[];
}

const MAX_LOGS = 1000;

const levelPriority: Record<LogLevel | 'ALL', number> = {
  DEBUG: 0,
  INFO: 1,
  WARN: 2,
  ERROR: 3,
  ALL: -1,
};

// Reconnection settings
let reconnectTimeout: ReturnType<typeof setTimeout> | null = null;
const RECONNECT_DELAY = 3000;

// Helper to detect topic from message/context
const detectTopic = (log: Partial<LogEntry>): LogTopic => {
  const msg = log.message?.toUpperCase() || '';

  if (msg.includes('AUTH') || msg.includes('LOGIN') || msg.includes('TOKEN')) return 'AUTH';
  if (msg.includes('RULE') || log.actionType === 'RULE_EXECUTION') return 'RULES';
  if (msg.includes('ASSET') || log.entityType === 'Asset') return 'ASSETS';
  if (msg.includes('PROJECT')) return 'PROJECT';
  if (msg.includes('IMPORT') || msg.includes('UPLOAD')) return 'IMPORT';
  if (msg.includes('CABLE')) return 'CABLES';
  if (msg.includes('IO LIST') || msg.includes('IO_LIST')) return 'IO_LISTS';

  return 'SYSTEM';
};

export const useLogStore = create<LogStore>((set, get) => ({
  logs: [],
  isConsoleOpen: false,
  dockPosition: 'bottom',
  consoleSize: 300,
  filterLevel: 'ALL',
  searchQuery: '',
  activeTab: 'logs',
  selectedDisciplines: [],
  wsState: 'disconnected',
  wsConnection: null,

  // V2 Defaults
  timeFilter: 'ALL',
  selectedTopics: [],
  userFilter: 'MY',
  devMode: false,

  addLog: (log) => {
    const newLog: LogEntry = {
      ...log,
      id: log.id || `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      timestamp: log.timestamp || new Date().toISOString(),
      topic: log.topic || detectTopic(log), // Auto-detect topic
    };

    set((state) => {
      // Check for duplicates if it's a backend log
      if (newLog.source === 'BACKEND') {
        const exists = state.logs.some(l => l.id === newLog.id);
        if (exists) return {};
      }

      const updatedLogs = [...state.logs, newLog];
      if (updatedLogs.length > MAX_LOGS) {
        updatedLogs.shift();
      }
      return { logs: updatedLogs };
    });
  },

  clearLogs: () => {
    set({ logs: [] });
    const ws = get().wsConnection;
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send('clear');
    }
  },

  toggleConsole: () => set((state) => ({ isConsoleOpen: !state.isConsoleOpen })),

  setDockPosition: (position) => set({ dockPosition: position }),

  setConsoleSize: (size) => set({ consoleSize: size }),

  setFilterLevel: (level) => set({ filterLevel: level }),

  setSearchQuery: (query) => set({ searchQuery: query }),

  setActiveTab: (tab) => set({ activeTab: tab }),

  toggleDisciplineFilter: (discipline) => set((state) => {
    const current = state.selectedDisciplines;
    if (current.includes(discipline)) {
      return { selectedDisciplines: current.filter(d => d !== discipline) };
    } else {
      return { selectedDisciplines: [...current, discipline] };
    }
  }),

  // V2 Actions
  setTimeFilter: (filter) => set({ timeFilter: filter }),

  toggleTopicFilter: (topic) => set((state) => {
    const current = state.selectedTopics;
    if (current.includes(topic)) {
      return { selectedTopics: current.filter(t => t !== topic) };
    } else {
      return { selectedTopics: [...current, topic] };
    }
  }),

  setUserFilter: (filter) => set({ userFilter: filter }),

  toggleDevMode: () => set((state) => ({ devMode: !state.devMode })),

  connectWebSocket: () => {
    const { wsConnection, addLog } = get();

    if (wsConnection && (wsConnection.readyState === WebSocket.OPEN || wsConnection.readyState === WebSocket.CONNECTING)) {
      return;
    }

    if (reconnectTimeout) {
      clearTimeout(reconnectTimeout);
      reconnectTimeout = null;
    }

    set({ wsState: 'connecting' });

    try {
      const ws = new WebSocket(`${WS_URL}/ws/logs`);

      ws.onopen = () => {
        set({ wsState: 'connected', wsConnection: ws });
        addLog({
          level: 'INFO',
          source: 'FRONTEND',
          message: 'WebSocket connected - Real-time logs enabled',
        });
      };

      ws.onmessage = (event) => {
        try {
          if (event.data === 'pong') return;

          const data: WsLogEntry = JSON.parse(event.data);
          addLog({
            id: data.id,
            timestamp: data.timestamp,
            level: data.level || 'INFO',
            source: (data.source as LogSource) || 'BACKEND',
            message: data.message,
            context: data.context,
            actionType: data.actionType,
            entityId: data.entityId,
            entityType: data.entityType,
            discipline: data.discipline,
            parentId: data.parentId,
            status: data.status,
          });
        } catch (e) {
          console.error('Failed to parse WebSocket message:', e);
        }
      };

      ws.onerror = () => {
        set({ wsState: 'error' });
      };

      ws.onclose = () => {
        set({ wsState: 'disconnected', wsConnection: null });

        reconnectTimeout = setTimeout(() => {
          const { isConsoleOpen } = get();
          if (isConsoleOpen) {
            get().connectWebSocket();
          }
        }, RECONNECT_DELAY);
      };

      set({ wsConnection: ws });
    } catch (error) {
      set({ wsState: 'error' });
      console.error('WebSocket connection error:', error);
    }
  },

  disconnectWebSocket: () => {
    const { wsConnection } = get();

    if (reconnectTimeout) {
      clearTimeout(reconnectTimeout);
      reconnectTimeout = null;
    }

    if (wsConnection) {
      wsConnection.close();
      set({ wsConnection: null, wsState: 'disconnected' });
    }
  },

  getFilteredLogs: () => {
    const { logs, filterLevel, searchQuery, selectedDisciplines, timeFilter, selectedTopics, userFilter, devMode } = get();

    let filtered = logs;

    // 1. Filter by level
    if (filterLevel !== 'ALL') {
      const minPriority = levelPriority[filterLevel];
      filtered = filtered.filter((log) => levelPriority[log.level] >= minPriority);
    }

    // 2. Filter by discipline (if any selected)
    if (selectedDisciplines.length > 0) {
      filtered = filtered.filter(log =>
        !log.discipline || selectedDisciplines.includes(log.discipline)
      );
    }

    // 3. Filter by Time (V2)
    if (timeFilter !== 'ALL') {
      const now = Date.now();
      const thresholds: Record<string, number> = {
        '5M': 5 * 60 * 1000,
        '15M': 15 * 60 * 1000,
        '1H': 60 * 60 * 1000,
      };
      const maxAge = thresholds[timeFilter];
      if (maxAge) {
        filtered = filtered.filter(log => {
          const logTime = new Date(log.timestamp).getTime();
          return (now - logTime) <= maxAge;
        });
      }
    }

    // 4. Filter by Topic (V2)
    if (selectedTopics.length > 0) {
      filtered = filtered.filter(log =>
        log.topic && selectedTopics.includes(log.topic)
      );
    }

    // 5. Filter by User (V2)
    if (userFilter === 'MY') {
      // TODO: Get current user from auth store
      // For now, filter by logs without userId (frontend logs) or specific userId
      // This will be implemented when backend sends userId
    }

    // 6. Dev Mode filtering (V2)
    if (!devMode) {
      // User Mode: Hide DEBUG levels and SYSTEM topic
      filtered = filtered.filter(log => {
        // Hide DEBUG
        if (log.level === 'DEBUG') return false;

        // Hide SYSTEM topic (unless ERROR)
        if (log.topic === 'SYSTEM' && log.level !== 'ERROR') return false;

        // Hide NETWORK source (unless ERROR)
        if (log.source === 'NETWORK' && log.level !== 'ERROR') return false;

        return true;
      });
    }

    // 7. Filter by search query
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter((log) =>
        log.message.toLowerCase().includes(query) ||
        log.source.toLowerCase().includes(query) ||
        log.entityTag?.toLowerCase().includes(query) ||
        (log.context && JSON.stringify(log.context).toLowerCase().includes(query))
      );
    }

    return filtered;
  },

  getTraceTree: () => {
    const { logs } = get();
    const backendLogs = logs.filter(l => l.source === 'BACKEND');

    const logMap = new Map<string, LogEntry>();
    backendLogs.forEach(log => {
      logMap.set(log.id, { ...log, children: [] });
    });

    const roots: LogEntry[] = [];

    backendLogs.forEach(originalLog => {
      const log = logMap.get(originalLog.id)!;
      if (log.parentId && logMap.has(log.parentId)) {
        const parent = logMap.get(log.parentId)!;
        parent.children?.push(log);
      } else {
        roots.push(log);
      }
    });

    const sortLogs = (nodes: LogEntry[]) => {
      nodes.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
      nodes.forEach(node => {
        if (node.children) sortLogs(node.children);
      });
    };

    sortLogs(roots);
    return roots;
  },

  fetchBackendLogs: async () => {
    try {
      const { useProjectStore } = await import('./useProjectStore');
      const { useAuthStore } = await import('./useAuthStore');
      const projectId = useProjectStore.getState().currentProject?.id;
      const token = useAuthStore.getState().token;

      if (!projectId || !token) {
        console.warn('No project or token for fetching logs');
        return;
      }

      const response = await fetch(`${API_URL}/api/v1/actions/?project_id=${projectId}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'X-Project-ID': projectId
        }
      });
      if (!response.ok) return;

      const actions: BackendAction[] = await response.json();
      const { addLog } = get();

      actions.forEach((action) => {
        addLog({
          id: action.id,
          timestamp: action.timestamp,
          level: action.action_type === 'ERROR' ? 'ERROR' : 'INFO',
          source: 'BACKEND',
          message: action.description,
          context: action.details,
          actionType: action.action_type as ActionType,
          parentId: action.parent_id,
          entityType: action.entity_type,
          entityId: action.entity_id,
          discipline: action.discipline,
          status: action.status,
        });
      });
    } catch (error) {
      console.error('Failed to fetch backend logs', error);
    }
  },

  rollbackAction: async (actionId: string) => {
    try {
      const response = await fetch(`${API_URL}/api/v1/actions/${actionId}/rollback`, {
        method: 'POST',
      });

      if (!response.ok) {
        throw new Error('Rollback failed');
      }

      toast.success('Action rolled back successfully');
      get().fetchBackendLogs();
    } catch (error) {
      toast.error('Failed to rollback action');
      console.error(error);
    }
  }
}));
