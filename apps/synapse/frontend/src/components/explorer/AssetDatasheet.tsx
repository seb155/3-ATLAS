import React, { useState, useEffect } from 'react';
import { Asset, PhysicalLocation, AssetType, IOType } from '../../../types';
import { Save, RefreshCw, MapPin, Cpu, Activity, Zap, ShoppingBag } from 'lucide-react';
import { logger } from '../../services/logger';

interface AssetDatasheetProps {
    asset: Asset;
    locations: PhysicalLocation[];
    onUpdate: (updatedAsset: Asset) => Promise<void>;
}

export const AssetDatasheet: React.FC<AssetDatasheetProps> = ({ asset, locations, onUpdate }) => {
    const [formData, setFormData] = useState<Asset>(asset);
    const [isDirty, setIsDirty] = useState(false);

    useEffect(() => {
        setFormData(asset);
        setIsDirty(false);
    }, [asset]);

    const handleChange = (field: string, value: string | number) => {
        setFormData(prev => {
            const updated = { ...prev };
            const keys = field.split('.');
            if (keys.length === 1) {
                (updated as Record<string, unknown>)[keys[0]] = value;
            } else {
                let current: Record<string, unknown> = updated as Record<string, unknown>;
                for (let i = 0; i < keys.length - 1; i++) {
                    if (!current[keys[i]]) current[keys[i]] = {} as Record<string, unknown>;
                    current = current[keys[i]] as Record<string, unknown>;
                }
                current[keys[keys.length - 1]] = value;
            }
            return updated;
        });
        setIsDirty(true);
    };

    const [isSaving, setIsSaving] = useState(false);

    const handleSave = async () => {
        setIsSaving(true);
        try {
            await onUpdate(formData);
            setIsDirty(false);
        } catch (error) {
            logger.error("Failed to save asset:", error);
            logger.error("Failed to save changes.");
        } finally {
            setIsSaving(false);
        }
    };

    return (
        <div className="h-full flex flex-col bg-slate-900 text-slate-200 overflow-hidden">
            {/* Toolbar */}
            <div className="h-14 border-b border-slate-800 flex items-center px-6 justify-between bg-slate-950">
                <div className="flex items-center gap-4">
                    <div className="p-2 bg-mining-teal/10 rounded-lg">
                        <Activity className="text-mining-teal" size={20} />
                    </div>
                    <div>
                        <h3 className="font-bold text-white">{formData.tag}</h3>
                        <p className="text-xs text-slate-500 uppercase tracking-wider">{formData.type} Datasheet</p>
                    </div>
                </div>
                <div className="flex items-center gap-3">
                    <button
                        onClick={() => setFormData(asset)}
                        disabled={!isDirty}
                        className={`p-2 rounded-md transition-colors ${isDirty ? 'text-slate-400 hover:text-white hover:bg-slate-800' : 'text-slate-700 cursor-not-allowed'}`}
                        title="Reset Changes"
                    >
                        <RefreshCw size={18} />
                    </button>
                    <button
                        onClick={handleSave}
                        disabled={!isDirty || isSaving}
                        className={`flex items-center gap-2 px-4 py-2 rounded-md font-medium transition-colors ${isDirty ? 'bg-mining-teal text-slate-950 hover:bg-mining-teal/90' : 'bg-slate-800 text-slate-500 cursor-not-allowed'}`}
                    >
                        <Save size={18} />
                        {isSaving ? 'Saving...' : 'Save Changes'}
                    </button>
                </div>
            </div>

            {/* Form Content */}
            <div className="flex-1 overflow-y-auto p-8">
                <div className="max-w-4xl mx-auto space-y-8">

                    {/* General Section */}
                    <Section title="General Information" icon={Cpu}>
                        <div className="grid grid-cols-2 gap-6">
                            <Field label="Tag" value={formData.tag} onChange={v => handleChange('tag', v)} disabled />
                            <Field label="Description" value={formData.description} onChange={v => handleChange('description', v)} />
                            <Select label="Asset Type" value={formData.type} options={Object.values(AssetType)} onChange={v => handleChange('type', v)} />
                            <Select label="IO Type" value={formData.ioType || ''} options={Object.values(IOType)} onChange={v => handleChange('ioType', v)} />
                        </div>
                    </Section>

                    {/* Location Section */}
                    <Section title="Location & Context" icon={MapPin}>
                        <div className="grid grid-cols-2 gap-6">
                            <div className="col-span-2">
                                <label className="block text-xs font-medium text-slate-500 mb-1 uppercase tracking-wider">Physical Location</label>
                                <select
                                    value={formData.locationId || ''}
                                    onChange={e => handleChange('locationId', e.target.value)}
                                    className="w-full bg-slate-950 border border-slate-800 rounded-md px-3 py-2 text-sm focus:outline-none focus:border-mining-teal focus:ring-1 focus:ring-mining-teal transition-colors"
                                >
                                    <option value="">-- Unassigned --</option>
                                    {locations.map(l => (
                                        <option key={l.id} value={l.id}>{l.name} ({l.type})</option>
                                    ))}
                                </select>
                            </div>
                            <Field label="Area (FBS)" value={formData.area || ''} onChange={v => handleChange('area', v)} />
                            <Field label="System (FBS)" value={formData.system || ''} onChange={v => handleChange('system', v)} />
                        </div>
                    </Section>

                    {/* Electrical Section */}
                    <Section title="Electrical Specification" icon={Zap}>
                        <div className="grid grid-cols-3 gap-6">
                            <Field label="Voltage (V)" value={formData.electrical?.voltage || ''} onChange={v => handleChange('electrical.voltage', v)} />
                            <Field label="Power (kW)" value={formData.electrical?.powerKW || ''} type="number" onChange={v => handleChange('electrical.powerKW', parseFloat(v))} />
                            <Field label="Load Type" value={formData.electrical?.loadType || ''} onChange={v => handleChange('electrical.loadType', v)} />
                        </div>
                    </Section>

                    {/* Process Section */}
                    <Section title="Process Data" icon={Activity}>
                        <div className="grid grid-cols-4 gap-6">
                            <div className="col-span-2">
                                <Field label="Fluid / Service" value={formData.process?.fluid || ''} onChange={v => handleChange('process.fluid', v)} />
                            </div>
                            <Field label="Min Range" value={formData.process?.minRange || ''} type="number" onChange={v => handleChange('process.minRange', parseFloat(v))} />
                            <Field label="Max Range" value={formData.process?.maxRange || ''} type="number" onChange={v => handleChange('process.maxRange', parseFloat(v))} />
                        </div>
                    </Section>

                    {/* Procurement Section */}
                    <Section title="Procurement" icon={ShoppingBag}>
                        <div className="grid grid-cols-2 gap-6">
                            <Field label="Manufacturer Part #" value={formData.manufacturerPartId || ''} onChange={v => handleChange('manufacturerPartId', v)} />
                            <Field label="Work Package" value={formData.purchasing?.workPackageId || ''} onChange={v => handleChange('purchasing.workPackageId', v)} />
                        </div>
                    </Section>

                </div>
            </div>
        </div>
    );
};

// --- Helper Components ---

interface SectionProps {
    title: string;
    icon: React.ComponentType<{ size?: number; className?: string }>;
    children: React.ReactNode;
}

const Section = ({ title, icon: Icon, children }: SectionProps) => (
    <div className="bg-slate-950/50 border border-slate-800 rounded-lg overflow-hidden">
        <div className="px-6 py-3 border-b border-slate-800 bg-slate-900 flex items-center gap-3">
            <Icon size={18} className="text-mining-teal" />
            <h4 className="font-semibold text-slate-200">{title}</h4>
        </div>
        <div className="p-6">
            {children}
        </div>
    </div>
);

interface FieldProps {
    label: string;
    value: string | number;
    onChange: (value: string) => void;
    type?: string;
    disabled?: boolean;
}

const Field = ({ label, value, onChange, type = "text", disabled = false }: FieldProps) => (
    <div>
        <label className="block text-xs font-medium text-slate-500 mb-1 uppercase tracking-wider">{label}</label>
        <input
            type={type}
            value={value}
            onChange={e => onChange(e.target.value)}
            disabled={disabled}
            className={`w-full bg-slate-950 border border-slate-800 rounded-md px-3 py-2 text-sm focus:outline-none focus:border-mining-teal focus:ring-1 focus:ring-mining-teal transition-colors ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
        />
    </div>
);

interface SelectProps {
    label: string;
    value: string;
    options: string[];
    onChange: (value: string) => void;
}

const Select = ({ label, value, options, onChange }: SelectProps) => (
    <div>
        <label className="block text-xs font-medium text-slate-500 mb-1 uppercase tracking-wider">{label}</label>
        <select
            value={value}
            onChange={e => onChange(e.target.value)}
            className="w-full bg-slate-950 border border-slate-800 rounded-md px-3 py-2 text-sm focus:outline-none focus:border-mining-teal focus:ring-1 focus:ring-mining-teal transition-colors"
        >
            <option value="">-- Select --</option>
            {options.map((opt: string) => (
                <option key={opt} value={opt}>{opt}</option>
            ))}
        </select>
    </div>
);
