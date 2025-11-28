
import React from 'react';
import { CheckCircle, XCircle, Zap, AlertTriangle, Eye } from 'lucide-react';
import { Rule, PropertyFilter, CreateChildAction, SetPropertyAction } from '../../types/rules';

interface RulePreviewProps {
  rule: Rule;
}

export default function RulePreview({ rule }: RulePreviewProps) {
  const renderConditionPreview = () => {
    if (!rule.condition || Object.keys(rule.condition).length === 0) {
      return (
        <div className="text-orange-600 flex items-center gap-2">
          <AlertTriangle className="w-4 h-4" />
          <span>No condition defined</span>
        </div>
      );
    }

    const parts: string[] = [];

    if (rule.condition.asset_type) {
      parts.push(`Asset type is "${rule.condition.asset_type}"`);
    }

    if (rule.condition.node_type) {
      parts.push(`Node type is "${rule.condition.node_type}"`);
    }

    if (rule.condition.property_filters && rule.condition.property_filters.length > 0) {
      rule.condition.property_filters.forEach((filter: PropertyFilter) => {
        parts.push(`${filter.key} ${filter.op} ${filter.value}`);
      });
    }

    return (
      <div className="space-y-1">
        {parts.map((part, index) => (
          <div key={index} className="text-sm text-gray-700 flex items-start gap-2">
            <span className="text-green-600 font-bold">•</span>
            <span>{part}</span>
          </div>
        ))}
      </div>
    );
  };

  const renderActionPreview = () => {
    if (!rule.action || Object.keys(rule.action).length === 0) {
      return (
        <div className="text-orange-600 flex items-center gap-2">
          <AlertTriangle className="w-4 h-4" />
          <span>No action defined</span>
        </div>
      );
    }

    if (rule.action_type === 'CREATE_CHILD' && rule.action.create_child) {
      const action = rule.action.create_child;
      return (
        <div className="space-y-2">
          <div className="text-sm">
            <span className="font-semibold text-indigo-700">Create</span>{' '}
            <span className="font-mono bg-indigo-100 px-2 py-1 rounded text-indigo-900">
              {action.type}
            </span>
          </div>
          <div className="text-sm">
            <span className="text-gray-600">Named:</span>{' '}
            <span className="font-mono bg-gray-100 px-2 py-1 rounded">{action.naming}</span>
          </div>
          <div className="text-sm">
            <span className="text-gray-600">Relationship:</span>{' '}
            <span className="text-gray-900">{action.relation}</span>
          </div>
          {action.inherit_properties && action.inherit_properties.length > 0 && (
            <div className="text-sm">
              <span className="text-gray-600">Inherit:</span>{' '}
              <span className="text-gray-900">{action.inherit_properties.join(', ')}</span>
            </div>
          )}
          {action.properties && Object.keys(action.properties).length > 0 && (
            <div className="text-sm">
              <span className="text-gray-600">Properties:</span>
              <div className="mt-1 space-y-1">
                {Object.entries(action.properties).map(([key, value]) => (
                  <div key={key} className="ml-4 font-mono text-xs bg-gray-100 px-2 py-1 rounded inline-block mr-2">
                    {key} = {JSON.stringify(value)}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      );
    }

    if (rule.action_type === 'SET_PROPERTY' && rule.action.set_property) {
      const props = rule.action.set_property;
      return (
        <div className="space-y-2">
          <div className="text-sm font-semibold text-teal-700">Set Properties:</div>
          <div className="space-y-1">
            {Object.entries(props).map(([key, value]) => (
              <div key={key} className="text-sm flex items-center gap-2">
                <span className="font-mono bg-gray-100 px-2 py-1 rounded">{key}</span>
                <span className="text-gray-500">=</span>
                <span className="font-mono bg-teal-100 px-2 py-1 rounded text-teal-900">
                  {JSON.stringify(value)}
                </span>
              </div>
            ))}
          </div>
        </div>
      );
    }

    return (
      <div className="text-sm text-gray-600">
        Action type: <span className="font-semibold">{rule.action_type}</span>
      </div>
    );
  };

  const getPriorityBadge = () => {
    const priority = rule.priority || 10;
    let color = 'bg-gray-100 text-gray-800';
    if (priority >= 100) color = 'bg-purple-100 text-purple-800';
    else if (priority >= 50) color = 'bg-yellow-100 text-yellow-800';
    else if (priority >= 30) color = 'bg-green-100 text-green-800';
    else color = 'bg-blue-100 text-blue-800';

    return (
      <span className={`px-3 py-1 rounded-full text-sm font-semibold ${color}`}>
        Priority {priority}
      </span>
    );
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h3 className="text-2xl font-bold text-gray-900">{rule.name || 'Untitled Rule'}</h3>
          {rule.description && (
            <p className="text-gray-600 mt-1">{rule.description}</p>
          )}
        </div>
        <div className="flex items-center gap-3">
          {getPriorityBadge()}
          {rule.is_active ? (
            <span className="flex items-center gap-1 text-green-600 text-sm font-medium">
              <CheckCircle className="w-4 h-4" />
              Active
            </span>
          ) : (
            <span className="flex items-center gap-1 text-gray-400 text-sm font-medium">
              <AlertTriangle className="w-4 h-4" />
              Inactive
            </span>
          )}
        </div>
      </div>

      {/* Metadata */}
      <div className="grid grid-cols-3 gap-4 p-4 bg-gray-50 rounded-lg">
        <div>
          <div className="text-xs text-gray-500 uppercase tracking-wide mb-1">Source</div>
          <div className="font-semibold text-gray-900">{rule.source}</div>
          {rule.source_id && (
            <div className="text-sm text-gray-600 mt-1">ID: {rule.source_id}</div>
          )}
        </div>
        <div>
          <div className="text-xs text-gray-500 uppercase tracking-wide mb-1">Discipline</div>
          <div className="font-semibold text-gray-900">{rule.discipline || 'All'}</div>
        </div>
        <div>
          <div className="text-xs text-gray-500 uppercase tracking-wide mb-1">Action Type</div>
          <div className="font-semibold text-gray-900">{rule.action_type}</div>
        </div>
      </div>

      {/* Rule Logic */}
      <div className="grid grid-cols-2 gap-6">
        {/* Condition */}
        <div className="p-4 bg-green-50 rounded-lg border-2 border-green-200">
          <div className="flex items-center gap-2 mb-3">
            <div className="w-8 h-8 bg-green-600 text-white rounded-full flex items-center justify-center font-bold">
              IF
            </div>
            <h4 className="text-lg font-semibold text-gray-900">Condition</h4>
          </div>
          {renderConditionPreview()}
        </div>

        {/* Action */}
        <div className="p-4 bg-purple-50 rounded-lg border-2 border-purple-200">
          <div className="flex items-center gap-2 mb-3">
            <div className="w-8 h-8 bg-purple-600 text-white rounded-full flex items-center justify-center font-bold">
              THEN
            </div>
            <h4 className="text-lg font-semibold text-gray-900">Action</h4>
          </div>
          {renderActionPreview()}
        </div>
      </div>

      {/* Examples */}
      <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <div className="flex items-center gap-2 mb-2">
          <Eye className="w-5 h-5 text-blue-600" />
          <h4 className="font-semibold text-blue-900">How this rule works:</h4>
        </div>
        <div className="text-sm text-blue-800 space-y-2">
          {rule.condition.asset_type === 'PUMP' && rule.action_type === 'CREATE_CHILD' && rule.action.create_child?.type === 'MOTOR' && (
            <p>
              When a <strong>PUMP</strong> asset is found (like "310-PP-001"), this rule will automatically
              create a <strong>MOTOR</strong> asset (like "310-PP-001-M") and link it to the pump
              with a "powers" relationship.
            </p>
          )}
          {rule.condition.asset_type === 'MOTOR' && rule.action_type === 'SET_PROPERTY' && (
            <p>
              When a <strong>MOTOR</strong> asset is found, this rule will update its properties
              {rule.action.set_property?.voltage && ` to set voltage to ${rule.action.set_property.voltage}`}
              {rule.action.set_property?.frequency && ` and frequency to ${rule.action.set_property.frequency}`}.
            </p>
          )}
          {rule.condition.node_type === 'AREA' && (
            <p>
              When an <strong>AREA</strong> node is found (like "310"), this rule will create
              the required control system infrastructure for that area.
            </p>
          )}
          {!rule.condition.asset_type && !rule.condition.node_type && (
            <p>Configure the condition to see how this rule will behave.</p>
          )}
        </div>
      </div>

      {/* JSON Preview (for debugging) */}
      <details className="mt-4">
        <summary className="cursor-pointer text-sm text-gray-600 hover:text-gray-900 font-medium">
          View JSON (for debugging)
        </summary>
        <pre className="mt-2 p-4 bg-gray-900 text-green-400 rounded-lg text-xs overflow-x-auto">
          {JSON.stringify(rule, null, 2)}
        </pre>
      </details>
    </div>
  );
}
