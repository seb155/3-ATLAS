import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  BookOpen,
  Plus,
  Play,
  Pause,
  Trash2,
  Edit,
  CheckCircle,
  AlertCircle,
  Zap,
  AlertTriangle,
  Loader2,
  ExternalLink
} from 'lucide-react';
import { logger } from '../services/logger';
import { API_URL } from '../../config';
import { useAuthStore } from '../store/useAuthStore';
import { useProjectStore } from '../store/useProjectStore';
import { Badge } from '../components/ui/Badge';
import { Card } from '../components/ui/Card';
import { Tabs } from '../components/ui/Tabs';
import { AssetSelectionGrid } from '../components/rules/AssetSelectionGrid';
import { RulesSidebar } from '../components/rules/RulesSidebar';
import { ExecutionLogs } from '../components/rules/ExecutionLogs';

interface Rule {
  id: string;
  name: string;
  description: string | null;
  source: 'FIRM' | 'COUNTRY' | 'PROJECT' | 'CLIENT';
  priority: number;
  discipline: string | null;
  action_type: string;
  is_active: boolean;
  execution_count: number;
  success_count: number;
  failure_count: number;
  created_at: string;
  last_executed_at: string | null;
}

interface ExecutionResult {
  total_rules: number;
  actions_taken: number;
  execution_time_ms: number;
  assets_processed?: number;
  details?: Array<{
    rule_id: string;
    rule_name: string;
    actions_taken: number;
  }>;
}

interface Asset {
  id: string;
  name: string;
  type: string;
  discipline: string | null;
  semantic_type: string;
  properties: Record<string, unknown>;
}

interface RulesTableProps {
  rules: Rule[];
  onToggle: (ruleId: string) => void;
  onDelete: (ruleId: string) => void;
}

function RulesTable({ rules, onToggle, onDelete }: RulesTableProps) {
  const getSourceBadgeColor = (source: string) => {
    const colors: Record<string, string> = {
      FIRM: 'bg-blue-500/20 text-blue-300 border-blue-500/30',
      COUNTRY: 'bg-green-500/20 text-green-300 border-green-500/30',
      PROJECT: 'bg-yellow-500/20 text-yellow-300 border-yellow-500/30',
      CLIENT: 'bg-purple-500/20 text-purple-300 border-purple-500/30',
    };
    return colors[source] || 'bg-slate-700 text-slate-300 border-slate-600';
  };

  const getActionTypeBadge = (actionType: string) => {
    const types: Record<string, { color: string; label: string }> = {
      CREATE_CHILD: { color: 'bg-indigo-500/20 text-indigo-300 border-indigo-500/30', label: 'Create Child' },
      CREATE_CABLE: { color: 'bg-orange-500/20 text-orange-300 border-orange-500/30', label: 'Create Cable' },
      SET_PROPERTY: { color: 'bg-teal-500/20 text-teal-300 border-teal-500/30', label: 'Set Property' },
      CREATE_RELATIONSHIP: { color: 'bg-pink-500/20 text-pink-300 border-pink-500/30', label: 'Create Relationship' },
      VALIDATE: { color: 'bg-red-500/20 text-red-300 border-red-500/30', label: 'Validate' },
    };
    const type = types[actionType] || { color: 'bg-slate-700 text-slate-300 border-slate-600', label: actionType };
    return (
      <Badge variant="outline" className={`border ${type.color}`}>
        {type.label}
      </Badge>
    );
  };

  return (
    <Card className="overflow-hidden border-slate-800 bg-slate-900">
      <table className="min-w-full divide-y divide-slate-800">
        <thead className="bg-slate-950">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
              Status
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
              Rule Name
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
              Source
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
              Priority
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
              Action
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
              Stats
            </th>
            <th className="px-6 py-3 text-right text-xs font-medium text-slate-400 uppercase tracking-wider">
              Actions
            </th>
          </tr>
        </thead>
        <tbody className="bg-slate-900 divide-y divide-slate-800">
          {rules.map((rule) => (
            <tr key={rule.id} className="hover:bg-slate-800 transition-colors">
              <td className="px-6 py-4 whitespace-nowrap">
                <button
                  onClick={() => onToggle(rule.id)}
                  className="flex items-center gap-2"
                >
                  {rule.is_active ? (
                    <CheckCircle className="w-5 h-5 text-green-400" />
                  ) : (
                    <Pause className="w-5 h-5 text-slate-500" />
                  )}
                </button>
              </td>
              <td className="px-6 py-4">
                <div className="text-sm font-medium text-white">{rule.name}</div>
                {rule.description && (
                  <div className="text-xs text-slate-400 mt-1 max-w-md truncate">
                    {rule.description}
                  </div>
                )}
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <Badge variant="outline" className={`border ${getSourceBadgeColor(rule.source)}`}>
                  {rule.source}
                </Badge>
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <span className="text-sm font-semibold text-white">{rule.priority}</span>
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                {getActionTypeBadge(rule.action_type)}
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <div className="flex items-center gap-3 text-xs text-slate-300">
                  <span title="Total Executions">
                    <Zap className="inline w-3 h-3 mr-1" />
                    {rule.execution_count}
                  </span>
                  <span title="Successes" className="text-green-400">
                    <CheckCircle className="inline w-3 h-3 mr-1" />
                    {rule.success_count}
                  </span>
                  {rule.failure_count > 0 && (
                    <span title="Failures" className="text-red-400">
                      <AlertTriangle className="inline w-3 h-3 mr-1" />
                      {rule.failure_count}
                    </span>
                  )}
                </div>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <button
                  onClick={() => onDelete(rule.id)}
                  className="text-red-400 hover:text-red-300 ml-3"
                  title="Delete Rule"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </Card>
  );
}

export default function RulesManagement() {
  const [rules, setRules] = useState<Rule[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isExecuting, setIsExecuting] = useState(false);
  const [executionResult, setExecutionResult] = useState<ExecutionResult | null>(null);
  const [selectedAssets, setSelectedAssets] = useState<Asset[]>([]);
  const [activeTab, setActiveTab] = useState<'table' | 'selection'>('table');
  const [sidebarTab, setSidebarTab] = useState<'rules' | 'logs'>('rules');
  const { token } = useAuthStore();
  const { currentProject } = useProjectStore();

  useEffect(() => {
    fetchRules();
  }, [currentProject]);

  const fetchRules = async () => {
    setIsLoading(true);
    try {
      const response = await axios.get(`${API_URL}/api/v1/rules`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      setRules(response.data.rules || []);
    } catch (error) {
      logger.error('Failed to fetch rules', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleToggle = async (ruleId: string) => {
    try {
      await axios.post(
        `${API_URL}/api/v1/rules/${ruleId}/toggle`,
        {},
        { headers: { 'Authorization': `Bearer ${token}` } }
      );
      logger.success('Rule status updated');
      fetchRules();
    } catch (error) {
      logger.error('Failed to toggle rule', error);
    }
  };

  const handleDelete = async (ruleId: string) => {
    if (!confirm('Are you sure you want to delete this rule?')) return;

    try {
      await axios.delete(
        `${API_URL}/api/v1/rules/${ruleId}`,
        { headers: { 'Authorization': `Bearer ${token}` } }
      );
      logger.success('Rule deleted');
      fetchRules();
    } catch (error) {
      logger.error('Failed to delete rule', error);
    }
  };

  const handleExecuteAllRules = async () => {
    if (!currentProject) {
      logger.error('No project selected');
      return;
    }

    setIsExecuting(true);
    setExecutionResult(null);

    try {
      const response = await axios.post(
        `${API_URL}/api/v1/rules/execute?project_id=${currentProject.id}`,
        {},
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );

      setExecutionResult(response.data);
      logger.success(
        `Executed ${response.data.total_rules} rules, ${response.data.actions_taken} actions taken in ${response.data.execution_time_ms}ms`
      );

      // Refresh rules to update stats
      fetchRules();
    } catch (error) {
      if (axios.isAxiosError(error)) {
        logger.error(`Failed to execute rules: ${error.response?.data?.detail || error.message}`);
      } else {
        logger.error('Failed to execute rules');
      }
    } finally {
      setIsExecuting(false);
    }
  };

  const handleExecuteSingleRule = async (ruleId: string) => {
    if (!currentProject) {
      logger.error('No project selected');
      return;
    }

    setIsExecuting(true);

    try {
      const payload = selectedAssets.length > 0
        ? { asset_ids: selectedAssets.map(a => a.id) }
        : { project_id: currentProject.id };

      const response = await axios.post(
        `${API_URL}/api/v1/rules/${ruleId}/execute`,
        payload,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'X-Project-ID': currentProject.id
          }
        }
      );

      logger.success(
        `Rule executed: ${response.data.assets_processed || 0} assets processed, ${response.data.actions_taken} actions taken`
      );

      // Refresh rules and clear selection
      fetchRules();
      setSelectedAssets([]);

      // Switch to logs tab to see results
      setSidebarTab('logs');
    } catch (error) {
      if (axios.isAxiosError(error)) {
        logger.error(`Failed to execute rule: ${error.response?.data?.detail || error.message}`);
      } else {
        logger.error('Failed to execute rule');
      }
    } finally {
      setIsExecuting(false);
    }
  };

  return (
    <div className="p-6 bg-slate-950 min-h-screen">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-white flex items-center gap-3">
              <BookOpen className="w-8 h-8 text-mining-teal" />
              Rules Management
            </h1>
            <p className="text-slate-400 mt-2">
              Create, edit, and manage engineering rules for your projects
            </p>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={handleExecuteAllRules}
              disabled={!currentProject || isExecuting || rules.filter(r => r.is_active).length === 0}
              className="px-4 py-2 bg-green-600 hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg text-white font-medium flex items-center gap-2 transition-colors"
              title={!currentProject ? 'Select a project first' : rules.filter(r => r.is_active).length === 0 ? 'No active rules' : 'Execute all active rules'}
            >
              {isExecuting ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Executing...
                </>
              ) : (
                <>
                  <Play className="w-5 h-5" />
                  Execute All Rules
                </>
              )}
            </button>
            <button
              className="px-4 py-2 bg-mining-teal hover:bg-teal-600 rounded-lg text-white font-medium flex items-center gap-2 transition-colors"
            >
              <Plus className="w-5 h-5" />
              Create New Rule
            </button>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card className="p-4 bg-slate-900 border-slate-800">
            <div className="text-sm text-slate-400">Total Rules</div>
            <div className="text-3xl font-bold text-white mt-1">{rules.length}</div>
          </Card>
          <Card className="p-4 bg-slate-900 border-slate-800">
            <div className="text-sm text-slate-400">Active Rules</div>
            <div className="text-3xl font-bold text-green-400 mt-1">
              {rules.filter(r => r.is_active).length}
            </div>
          </Card>
          <Card className="p-4 bg-slate-900 border-slate-800">
            <div className="text-sm text-slate-400">Total Executions</div>
            <div className="text-3xl font-bold text-mining-teal mt-1">
              {rules.reduce((sum, r) => sum + r.execution_count, 0)}
            </div>
          </Card>
          <Card className="p-4 bg-slate-900 border-slate-800">
            <div className="text-sm text-slate-400">Success Rate</div>
            <div className="text-3xl font-bold text-white mt-1">
              {rules.length > 0
                ? Math.round((rules.reduce((sum, r) => sum + r.success_count, 0) /
                  rules.reduce((sum, r) => sum + r.execution_count, 1)) * 100)
                : 0}%
            </div>
          </Card>
        </div>

        {/* Execution Result Card */}
        {executionResult && (
          <Card className="p-4 bg-gradient-to-r from-green-900/20 to-blue-900/20 border-green-500/30">
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <CheckCircle className="w-5 h-5 text-green-400" />
                  <div className="text-lg font-semibold text-white">Rules Executed Successfully</div>
                </div>
                <div className="text-sm text-slate-300 mt-2 flex items-center gap-4">
                  <span>
                    <span className="font-semibold text-white">{executionResult.total_rules}</span> rules applied
                  </span>
                  <span>•</span>
                  <span>
                    <span className="font-semibold text-green-400">{executionResult.actions_taken}</span> actions taken
                  </span>
                  <span>•</span>
                  <span>
                    <span className="font-semibold text-blue-400">{executionResult.execution_time_ms}ms</span> execution time
                  </span>
                  {executionResult.assets_processed && (
                    <>
                      <span>•</span>
                      <span>
                        <span className="font-semibold text-mining-teal">{executionResult.assets_processed}</span> assets processed
                      </span>
                    </>
                  )}
                </div>
              </div>
              <button
                onClick={() => window.location.href = '/dev-console'}
                className="px-3 py-2 bg-blue-600/20 hover:bg-blue-600/30 border border-blue-500/30 rounded-lg text-blue-300 text-sm font-medium flex items-center gap-2 transition-colors"
              >
                View Logs
                <ExternalLink className="w-4 h-4" />
              </button>
            </div>
          </Card>
        )}

        {/* View Toggle */}
        <Tabs
          tabs={[
            { id: 'table', label: 'Rules Table' },
            { id: 'selection', label: 'Asset Selection & Execution' }
          ]}
          activeTab={activeTab}
          onChange={(id) => setActiveTab(id as 'table' | 'selection')}
        />

        {/* Table View */}
        {activeTab === 'table' && (
          <>
            {isLoading ? (
              <Card className="p-8 bg-slate-900 border-slate-800 text-center">
                <div className="text-slate-400">Loading rules...</div>
              </Card>
            ) : rules.length === 0 ? (
              <Card className="p-8 bg-slate-900 border-slate-800 text-center">
                <AlertCircle className="w-12 h-12 text-slate-600 mx-auto mb-4" />
                <div className="text-slate-400">No rules found. Create your first rule to get started.</div>
              </Card>
            ) : (
              <RulesTable
                rules={rules}
                onToggle={handleToggle}
                onDelete={handleDelete}
              />
            )}
          </>
        )}

        {/* Two-Panel Selection View */}
        {activeTab === 'selection' && (
          <div className="grid grid-cols-3 gap-6">
            {/* Left: Asset Selection Grid (2/3 width) */}
            <div className="col-span-2">
              <Card className="bg-slate-900 border-slate-800">
                <div className="p-4 border-b border-slate-800">
                  <h2 className="text-lg font-semibold text-white">Project Assets</h2>
                  <p className="text-xs text-slate-400 mt-1">
                    {selectedAssets.length > 0
                      ? `${selectedAssets.length} asset(s) selected - apply rules selectively below`
                      : 'Select assets to apply rules selectively, or leave unselected to apply to all'
                    }
                  </p>
                </div>
                <div className="p-4">
                  <AssetSelectionGrid
                    projectId={currentProject?.id}
                    onSelectionChange={setSelectedAssets}
                  />
                </div>
              </Card>
            </div>

            {/* Right: Rules Sidebar (1/3 width) */}
            <div className="col-span-1">
              <Card className="bg-slate-900 border-slate-800">
                <Tabs
                  tabs={[
                    { id: 'rules', label: 'Rules' },
                    { id: 'logs', label: 'Logs' }
                  ]}
                  activeTab={sidebarTab}
                  onChange={(id) => setSidebarTab(id as 'rules' | 'logs')}
                />

                {sidebarTab === 'rules' ? (
                  <RulesSidebar
                    rules={rules}
                    selectedAssets={selectedAssets}
                    isExecuting={isExecuting}
                    onExecuteRule={handleExecuteSingleRule}
                  />
                ) : (
                  <ExecutionLogs projectId={currentProject?.id} />
                )}
              </Card>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

