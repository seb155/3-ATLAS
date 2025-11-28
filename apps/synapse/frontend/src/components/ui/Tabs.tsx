import React from 'react';

interface Tab {
    id: string;
    label: string;
    icon?: React.ElementType;
    count?: number;
}

interface TabsProps {
    tabs: Tab[];
    activeTab: string;
    onChange: (id: string) => void;
    className?: string;
}

export const Tabs: React.FC<TabsProps> = ({ tabs, activeTab, onChange, className = '' }) => {
    return (
        <div className={`flex items-center border-b border-slate-800 bg-slate-900/50 ${className}`}>
            {tabs.map(tab => {
                const isActive = activeTab === tab.id;
                const Icon = tab.icon;

                return (
                    <button
                        key={tab.id}
                        onClick={() => onChange(tab.id)}
                        className={`
                            flex items-center px-4 py-3 text-sm font-medium border-b-2 transition-colors
                            ${isActive
                                ? 'border-mining-teal text-mining-teal bg-mining-teal/5'
                                : 'border-transparent text-slate-400 hover:text-slate-200 hover:bg-slate-800'
                            }
                        `}
                    >
                        {Icon && <Icon size={16} className="mr-2" />}
                        {tab.label}
                        {tab.count !== undefined && (
                            <span className="ml-2 px-1.5 py-0.5 bg-slate-800 rounded-full text-[10px] text-slate-400">
                                {tab.count}
                            </span>
                        )}
                    </button>
                );
            })}
        </div>
    );
};
