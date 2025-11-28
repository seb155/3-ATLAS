import React, { useState, useEffect } from 'react';
import { X, Save, AlertCircle, HelpCircle } from 'lucide-react';
import ConditionBuilder from './ConditionBuilder';
import ActionBuilder from './ActionBuilder';
import RulePreview from './RulePreview';
import { Rule, RuleCreate, RuleSource, RuleActionType, RuleCondition, RuleAction } from '../../types/rules';

interface RuleEditorProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (rule: RuleCreate) => Promise<void>;
  existingRule?: Rule | null;
}

export default function RuleEditor({ isOpen, onClose, onSave, existingRule }: RuleEditorProps) {
  const [formData, setFormData] = useState<RuleCreate>({
    name: '',
    description: '',
    source: RuleSource.FIRM,
    source_id: null,
    priority: 10, // Default priority for FIRM
    discipline: '',
    category: '', // Assuming a default empty string for category
    action_type: RuleActionType.CREATE_CHILD,
    condition: {} as RuleCondition,
    action: {} as RuleAction,
    is_active: true,
    is_enforced: false, // Assuming a default false
    overrides_rule_id: null, // Assuming a default null
    conflicts_with: [], // Assuming a default empty array
  });

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isSaving, setIsSaving] = useState(false);
  const [showPreview, setShowPreview] = useState(false);

  useEffect(() => {
    if (existingRule) {
      setFormData({
        name: existingRule.name || '',
        description: existingRule.description || '',
        source: existingRule.source || RuleSource.FIRM,
        source_id: existingRule.source_id || null,
        priority: existingRule.priority || 10,
        discipline: existingRule.discipline || '',
        category: existingRule.category || '',
        action_type: existingRule.action_type || RuleActionType.CREATE_CHILD,
        condition: existingRule.condition || {} as RuleCondition,
        action: existingRule.action || {} as RuleAction,
        is_active: existingRule.is_active !== undefined ? existingRule.is_active : true,
        is_enforced: existingRule.is_enforced !== undefined ? existingRule.is_enforced : false,
        overrides_rule_id: existingRule.overrides_rule_id || null,
        conflicts_with: existingRule.conflicts_with || [],
      });
    } else {
      // Reset for new rule
      setFormData({
        name: '',
        description: '',
        source: RuleSource.FIRM,
        source_id: null,
        priority: 10,
        discipline: '',
        category: '',
        action_type: RuleActionType.CREATE_CHILD,
        condition: {} as RuleCondition,
        action: {} as RuleAction,
        is_active: true,
        is_enforced: false,
        overrides_rule_id: null,
        conflicts_with: [],
      });
    }
    setErrors({});
  }, [existingRule, isOpen]);

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.name.trim()) {
      newErrors.name = 'Rule name is required';
    }

    if (!formData.condition || Object.keys(formData.condition).length === 0) {
      newErrors.condition = 'At least one condition is required';
    }

    if (!formData.action || Object.keys(formData.action).length === 0) {
      newErrors.action = 'Action configuration is required';
    }

    if (formData.source === 'COUNTRY' && !formData.source_id) {
      newErrors.source_id = 'Country code is required for COUNTRY source';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSave = async () => {
    if (!validateForm()) {
      return;
    }

    setIsSaving(true);
    try {
      await onSave(formData);
      onClose();
    } catch (error) {
      console.error('Failed to save rule:', error);
      setErrors({ submit: 'Failed to save rule. Please try again.' });
    } finally {
      setIsSaving(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-slate-900 rounded-lg shadow-xl max-w-5xl w-full max-h-[90vh] overflow-hidden flex flex-col border border-slate-700">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-slate-700">
          <div>
            <h2 className="text-2xl font-bold text-white">
              {existingRule ? 'Edit Rule' : 'Create New Rule'}
            </h2>
            <p className="text-sm text-slate-400 mt-1">
              Define conditions and actions for automated engineering logic
            </p>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setShowPreview(!showPreview)}
              className="px-3 py-2 text-sm border border-slate-600 rounded-lg hover:bg-slate-700 transition-colors text-slate-300"
            >
              {showPreview ? 'Edit' : 'Preview'}
            </button>
            <button
              onClick={onClose}
              className="p-2 hover:bg-slate-700 rounded-lg transition-colors text-slate-400"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {showPreview ? (
            <RulePreview rule={formData} />
          ) : (
            <div className="space-y-6">
              {/* Basic Information */}
              <div className="bg-slate-800/50 p-4 rounded-lg border border-slate-700">
                <h3 className="text-lg font-semibold text-white mb-4">Basic Information</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div className="col-span-2">
                    <label className="block text-sm font-medium text-slate-300 mb-1">
                      Rule Name *
                    </label>
                    <input
                      type="text"
                      value={formData.name}
                      onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                      className={`w-full px-3 py-2 bg-slate-900 border rounded-lg focus:ring-2 focus:ring-blue-500 text-white ${errors.name ? 'border-red-500' : 'border-slate-600'
                        }`}
                      placeholder="e.g., Create motor for centrifugal pumps"
                    />
                    {errors.name && (
                      <p className="mt-1 text-sm text-red-400 flex items-center gap-1">
                        <AlertCircle className="w-4 h-4" />
                        {errors.name}
                      </p>
                    )}
                  </div>

                  <div className="col-span-2">
                    <label className="block text-sm font-medium text-slate-300 mb-1">
                      Description
                    </label>
                    <textarea
                      value={formData.description}
                      onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                      className="w-full px-3 py-2 bg-slate-900 border border-slate-600 rounded-lg focus:ring-2 focus:ring-blue-500 text-white placeholder-slate-500"
                      rows={2}
                      placeholder="Explain what this rule does and why it exists"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-1">
                      Source *
                      <HelpCircle className="inline w-4 h-4 ml-1 text-slate-500" />
                    </label>
                    <select
                      value={formData.source}
                      onChange={(e) => setFormData({ ...formData, source: e.target.value as RuleSource })}
                      className="w-full px-3 py-2 bg-slate-900 border border-slate-600 rounded-lg focus:ring-2 focus:ring-blue-500 text-white"
                    >
                      <option value="FIRM">FIRM (Priority 10)</option>
                      <option value="COUNTRY">COUNTRY (Priority 30)</option>
                      <option value="PROJECT">PROJECT (Priority 50)</option>
                      <option value="CLIENT">CLIENT (Priority 100)</option>
                    </select>
                  </div>

                  {formData.source === 'COUNTRY' && (
                    <div>
                      <label className="block text-sm font-medium text-slate-300 mb-1">
                        Country Code *
                      </label>
                      <input
                        type="text"
                        value={formData.source_id || ''}
                        onChange={(e) => setFormData({ ...formData, source_id: e.target.value })}
                        className={`w-full px-3 py-2 bg-slate-900 border rounded-lg focus:ring-2 focus:ring-blue-500 text-white ${errors.source_id ? 'border-red-500' : 'border-slate-600'
                          }`}
                        placeholder="e.g., CA, BR, GR"
                      />
                      {errors.source_id && (
                        <p className="mt-1 text-sm text-red-400">{errors.source_id}</p>
                      )}
                    </div>
                  )}

                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-1">
                      Discipline
                    </label>
                    <select
                      value={formData.discipline || ''}
                      onChange={(e) => setFormData({ ...formData, discipline: e.target.value || null })}
                      className="w-full px-3 py-2 bg-slate-900 border border-slate-600 rounded-lg focus:ring-2 focus:ring-blue-500 text-white"
                    >
                      <option value="">All Disciplines</option>
                      <option value="ELECTRICAL">Electrical</option>
                      <option value="AUTOMATION">Automation</option>
                      <option value="MECHANICAL">Mechanical</option>
                      <option value="PROCESS">Process</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-1">
                      Priority (Optional)
                    </label>
                    <input
                      type="number"
                      value={formData.priority || ''}
                      onChange={(e) =>
                        setFormData({
                          ...formData,
                          priority: e.target.value ? parseInt(e.target.value) : undefined,
                        })
                      }
                      className="w-full px-3 py-2 bg-slate-900 border border-slate-600 rounded-lg focus:ring-2 focus:ring-blue-500 text-white placeholder-slate-500"
                      placeholder="Auto-assigned by source"
                      min="1"
                      max="100"
                    />
                  </div>

                  <div className="col-span-2 flex items-center">
                    <input
                      type="checkbox"
                      id="is_active"
                      checked={formData.is_active}
                      onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                      className="w-4 h-4 text-blue-600 border-slate-600 rounded focus:ring-blue-500 bg-slate-900"
                    />
                    <label htmlFor="is_active" className="ml-2 text-sm text-slate-300">
                      Rule is active (will be applied during rule execution)
                    </label>
                  </div>
                </div>
              </div>

              {/* Action Type */}
              <div className="bg-slate-800/50 p-4 rounded-lg border border-slate-700">
                <h3 className="text-lg font-semibold text-white mb-4">Action Type</h3>
                <div className="grid grid-cols-2 gap-3">
                  {[
                    { value: 'CREATE_CHILD', label: 'Create Child Asset', desc: 'Create related asset (e.g., motor for pump)' },
                    { value: 'SET_PROPERTY', label: 'Set Property', desc: 'Update asset properties' },
                    { value: 'CREATE_CABLE', label: 'Create Cable', desc: 'Generate cable connection (Phase 2)' },
                    { value: 'CREATE_RELATIONSHIP', label: 'Create Relationship', desc: 'Link existing assets' },
                  ].map((type) => (
                    <button
                      key={type.value}
                      onClick={() => setFormData({ ...formData, action_type: type.value as RuleActionType })}
                      className={`p-3 text-left border-2 rounded-lg transition-all ${formData.action_type === type.value
                        ? 'border-blue-500 bg-blue-500/20 text-white'
                        : 'border-slate-600 hover:border-blue-400 text-slate-300'
                        }`}
                    >
                      <div className="font-semibold text-sm">{type.label}</div>
                      <div className="text-xs text-slate-400 mt-1">{type.desc}</div>
                    </button>
                  ))}
                </div>
              </div>

              {/* Condition Builder */}
              <div className="bg-slate-800/50 p-4 rounded-lg border border-slate-700">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-white">When (Condition)</h3>
                  {errors.condition && (
                    <p className="text-sm text-red-400 flex items-center gap-1">
                      <AlertCircle className="w-4 h-4" />
                      {errors.condition}
                    </p>
                  )}
                </div>
                <ConditionBuilder
                  condition={formData.condition}
                  onChange={(condition) => setFormData({ ...formData, condition })}
                />
              </div>

              {/* Action Builder */}
              <div className="bg-slate-800/50 p-4 rounded-lg border border-slate-700">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-white">Then (Action)</h3>
                  {errors.action && (
                    <p className="text-sm text-red-400 flex items-center gap-1">
                      <AlertCircle className="w-4 h-4" />
                      {errors.action}
                    </p>
                  )}
                </div>
                <ActionBuilder
                  actionType={formData.action_type}
                  action={formData.action}
                  onChange={(action) => setFormData({ ...formData, action })}
                />
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between p-6 border-t border-slate-700 bg-slate-800/50">
          <div>
            {errors.submit && (
              <p className="text-sm text-red-400 flex items-center gap-1">
                <AlertCircle className="w-4 h-4" />
                {errors.submit}
              </p>
            )}
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={onClose}
              className="px-4 py-2 text-slate-300 border border-slate-600 rounded-lg hover:bg-slate-700 transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={handleSave}
              disabled={isSaving}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Save className="w-4 h-4" />
              {isSaving ? 'Saving...' : existingRule ? 'Update Rule' : 'Create Rule'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
