import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Allotment } from 'allotment';
import 'allotment/dist/style.css';
import { cn } from '@/lib/utils';
import {
  Files,
  Search,
  GitGraph,
  Bug,
  Settings,
  User,
  FileUp,
  Command,
  Sparkles
} from 'lucide-react';
import { CommandPalette } from '../ui/CommandPalette';

interface AppLayoutProps {
  children: React.ReactNode;
  onActivityChange?: (activity: string) => void;
}

export const AppLayout = ({ children, onActivityChange }: AppLayoutProps) => {
  const navigate = useNavigate();
  const [sidebarVisible, setSidebarVisible] = useState(true);
  const [activeActivity, setActiveActivity] = useState('explorer');
  const [commandPaletteOpen, setCommandPaletteOpen] = useState(false);

  // Global keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Ctrl+K or Cmd+K - Open command palette
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        setCommandPaletteOpen(true);
      }

      // Escape - Close command palette
      if (e.key === 'Escape' && commandPaletteOpen) {
        setCommandPaletteOpen(false);
      }

      // Ctrl+P - Quick file/asset search
      if ((e.ctrlKey || e.metaKey) && e.key === 'p') {
        e.preventDefault();
        setCommandPaletteOpen(true);
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [commandPaletteOpen]);

  // Notify parent when activity changes
  useEffect(() => {
    if (onActivityChange) {
      onActivityChange(activeActivity);
    }
  }, [activeActivity, onActivityChange]);

  const handleSearchClick = useCallback(() => {
    setCommandPaletteOpen(true);
  }, []);

  return (
    <div className="flex h-screen w-screen flex-col bg-[#1e1e1e] text-[#cccccc] overflow-hidden font-sans">
      {/* Title Bar with Search */}
      <div className="h-10 bg-[#3c3c3c] border-b border-[#2b2b2b] flex items-center justify-between px-4 select-none">
        {/* Left: Logo */}
        <div className="flex items-center gap-2">
          <Sparkles size={18} className="text-mining-teal" />
          <span className="text-sm font-semibold text-white">SYNAPSE</span>
        </div>

        {/* Center: Search Bar */}
        <div
          onClick={handleSearchClick}
          className="flex items-center gap-2 bg-[#2d2d2d] hover:bg-[#383838] border border-[#454545] rounded-md px-3 py-1.5 cursor-pointer transition-colors w-[400px] max-w-[50vw]"
        >
          <Search size={14} className="text-slate-400" />
          <span className="text-sm text-slate-400 flex-1">Search anything...</span>
          <div className="flex items-center gap-1">
            <kbd className="px-1.5 py-0.5 text-xs bg-[#3c3c3c] text-slate-400 rounded border border-[#454545]">
              ⌘
            </kbd>
            <kbd className="px-1.5 py-0.5 text-xs bg-[#3c3c3c] text-slate-400 rounded border border-[#454545]">
              K
            </kbd>
          </div>
        </div>

        {/* Right: Actions */}
        <div className="flex items-center gap-2">
          <button
            onClick={handleSearchClick}
            className="p-1.5 hover:bg-[#454545] rounded transition-colors"
            title="Command Palette (Ctrl+K)"
          >
            <Command size={16} className="text-slate-400" />
          </button>
        </div>
      </div>

      {/* Main Area */}
      <div className="flex-1 flex overflow-hidden">
        {/* Activity Bar */}
        <div className="w-[48px] flex flex-col items-center py-2 bg-[#333333] border-r border-[#2b2b2b] z-10">
          <ActivityBarItem
            icon={Files}
            active={activeActivity === 'explorer'}
            tooltip="Explorer"
            onClick={() => {
              if (activeActivity === 'explorer' && sidebarVisible) {
                setSidebarVisible(false);
              } else {
                setSidebarVisible(true);
                setActiveActivity('explorer');
              }
            }}
          />
          <ActivityBarItem
            icon={Search}
            active={activeActivity === 'search'}
            tooltip="Search (Ctrl+K)"
            onClick={() => setCommandPaletteOpen(true)}
          />
          <ActivityBarItem
            icon={GitGraph}
            active={activeActivity === 'git'}
            tooltip="Metamodel"
            onClick={() => {
              setActiveActivity('git');
              navigate('/metamodel');
            }}
          />
          <ActivityBarItem
            icon={Bug}
            active={activeActivity === 'debug'}
            tooltip="Rules & Debug"
            onClick={() => {
              setActiveActivity('debug');
              navigate('/rules');
            }}
          />
          <ActivityBarItem
            icon={FileUp}
            active={activeActivity === 'import'}
            tooltip="Import Data"
            onClick={() => {
              setActiveActivity('import');
              navigate('/modern-ingestion');
            }}
          />

          <div className="flex-1" />

          <ActivityBarItem
            icon={User}
            active={activeActivity === 'account'}
            tooltip="Account"
            onClick={() => setActiveActivity('account')}
          />
          <ActivityBarItem
            icon={Settings}
            active={activeActivity === 'settings'}
            tooltip="Settings"
            onClick={() => setActiveActivity('settings')}
          />
        </div>

        {/* Resizable Content */}
        <div className="flex-1 h-full relative">
          <Allotment>
            <Allotment.Pane
              visible={sidebarVisible}
              minSize={170}
              preferredSize={300}
              maxSize={600}
              className="bg-[#252526]"
            >
              <div className="h-full flex flex-col">
                <div className="h-9 px-4 flex items-center text-xs font-bold uppercase tracking-wide text-[#bbbbbb] bg-[#252526]">
                  Explorer
                </div>
                <div className="flex-1 overflow-y-auto">
                  {/* Sidebar Content Placeholder */}
                  <div className="p-4 text-sm text-[#8b949e]">Sidebar Content</div>
                </div>
              </div>
            </Allotment.Pane>

            <Allotment.Pane>
              <div className="h-full bg-[#1e1e1e] flex flex-col">
                {/* Tabs Placeholder */}
                <div className="h-9 bg-[#2d2d2d] flex items-center overflow-x-auto">
                  <div className="px-3 py-2 bg-[#1e1e1e] border-t-2 border-[#007fd4] text-white text-sm min-w-[120px] flex items-center">
                    Welcome
                  </div>
                </div>
                {/* Editor Content */}
                <div className="flex-1 overflow-auto p-4">{children}</div>
              </div>
            </Allotment.Pane>
          </Allotment>
        </div>
      </div>

      {/* Status Bar */}
      <div className="h-[22px] bg-[#007fd4] text-white flex items-center px-3 text-xs justify-between select-none z-20">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1 hover:bg-white/10 px-1 rounded cursor-pointer">
            <GitGraph size={12} />
            <span>main*</span>
          </div>
          <div className="flex items-center gap-1 hover:bg-white/10 px-1 rounded cursor-pointer">
            <Bug size={12} />
            <span>0 errors</span>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <div
            onClick={handleSearchClick}
            className="flex items-center gap-1 hover:bg-white/10 px-2 rounded cursor-pointer"
          >
            <Search size={12} />
            <span>Ctrl+K to search</span>
          </div>
          <div className="hover:bg-white/10 px-1 rounded cursor-pointer">SYNAPSE v0.2.2</div>
        </div>
      </div>

      {/* Command Palette */}
      <CommandPalette
        isOpen={commandPaletteOpen}
        onClose={() => setCommandPaletteOpen(false)}
      />
    </div>
  );
};

interface ActivityBarItemProps {
  icon: React.ElementType;
  active?: boolean;
  tooltip?: string;
  onClick?: () => void;
}

const ActivityBarItem = ({ icon: Icon, active, tooltip, onClick }: ActivityBarItemProps) => {
  return (
    <div
      onClick={onClick}
      title={tooltip}
      className={cn(
        'w-[48px] h-[48px] flex items-center justify-center cursor-pointer transition-colors relative group',
        active ? 'text-white' : 'text-[#858585] hover:text-white'
      )}
    >
      {active && <div className="absolute left-0 top-0 bottom-0 w-[2px] bg-[#007fd4]" />}
      <Icon size={24} strokeWidth={1.5} />

      {/* Tooltip */}
      {tooltip && (
        <div className="absolute left-full ml-2 px-2 py-1 bg-[#252526] text-white text-xs rounded shadow-lg opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap z-50 border border-[#454545]">
          {tooltip}
        </div>
      )}
    </div>
  );
};
