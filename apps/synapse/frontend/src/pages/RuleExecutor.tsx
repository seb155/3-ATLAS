import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  Play,
  Zap,
  CheckSquare,
  Square,
  Info,
  BookOpen,
  Activity,
  Clock
} from 'lucide-react';
import { logger } from '../services/logger';
import { API_URL } from '../../config';
import { useAuthStore } from '../store/useAuthStore';
import { useProjectStore } from '../store/useProjectStore';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';

interface Asset {
  id: string;
  tag: string;
  description: string | null;
  type: string;
  area: string | null;
  system: string | null;
}

interface Rule {
  id: string;
  name: string;
  description: string | null;
  source: string;
  priority: number;
  action_type: string;
  is_active: boolean;
}

interface ExecutionLog {
  id: string;
  action_type: string;
  description: string;
  timestamp: string;
  details: Record<string, unknown>;
}

type TabType = 'data' | 'rules' | 'logs';

export default function RuleExecutor() {
  const [assets, setAssets] = useState<Asset[]>([]);
  const [rules, setRules] = useState<Rule[]>([]);
  const [logs, setLogs] = useState<ExecutionLog[]>([]);
  const [selectedAssetIds, setSelectedAssetIds] = useState<Set<string>>(new Set());
  const [selectedRuleId, setSelectedRuleId] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<TabType>('data');
  const [isLoading, setIsLoading] = useState(false);
  const [isExecuting, setIsExecuting] = useState(false);

  const { token } = useAuthStore();
  const { currentProject } = useProjectStore();

  useEffect(() => {
    if (currentProject) {
      fetchAssets();
      fetchRules();
      fetchLogs();
    }
  }, [currentProject]);

  const fetchAssets = async () => {
    setIsLoading(true);
    try {
      const response = await axios.get(`${API_URL}/api/v1/assets/?limit=10000`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'X-Project-ID': currentProject?.id || ''
        }
      });
      setAssets(response.data || []);
    } catch (error) {
      logger.error('Failed to fetch assets', error);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchRules = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/v1/rules`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const activeRules = (response.data.rules || []).filter((r: Rule) => r.is_active);
      setRules(activeRules);
    } catch (error) {
      logger.error('Failed to fetch rules', error);
    }
  };

  const fetchLogs = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/v1/actions/?limit=50&project_id=${currentProject?.id}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      setLogs(response.data || []);
    } catch (error) {
      logger.error('Failed to fetch logs', error);
    }
  };

  const toggleAssetSelection = (assetId: string) => {
    const newSelection = new Set(selectedAssetIds);
    if (newSelection.has(assetId)) {
      newSelection.delete(assetId);
    } else {
      newSelection.add(assetId);
    }
    setSelectedAssetIds(newSelection);
  };

  const toggleSelectAll = () => {
    if (selectedAssetIds.size === assets.length) {
      setSelectedAssetIds(new Set());
    } else {
      setSelectedAssetIds(new Set(assets.map(a => a.id)));
    }
  };

  const executeSelectedRule = async () => {
    if (!selectedRuleId || selectedAssetIds.size === 0) {
      logger.warn('Please select a rule and at least one asset');
      return;
    }

    setIsExecuting(true);
    try {
      const response = await axios.post(
        `${API_URL}/api/v1/rules/${selectedRuleId}/execute`,
        {
          asset_ids: Array.from(selectedAssetIds),
          project_id: currentProject?.id
        },
        { headers: { 'Authorization': `Bearer ${token}` } }
      );

      logger.success(`✅ Rule executed! ${response.data.actions_taken || 0} actions taken`);
      await fetchAssets();
      await fetchLogs();
      setSelectedAssetIds(new Set());
    } catch (error) {
      logger.error('Failed to execute rule', error);
    } finally {
      setIsExecuting(false);
    }
  };

  const executeAllRules = async () => {
    if (selectedAssetIds.size === 0) {
      logger.warn('Please select at least one asset');
      return;
    }

    setIsExecuting(true);
    try {
      let totalActions = 0;

      for (const ruleId of rules.map(r => r.id)) {
        const response = await axios.post(
          `${API_URL}/api/v1/rules/${ruleId}/execute`,
          {
            asset_ids: Array.from(selectedAssetIds),
            project_id: currentProject?.id
          },
          { headers: { 'Authorization': `Bearer ${token}` } }
        );
        totalActions += response.data.actions_taken || 0;
      }

      logger.success(`✅ All rules executed! ${totalActions} total actions taken`);
      await fetchAssets();
      await fetchLogs();
      setSelectedAssetIds(new Set());
    } catch (error) {
      logger.error('Failed to execute all rules', error);
    } finally {
      setIsExecuting(false);
    }
  };

  const selectedAssets = assets.filter(a => selectedAssetIds.has(a.id));
  const selectedRule = rules.find(r => r.id === selectedRuleId);

  return (
    <div className="flex h-full bg-slate-950">
      {/* Left Panel - Asset Grid */}
      <div className="flex-1 flex flex-col border-r border-slate-800 overflow-hidden">
        {/* Header */}
        <div className="p-6 border-b border-slate-800 bg-slate-900">
          <h1 className="text-2xl font-bold text-white flex items-center gap-3">
            <Zap className="w-7 h-7 text-mining-teal" />
            Rule Executor
          </h1>
          <p className="text-slate-400 mt-1">
            Select assets and execute rules
          </p>
          <div className="mt-3 flex items-center gap-4 text-sm">
            <span className="text-slate-400">
              {selectedAssetIds.size} of {assets.length} assets selected
            </span>
            {selectedRule && (
              <Badge variant="outline" className="border-mining-teal text-mining-teal">
                {selectedRule.name}
              </Badge>
            )}
          </div>
        </div>

        {/* Asset Table */}
        <div className="flex-1 overflow-auto">
          {isLoading ? (
            <div className="flex items-center justify-center h-full">
              <div className="text-slate-400">Loading assets...</div>
            </div>
          ) : (
            <table className="min-w-full divide-y divide-slate-800">
              <thead className="bg-slate-900 sticky top-0 z-10">
                <tr>
                  <th className="px-4 py-3 text-left">
                    <button
                      onClick={toggleSelectAll}
                      className="hover:text-mining-teal transition-colors"
                    >
                      {selectedAssetIds.size === assets.length ? (
                        <CheckSquare className="w-5 h-5 text-mining-teal" />
                      ) : (
                        <Square className="w-5 h-5 text-slate-500" />
                      )}
                    </button>
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
                    Tag
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
                    Type
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
                    Area
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
                    System
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
                    Description
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {assets.map((asset) => (
                  <tr
                    key={asset.id}
                    className={`hover:bg-slate-800 transition-colors cursor-pointer ${selectedAssetIds.has(asset.id) ? 'bg-slate-800/50' : ''
                      }`}
                    onClick={() => toggleAssetSelection(asset.id)}
                  >
                    <td className="px-4 py-3">
                      {selectedAssetIds.has(asset.id) ? (
                        <CheckSquare className="w-5 h-5 text-mining-teal" />
                      ) : (
                        <Square className="w-5 h-5 text-slate-500" />
                      )}
                    </td>
                    <td className="px-4 py-3 text-sm font-medium text-white">
                      {asset.tag}
                    </td>
                    <td className="px-4 py-3 text-sm text-slate-300">
                      {asset.type}
                    </td>
                    <td className="px-4 py-3 text-sm text-slate-400">
                      {asset.area || '-'}
                    </td>
                    <td className="px-4 py-3 text-sm text-slate-400">
                      {asset.system || '-'}
                    </td>
                    <td className="px-4 py-3 text-sm text-slate-400 truncate max-w-xs">
                      {asset.description || '-'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        {/* Bottom Action Bar */}
        <div className="p-4 border-t border-slate-800 bg-slate-900 flex items-center gap-3">
          <button
            onClick={executeSelectedRule}
            disabled={!selectedRuleId || selectedAssetIds.size === 0 || isExecuting}
            className="px-4 py-2 bg-mining-teal hover:bg-teal-600 disabled:bg-slate-700 disabled:text-slate-500 rounded-lg text-white font-medium flex items-center gap-2 transition-colors"
          >
            <Play className="w-4 h-4" />
            Execute Selected Rule
          </button>
          <button
            onClick={executeAllRules}
            disabled={selectedAssetIds.size === 0 || isExecuting}
            className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 disabled:bg-slate-700 disabled:text-slate-500 rounded-lg text-white font-medium flex items-center gap-2 transition-colors"
          >
            <Zap className="w-4 h-4" />
            Execute All Rules
          </button>
          {isExecuting && (
            <span className="text-sm text-slate-400 animate-pulse">
              Executing...
            </span>
          )}
        </div>
      </div>

      {/* Right Panel - Tabs */}
      <div className="w-96 flex flex-col bg-slate-900">
        {/* Tab Headers */}
        <div className="flex border-b border-slate-800">
          <button
            onClick={() => setActiveTab('data')}
            className={`flex-1 px-4 py-3 text-sm font-medium transition-colors ${activeTab === 'data'
              ? 'text-mining-teal border-b-2 border-mining-teal'
              : 'text-slate-400 hover:text-white'
              }`}
          >
            <Info className="w-4 h-4 inline mr-2" />
            Data
          </button>
          <button
            onClick={() => setActiveTab('rules')}
            className={`flex-1 px-4 py-3 text-sm font-medium transition-colors ${activeTab === 'rules'
              ? 'text-mining-teal border-b-2 border-mining-teal'
              : 'text-slate-400 hover:text-white'
              }`}
          >
            <BookOpen className="w-4 h-4 inline mr-2" />
            Rules
          </button>
          <button
            onClick={() => setActiveTab('logs')}
            className={`flex-1 px-4 py-3 text-sm font-medium transition-colors ${activeTab === 'logs'
              ? 'text-mining-teal border-b-2 border-mining-teal'
              : 'text-slate-400 hover:text-white'
              }`}
          >
            <Activity className="w-4 h-4 inline mr-2" />
            Logs
          </button>
        </div>

        {/* Tab Content */}
        <div className="flex-1 overflow-auto p-4">
          {activeTab === 'data' && (
            <div className="space-y-4">
              <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider">
                Selected Assets ({selectedAssets.length})
              </h3>
              {selectedAssets.length === 0 ? (
                <p className="text-sm text-slate-500">No assets selected</p>
              ) : (
                <div className="space-y-2">
                  {selectedAssets.map((asset) => (
                    <Card key={asset.id} className="p-3 bg-slate-800 border-slate-700">
                      <div className="text-sm font-medium text-white">{asset.tag}</div>
                      <div className="text-xs text-slate-400 mt-1">{asset.type}</div>
                      {asset.description && (
                        <div className="text-xs text-slate-500 mt-1 line-clamp-2">
                          {asset.description}
                        </div>
                      )}
                    </Card>
                  ))}
                </div>
              )}
            </div>
          )}

          {activeTab === 'rules' && (
            <div className="space-y-4">
              <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider">
                Active Rules ({rules.length})
              </h3>
              <div className="space-y-2">
                {rules.map((rule) => (
                  <div key={rule.id} onClick={() => setSelectedRuleId(rule.id)}>
                    <Card
                      className={`p-3 cursor-pointer transition-all ${selectedRuleId === rule.id
                        ? 'bg-mining-teal/20 border-mining-teal'
                        : 'bg-slate-800 border-slate-700 hover:border-slate-600'
                        }`}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="text-sm font-medium text-white">{rule.name}</div>
                          {rule.description && (
                            <div className="text-xs text-slate-400 mt-1 line-clamp-2">
                              {rule.description}
                            </div>
                          )}
                          <div className="flex items-center gap-2 mt-2">
                            <Badge variant="outline" className="text-xs border-slate-600 text-slate-400">
                              {rule.source}
                            </Badge>
                            <Badge variant="outline" className="text-xs border-slate-600 text-slate-400">
                              Priority: {rule.priority}
                            </Badge>
                          </div>
                        </div>
                      </div>
                    </Card>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'logs' && (
            <div className="space-y-4">
              <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider">
                Recent Executions
              </h3>
              <div className="space-y-2">
                {logs.map((log) => (
                  <Card key={log.id} className="p-3 bg-slate-800 border-slate-700">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="text-xs font-medium text-white">{log.description}</div>
                        <div className="text-xs text-slate-400 mt-1 flex items-center gap-1">
                          <Clock className="w-3 h-3" />
                          {new Date(log.timestamp).toLocaleString()}
                        </div>
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
