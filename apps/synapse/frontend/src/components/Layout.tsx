import { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  LayoutDashboard, Network, Database, FileJson, Menu, LogOut,
  BookOpen, User, ChevronRight, Settings, Terminal, Zap,
  Sun, Moon, ChevronDown, Upload, CheckCircle2, Cable, Layers,
  Folder, FolderInput, FolderCog, FolderOutput, FolderLock, Keyboard,
  Activity, Wrench
} from 'lucide-react';
import { Toaster } from 'react-hot-toast';
import { useThemeStore } from '../store/useThemeStore';
import { useAuthStore } from '../store/useAuthStore';
import { useProjectStore } from '../store/useProjectStore';
import { useAppStore } from '../store/useAppStore';
import { useLogStore } from '../store/useLogStore';
import { CreateProjectModal } from './projects/CreateProjectModal';
import { ProjectSelector } from './projects/ProjectSelector';
import { useKeyboardShortcuts, KeyboardShortcut } from '../hooks/useKeyboardShortcuts';
import { KeyboardShortcutsModal } from './KeyboardShortcutsModal';
import { CommandPalette } from './ui/CommandPalette';

// Build info injected by Vite at build time
declare const __APP_VERSION__: string;
declare const __BUILD_NUMBER__: string;

interface Project {
  id: string;
  name: string;
  client_id: string;
  description?: string;
}

interface LayoutProps {
  children: React.ReactNode;
  currentView: string;
  setView: (view: string) => void;
}

interface MenuItem {
  id: string;
  label: string;
  icon: any;
  view?: string;
  children?: MenuItem[];
}

export const Layout = ({ children, currentView, setView }: LayoutProps) => {
  const navigate = useNavigate();
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const [isCreateProjectOpen, setIsCreateProjectOpen] = useState(false);
  const [showShortcutsHelp, setShowShortcutsHelp] = useState(false);
  const [showCommandPalette, setShowCommandPalette] = useState(false);
  const [expandedSections, setExpandedSections] = useState<Set<string>>(
    new Set(['project', 'data']) // Default expanded sections
  );

  const { user, logout } = useAuthStore();
  const { currentClient, currentProject, allProjects, allClients, setCurrentProject, setCurrentClient } = useProjectStore();
  const { refreshData } = useAppStore();
  const { toggleConsole } = useLogStore();
  const { isDarkMode, toggleTheme } = useThemeStore();

  // Global keyboard shortcuts
  const shortcuts: KeyboardShortcut[] = [
    {
      key: 'k',
      ctrl: true,
      description: 'Open Command Palette',
      category: 'global',
      action: () => setShowCommandPalette(true)
    },
    {
      key: 'b',
      ctrl: true,
      description: 'Toggle Sidebar',
      category: 'global',
      action: () => setSidebarOpen(!sidebarOpen)
    },
    {
      key: '\\',
      ctrl: true,
      description: 'Toggle DevConsole',
      category: 'global',
      action: () => toggleConsole()
    },
    {
      key: '/',
      ctrl: true,
      description: 'Show keyboard shortcuts',
      category: 'global',
      action: () => setShowShortcutsHelp(true)
    },
    {
      key: 'Escape',
      description: 'Close modals',
      category: 'global',
      action: () => {
        setShowShortcutsHelp(false);
        setUserMenuOpen(false);
        setShowCommandPalette(false);
      }
    }
  ];

  useKeyboardShortcuts({ shortcuts, enabled: true });

  const menuStructure: MenuItem[] = [
    {
      id: 'project',
      label: 'Project',
      icon: Folder,
      children: [
        { id: 'dashboard', label: 'Overview', icon: LayoutDashboard, view: 'dashboard' }
      ]
    },
    {
      id: 'data',
      label: 'Data',
      icon: FolderInput,
      children: [
        { id: 'modern-ingestion', label: 'Import', icon: Upload, view: 'modern-ingestion' },
        { id: 'validation-results', label: 'Validation', icon: CheckCircle2, view: 'validation-results' }
      ]
    },
    {
      id: 'engineering',
      label: 'Engineering',
      icon: FolderCog,
      children: [
        { id: 'explorer', label: 'Asset Explorer', icon: Network, view: 'engineering' },
        { id: 'locations', label: 'Locations', icon: Layers, view: 'locations' }
      ]
    },
    {
      id: 'automation',
      label: 'Automation',
      icon: Zap,
      children: [
        { id: 'rules', label: 'Rules Library', icon: BookOpen, view: 'rules' }
      ]
    },
    {
      id: 'outputs',
      label: 'Outputs',
      icon: FolderOutput,
      children: [
        { id: 'cables', label: 'Cable Schedule', icon: Cable, view: 'cables' }
      ]
    },
    {
      id: 'admin',
      label: 'Admin',
      icon: FolderLock,
      children: [
        { id: 'activity', label: 'Activity Log', icon: Activity, view: 'admin/activity' },
        { id: 'rule-executor', label: 'Rule Executor', icon: Zap, view: 'rule-executor' },
        { id: 'admin-tools', label: 'Admin Tools', icon: Wrench, view: 'admin/tools' },
        { id: 'metamodel', label: 'Metamodel', icon: Database, view: 'metamodel' }
      ]
    }
  ];

  const toggleSection = (sectionId: string) => {
    setExpandedSections(prev => {
      const next = new Set(prev);
      next.has(sectionId) ? next.delete(sectionId) : next.add(sectionId);
      return next;
    });
  };

  const handleProjectSwitch = async (project: Project) => { // Changed project type from any to Project
    setCurrentProject(project);
    // Data will auto-refresh via App.tsx useEffect
  };

  const handleLogout = () => {
    logout();
    // NO window.location.reload() - React will handle re-render
  };

  const getInitials = (name?: string) => {
    if (!name) return 'U';
    return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
  };

  return (
    <div className="flex h-screen bg-slate-900 text-slate-200 overflow-hidden">
      {/* Sidebar */}
      <div className={`${sidebarOpen ? 'w-64' : 'w-20'} transition-all duration-200 ease-out bg-slate-950 border-r border-slate-800 flex flex-col`}>
        {/* Logo */}
        <div className="h-16 flex items-center justify-between px-4 border-b border-slate-800">
          {sidebarOpen && <span className="font-mono font-bold text-mining-teal text-xl tracking-tight">SYNAPSE</span>}
          <button onClick={() => setSidebarOpen(!sidebarOpen)} className="p-2 hover:bg-slate-800 rounded">
            <Menu size={20} />
          </button>
        </div>

        {/* Project Switcher - REMOVED FROM SIDEBAR, NOW IN HEADER */}

        {/* Navigation - Hierarchical */}
        <nav className="flex-1 py-6 px-2 space-y-1 overflow-y-auto">
          {menuStructure.map((section) => {
            const SectionIcon = section.icon;
            const isExpanded = expandedSections.has(section.id);

            return (
              <div key={section.id} className="space-y-1">
                {/* Section Header */}
                <button
                  onClick={() => toggleSection(section.id)}
                  className="w-full flex items-center justify-between px-3 py-2 text-sm font-medium text-slate-400 hover:text-white hover:bg-slate-800/50 rounded-lg transition-colors"
                  title={!sidebarOpen ? section.label : undefined}
                >
                  <div className="flex items-center gap-2">
                    <SectionIcon size={18} />
                    {sidebarOpen && <span>{section.label}</span>}
                  </div>
                  {sidebarOpen && (
                    <ChevronDown
                      size={14}
                      className={`text-slate-500 transition-transform duration-200 ${isExpanded ? 'rotate-0' : '-rotate-90'
                        }`}
                    />
                  )}
                </button>

                {/* Section Items */}
                {isExpanded && section.children?.map((item) => {
                  const ItemIcon = item.icon;
                  const isActive = location.pathname === `/${item.view}` ||
                    (location.pathname.startsWith('/engineering') && item.view === 'engineering');

                  return (
                    <button
                      key={item.id}
                      onClick={() => navigate(`/${item.view}`)}
                      className={`w-full flex items-center px-3 py-2 ${sidebarOpen ? 'ml-6' : 'ml-0'
                        } text-sm rounded-lg transition-colors ${isActive
                          ? 'bg-mining-teal/10 text-mining-teal border-l-2 border-mining-teal'
                          : 'text-slate-400 hover:bg-slate-800 hover:text-white'
                        }`}
                      title={!sidebarOpen ? item.label : undefined}
                    >
                      <ItemIcon size={18} />
                      {sidebarOpen && <span className="ml-3">{item.label}</span>}
                    </button>
                  );
                })}
              </div>
            );
          })}
        </nav>

        {/* Footer Actions */}
        <div className="p-4 border-t border-slate-800 space-y-2">
          <button
            onClick={handleLogout}
            className="w-full flex items-center p-2 text-sm text-red-400 hover:bg-red-900/20 hover:text-red-300 rounded transition-colors"
          >
            <LogOut size={16} className="mr-2" />
            {sidebarOpen && <span>Logout</span>}
          </button>

          {sidebarOpen && (
            <div className="mt-4 text-xs font-mono">
              <div className="text-slate-500">SYNAPSE</div>
              <div className="text-mining-teal">
                v{typeof __APP_VERSION__ !== 'undefined' ? __APP_VERSION__ : '0.2.2'}
                {typeof __BUILD_NUMBER__ !== 'undefined' && (
                  <span className="text-slate-600 ml-1">#{__BUILD_NUMBER__.slice(-6)}</span>
                )}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <header className="h-16 bg-slate-900 border-b border-slate-800 flex items-center justify-between px-6 shadow-sm">
          {/* Left: ProjectSelector */}
          <div className="flex items-center gap-4">
            <ProjectSelector />

            {/* Breadcrumb */}
            <div className="flex items-center gap-2 text-sm text-slate-500">
              <ChevronRight size={14} className="text-slate-600" />
              <span className="text-mining-teal">
                {menuStructure
                  .flatMap(section => section.children || [])
                  .find(item => item.view === currentView)?.label}
              </span>
            </div>
          </div>

          {/* User Menu */}
          <div className="flex items-center gap-3">
            <button
              onClick={toggleTheme}
              className="p-2 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition-colors"
              title={isDarkMode ? "Switch to Light Mode" : "Switch to Dark Mode"}
            >
              {isDarkMode ? <Moon size={18} /> : <Sun size={18} />}
            </button>

            <button
              onClick={() => setShowShortcutsHelp(true)}
              className="p-2 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition-colors"
              title="Keyboard Shortcuts (Ctrl+/)"
            >
              <Keyboard size={18} />
            </button>

            <button
              onClick={toggleConsole}
              className="p-2 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition-colors"
              title="Dev Console (Ctrl+`)"
            >
              <Terminal size={18} />
            </button>

            <div className="relative">
              <button
                onClick={() => setUserMenuOpen(!userMenuOpen)}
                className="flex items-center gap-3 px-3 py-2 bg-slate-800 hover:bg-slate-700 rounded-lg transition-colors"
              >
                <div className="w-8 h-8 bg-mining-teal rounded-full flex items-center justify-center text-white text-sm font-bold">
                  {getInitials(user?.full_name)}
                </div>
                {user && (
                  <div className="text-left">
                    <div className="text-sm text-white font-medium">{user.full_name}</div>
                    <div className="text-xs text-slate-400">{user.email}</div>
                  </div>
                )}
              </button>

              {/* User Dropdown */}
              {userMenuOpen && (
                <div className="absolute right-0 top-full mt-2 w-64 bg-slate-800 border border-slate-700 rounded-lg shadow-xl z-50">
                  <div className="p-4 border-b border-slate-700">
                    <div className="text-white font-medium">{user?.full_name}</div>
                    <div className="text-xs text-slate-400">{user?.email}</div>
                    <div className="mt-2 inline-block px-2 py-1 bg-slate-700 rounded text-xs text-slate-300">
                      {user?.role}
                    </div>
                  </div>
                  <div className="p-2">
                    <button className="w-full flex items-center gap-2 px-3 py-2 text-sm text-slate-300 hover:bg-slate-700 rounded transition-colors">
                      <User size={16} />
                      Profile
                    </button>
                    <button className="w-full flex items-center gap-2 px-3 py-2 text-sm text-slate-300 hover:bg-slate-700 rounded transition-colors">
                      <Settings size={16} />
                      Settings
                    </button>
                    <button
                      onClick={toggleConsole}
                      className="w-full flex items-center gap-2 px-3 py-2 text-sm text-slate-300 hover:bg-slate-700 rounded transition-colors"
                    >
                      <Terminal size={16} />
                      Dev Console
                    </button>
                  </div>
                  <div className="p-2 border-t border-slate-700">
                    <button
                      onClick={handleLogout}
                      className="w-full flex items-center gap-2 px-3 py-2 text-sm text-red-400 hover:bg-red-900/20 rounded transition-colors"
                    >
                      <LogOut size={16} />
                      Logout
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="flex-1 overflow-y-auto relative">
          {children}
        </main>
      </div>

      {/* Modals */}
      <CreateProjectModal
        isOpen={isCreateProjectOpen}
        onClose={() => setIsCreateProjectOpen(false)}
      />

      {showShortcutsHelp && (
        <KeyboardShortcutsModal onClose={() => setShowShortcutsHelp(false)} />
      )}

      {/* Command Palette */}
      <CommandPalette
        isOpen={showCommandPalette}
        onClose={() => setShowCommandPalette(false)}
        onToggleDevConsole={toggleConsole}
      />

      {/* Toast Notifications */}
      <Toaster
        position="bottom-right"
        toastOptions={{
          className: '',
          style: {
            background: '#1e293b',
            color: '#e2e8f0',
            border: '1px solid #334155',
          },
          success: {
            iconTheme: {
              primary: '#2dd4bf',
              secondary: '#1e293b',
            },
          },
          error: {
            iconTheme: {
              primary: '#f87171',
              secondary: '#1e293b',
            },
          },
        }}
      />
    </div>
  );
};
