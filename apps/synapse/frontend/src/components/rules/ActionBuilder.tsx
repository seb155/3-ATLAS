import React, { useState, useEffect } from 'react';
import { Plus, Trash2, HelpCircle } from 'lucide-react';
import { RuleAction, RuleActionType, CreateChildAction, SetPropertyAction } from '../../types/rules';

interface ActionBuilderProps {
  actionType: RuleActionType;
  action: RuleAction;
  onChange: (action: RuleAction) => void;
}

export default function ActionBuilder({ actionType, action, onChange }: ActionBuilderProps) {
  const [actionData, setActionData] = useState(action);

  useEffect(() => {
    setActionData(action);
  }, [action]);

  const updateAction = (updates: Partial<RuleAction>) => {
    const newAction = { ...actionData, ...updates };
    setActionData(newAction);
    onChange(newAction);
  };

  const renderCreateChildAction = () => {
    const createChild = actionData.create_child || {
      type: '',
      naming: '{parent_tag}-',
      relation: 'related_to',
      discipline: '',
      semantic_type: 'ASSET',
      inherit_properties: [],
      properties: {},
    };

    const updateCreateChild = (updates: Partial<CreateChildAction>) => {
      updateAction({ create_child: { ...createChild, ...updates } });
    };

    const addInheritProperty = () => {
      const newInherit = [...(createChild.inherit_properties || []), ''];
      updateCreateChild({ inherit_properties: newInherit });
    };

    const updateInheritProperty = (index: number, value: string) => {
      const newInherit = [...createChild.inherit_properties];
      newInherit[index] = value;
      updateCreateChild({ inherit_properties: newInherit });
    };

    const removeInheritProperty = (index: number) => {
      const newInherit = createChild.inherit_properties.filter((_: string, i: number) => i !== index);
      updateCreateChild({ inherit_properties: newInherit });
    };

    const addProperty = () => {
      const newProps = { ...createChild.properties, '': '' };
      updateCreateChild({ properties: newProps });
    };

    const updateProperty = (oldKey: string, newKey: string, value: string) => {
      const newProps = { ...createChild.properties };
      if (oldKey !== newKey) {
        delete newProps[oldKey];
      }
      newProps[newKey] = value;
      updateCreateChild({ properties: newProps });
    };

    const removeProperty = (key: string) => {
      const newProps = { ...createChild.properties };
      delete newProps[key];
      updateCreateChild({ properties: newProps });
    };

    return (
      <div className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Child Asset Type *
            </label>
            <input
              type="text"
              value={createChild.type}
              onChange={(e) => updateCreateChild({ type: e.target.value })}
              placeholder="e.g., MOTOR, LEVEL_TRANSMITTER"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Naming Convention *
              <HelpCircle className="inline w-3 h-3 ml-1 text-gray-400" />
            </label>
            <input
              type="text"
              value={createChild.naming}
              onChange={(e) => updateCreateChild({ naming: e.target.value })}
              placeholder="e.g., {parent_tag}-M"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Relationship Type
            </label>
            <select
              value={createChild.relation}
              onChange={(e) => updateCreateChild({ relation: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
            >
              <option value="powers">Powers</option>
              <option value="measured_by">Measured By</option>
              <option value="controlled_by">Controlled By</option>
              <option value="contains">Contains</option>
              <option value="related_to">Related To</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Discipline
            </label>
            <select
              value={createChild.discipline}
              onChange={(e) => updateCreateChild({ discipline: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
            >
              <option value="">Inherit from parent</option>
              <option value="ELECTRICAL">Electrical</option>
              <option value="AUTOMATION">Automation</option>
              <option value="MECHANICAL">Mechanical</option>
              <option value="PROCESS">Process</option>
            </select>
          </div>
        </div>

        {/* Inherit Properties */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <label className="block text-sm font-medium text-gray-700">
              Inherit Properties from Parent
            </label>
            <button
              onClick={addInheritProperty}
              className="flex items-center gap-1 px-2 py-1 text-xs text-purple-600 hover:bg-purple-50 rounded transition-colors"
            >
              <Plus className="w-3 h-3" />
              Add Property
            </button>
          </div>
          {createChild.inherit_properties && createChild.inherit_properties.length > 0 ? (
            <div className="space-y-2">
              {createChild.inherit_properties.map((prop: string, index: number) => (
                <div key={index} className="flex items-center gap-2">
                  <input
                    type="text"
                    value={prop}
                    onChange={(e) => updateInheritProperty(index, e.target.value)}
                    placeholder="Property name (e.g., area, system, voltage)"
                    className="flex-1 px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                  />
                  <button
                    onClick={() => removeInheritProperty(index)}
                    className="p-1 text-red-600 hover:bg-red-50 rounded transition-colors"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-sm text-gray-500 italic p-2 bg-gray-50 rounded border border-dashed border-gray-300">
              No inherited properties. Child will have only new properties.
            </div>
          )}
        </div>

        {/* New Properties */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <label className="block text-sm font-medium text-gray-700">
              New Properties for Child
            </label>
            <button
              onClick={addProperty}
              className="flex items-center gap-1 px-2 py-1 text-xs text-purple-600 hover:bg-purple-50 rounded transition-colors"
            >
              <Plus className="w-3 h-3" />
              Add Property
            </button>
          </div>
          {Object.keys(createChild.properties || {}).length > 0 ? (
            <div className="space-y-2">
              {Object.entries(createChild.properties).map(([key, value]) => (
                <div key={key} className="flex items-center gap-2">
                  <input
                    type="text"
                    value={key}
                    onChange={(e) => updateProperty(key, e.target.value, String(value))}
                    placeholder="Property key"
                    className="flex-1 px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                  />
                  <span className="text-gray-500">=</span>
                  <input
                    type="text"
                    value={String(value)}
                    onChange={(e) => updateProperty(key, key, e.target.value)}
                    placeholder="Property value"
                    className="flex-1 px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                  />
                  <button
                    onClick={() => removeProperty(key)}
                    className="p-1 text-red-600 hover:bg-red-50 rounded transition-colors"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-sm text-gray-500 italic p-2 bg-gray-50 rounded border border-dashed border-gray-300">
              No new properties. Use "Add Property" button above.
            </div>
          )}
        </div>

        <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg text-sm text-blue-800">
          <strong>Example:</strong> For a PUMP asset "310-PP-001", this will create a MOTOR named "310-PP-001-M"
          {createChild.inherit_properties?.length > 0 && ` inheriting ${createChild.inherit_properties.join(', ')}`}
        </div>
      </div>
    );
  };

  const renderSetPropertyAction = () => {
    const setProperty = actionData.set_property || {};

    const addProperty = () => {
      const newProps = { ...setProperty, '': '' };
      updateAction({ set_property: newProps });
    };

    const updateProperty = (oldKey: string, newKey: string, value: string) => {
      const newProps = { ...setProperty };
      if (oldKey !== newKey) {
        delete newProps[oldKey];
      }
      newProps[newKey] = value;
      updateAction({ set_property: newProps });
    };

    const removeProperty = (key: string) => {
      const newProps = { ...setProperty };
      delete newProps[key];
      updateAction({ set_property: newProps });
    };

    return (
      <div className="space-y-4">
        <div className="flex items-center justify-between mb-2">
          <label className="block text-sm font-medium text-gray-700">
            Properties to Set
          </label>
          <button
            onClick={addProperty}
            className="flex items-center gap-1 px-2 py-1 text-xs text-purple-600 hover:bg-purple-50 rounded transition-colors"
          >
            <Plus className="w-3 h-3" />
            Add Property
          </button>
        </div>

        {Object.keys(setProperty).length > 0 ? (
          <div className="space-y-2">
            {Object.entries(setProperty).map(([key, value]) => (
              <div key={key} className="flex items-center gap-2">
                <input
                  type="text"
                  value={key}
                  onChange={(e) => updateProperty(key, e.target.value, String(value))}
                  placeholder="Property key (e.g., voltage, manufacturer)"
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                />
                <span className="text-gray-500">=</span>
                <input
                  type="text"
                  value={String(value)}
                  onChange={(e) => updateProperty(key, key, e.target.value)}
                  placeholder="Property value (e.g., 600V, Rockwell)"
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                />
                <button
                  onClick={() => removeProperty(key)}
                  className="p-1 text-red-600 hover:bg-red-50 rounded transition-colors"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-sm text-gray-500 italic p-3 bg-gray-50 rounded border border-dashed border-gray-300">
            No properties to set. Click "Add Property" to define property updates.
          </div>
        )}

        <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg text-sm text-blue-800">
          <strong>Example:</strong> For motors in Canada, set voltage=600V and frequency=60Hz
        </div>
      </div>
    );
  };

  const renderPlaceholder = () => {
    return (
      <div className="p-6 text-center text-gray-500 bg-gray-50 rounded-lg border border-dashed border-gray-300">
        <p className="font-medium">Action type "{actionType}" is not yet implemented.</p>
        <p className="text-sm mt-1">This will be available in Phase 2.</p>
      </div>
    );
  };

  return (
    <div>
      {actionType === 'CREATE_CHILD' && renderCreateChildAction()}
      {actionType === 'SET_PROPERTY' && renderSetPropertyAction()}
      {actionType === 'CREATE_CABLE' && renderPlaceholder()}
      {actionType === 'CREATE_PACKAGE' && renderPlaceholder()}
      {actionType === 'ALLOCATE_IO' && renderPlaceholder()}
      {actionType === 'VALIDATE' && renderPlaceholder()}
    </div>
  );
}
