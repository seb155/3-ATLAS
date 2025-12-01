import React, { useState, useEffect } from 'react';
import { ChevronLeft, ChevronRight, Columns3, Filter, Zap } from 'lucide-react';

type TabId = 'columns' | 'filters' | 'actions';

interface Tab {
    id: TabId;
    icon: any;
    label: string;
}

interface RightSidebarProps {
    columnsContent?: React.ReactNode;
    filtersContent?: React.ReactNode;
    actionsContent?: React.ReactNode;
    defaultTab?: TabId;
    defaultWidth?: number;
    minWidth?: number;
    maxWidth?: number;
    defaultExpanded?: boolean;
}

export function RightSidebar({
    columnsContent,
    filtersContent,
    actionsContent,
    defaultTab = 'columns',
    defaultWidth = 350,
    minWidth = 280,
    maxWidth = 600,
    defaultExpanded = false
}: RightSidebarProps) {
    const [isExpanded, setIsExpanded] = useState(defaultExpanded);
    const [activeTab, setActiveTab] = useState<TabId>(defaultTab);
    const [width, setWidth] = useState(defaultWidth);
    const [isResizing, setIsResizing] = useState(false);

    const tabs: Tab[] = [
        { id: 'columns', icon: Columns3, label: 'COLUMNS' },
        { id: 'filters', icon: Filter, label: 'FILTERS' },
        { id: 'actions', icon: Zap, label: 'ACTIONS' }
    ];

    const handleTabClick = (tabId: TabId) => {
        if (!isExpanded) {
            setIsExpanded(true);
        }
        setActiveTab(tabId);
    };

    const handleMouseDown = (e: React.MouseEvent) => {
        e.preventDefault();
        setIsResizing(true);
    };

    const handleMouseMove = (e: MouseEvent) => {
        if (!isResizing) return;

        const newWidth = window.innerWidth - e.clientX;
        if (newWidth >= minWidth && newWidth <= maxWidth) {
            setWidth(newWidth);
        }
    };

    const handleMouseUp = () => {
        setIsResizing(false);
    };

    // Add/remove mouse listeners for resizing
    useEffect(() => {
        if (isResizing) {
            window.addEventListener('mousemove', handleMouseMove as any);
            window.addEventListener('mouseup', handleMouseUp);
        } else {
            window.removeEventListener('mousemove', handleMouseMove as any);
            window.removeEventListener('mouseup', handleMouseUp);
        }
        return () => {
            window.removeEventListener('mousemove', handleMouseMove as any);
            window.removeEventListener('mouseup', handleMouseUp);
        };
    }, [isResizing]);

    const renderContent = () => {
        switch (activeTab) {
            case 'columns':
                return columnsContent || <div className="p-4 text-slate-400">No columns content</div>;
            case 'filters':
                return filtersContent || <div className="p-4 text-slate-400">Filters coming soon</div>;
            case 'actions':
                return actionsContent || <div className="p-4 text-slate-400">Actions coming soon</div>;
        }
    };

    if (!isExpanded) {
        // COLLAPSED STATE - Vertical tabs
        return (
            <div className="h-full bg-slate-900 border-l border-slate-800 flex flex-col items-center py-4 gap-6" style={{ width: '40px' }}>
                {tabs.map(tab => {
                    const Icon = tab.icon;
                    const isActive = activeTab === tab.id;

                    return (
                        <button
                            key={tab.id}
                            onClick={() => handleTabClick(tab.id)}
                            className={`
                relative flex items-center justify-center py-4 px-2
                transition-colors
                ${isActive ? 'text-mining-teal bg-slate-800' : 'text-slate-400 hover:text-white hover:bg-slate-800'}
              `}
                            style={{ writingMode: 'vertical-rl', textOrientation: 'mixed' }}
                            title={tab.label}
                        >
                            <Icon size={16} className="mb-2" />
                            <span className="text-xs font-semibold tracking-wider">{tab.label}</span>
                        </button>
                    );
                })}
            </div>
        );
    }

    // EXPANDED STATE - Horizontal tabs + content
    return (
        <div
            className="h-full bg-slate-900 border-l border-slate-800 flex flex-col"
            style={{ width: `${width}px` }}
        >
            {/* Resize Handle */}
            <div
                onMouseDown={handleMouseDown}
                className="absolute left-0 top-0 bottom-0 w-1 cursor-ew-resize hover:bg-mining-teal transition-colors z-10"
            />

            {/* Header with Tabs */}
            <div className="flex items-center border-b border-slate-800">
                {/* Tabs */}
                <div className="flex-1 flex">
                    {tabs.map(tab => {
                        const Icon = tab.icon;
                        const isActive = activeTab === tab.id;

                        return (
                            <button
                                key={tab.id}
                                onClick={() => setActiveTab(tab.id)}
                                className={`
                  flex items-center gap-2 px-4 py-3 border-b-2 transition-colors
                  ${isActive
                                        ? 'border-mining-teal text-mining-teal bg-slate-800/50'
                                        : 'border-transparent text-slate-400 hover:text-white hover:bg-slate-800/30'
                                    }
                `}
                            >
                                <Icon size={16} />
                                <span className="text-sm font-semibold">{tab.label}</span>
                            </button>
                        );
                    })}
                </div>

                {/* Collapse Button */}
                <button
                    onClick={() => setIsExpanded(false)}
                    className="p-2 text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
                    title="Collapse sidebar"
                >
                    <ChevronRight size={18} />
                </button>
            </div>

            {/* Content Area */}
            <div className="flex-1 overflow-y-auto custom-scrollbar">
                {renderContent()}
            </div>
        </div>
    );
}
