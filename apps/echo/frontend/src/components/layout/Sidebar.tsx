import { Link, useLocation } from 'react-router-dom';
import { Mic, Library, Settings, Radio } from 'lucide-react';
import { cn } from '@/lib/utils';

const navItems = [
  { path: '/', icon: Mic, label: 'Record' },
  { path: '/library', icon: Library, label: 'Library' },
  { path: '/settings', icon: Settings, label: 'Settings' },
];

export function Sidebar() {
  const location = useLocation();

  return (
    <aside className="w-16 bg-slate-800 border-r border-slate-700 flex flex-col items-center py-4">
      {/* Logo */}
      <div className="mb-8">
        <div className="w-10 h-10 bg-echo-500 rounded-xl flex items-center justify-center">
          <Radio className="w-6 h-6 text-white" />
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex flex-col gap-2">
        {navItems.map((item) => {
          const isActive = location.pathname === item.path;
          const Icon = item.icon;

          return (
            <Link
              key={item.path}
              to={item.path}
              className={cn(
                'w-10 h-10 rounded-lg flex items-center justify-center transition-smooth',
                isActive
                  ? 'bg-echo-500 text-white'
                  : 'text-slate-400 hover:bg-slate-700 hover:text-white'
              )}
              title={item.label}
            >
              <Icon className="w-5 h-5" />
            </Link>
          );
        })}
      </nav>

      {/* Spacer */}
      <div className="flex-1" />

      {/* Version */}
      <div className="text-xs text-slate-500">v0.1</div>
    </aside>
  );
}
