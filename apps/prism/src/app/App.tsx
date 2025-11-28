import { NavLink, Route, Routes, Navigate } from 'react-router-dom';
import OverviewPage from '../features/overview/OverviewPage';
import HealthPage from '../features/health/HealthPage';
import TestsPage from '../features/tests/TestsPage';
import TechDebtPage from '../features/techdebt/TechDebtPage';
import ArchitecturePage from '../features/architecture/ArchitecturePage';
import InfraPage from '../features/infra/InfraPage';
import { Fragment } from 'react';
import { env } from '../shared/config/env';

type NavItem = {
  label: string;
  to: string;
};

const navItems: NavItem[] = [
  { label: 'Overview', to: '/' },
  { label: 'Health', to: '/health' },
  { label: 'Tests', to: '/tests' },
  { label: 'Tech Debt', to: '/tech-debt' },
  { label: 'Architecture', to: '/architecture' },
  { label: 'Tools', to: '/infra' },
];

export default function App() {
  return (
    <div className="min-h-screen text-slate-50">
      <header className="sticky top-0 z-10 backdrop-blur bg-slate-950/80 border-b border-white/5">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-emerald-400/30 to-blue-500/20 border border-white/10 flex items-center justify-center text-emerald-200 font-bold">
              OP
            </div>
            <div>
              <p className="text-sm text-slate-300">Owner Portal</p>
              <p className="text-xs text-slate-500">Read-only | synapse_analytics.owner</p>
            </div>
          </div>
          <div className="text-xs text-slate-400 rounded-lg border border-white/10 bg-white/5 px-3 py-2">
            API: <span className="text-emerald-200">{env.apiBaseUrl}</span>
          </div>
          <nav className="flex gap-2 text-sm font-medium">
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  `rounded-lg px-3 py-2 transition-colors ${
                    isActive
                      ? 'bg-white/10 text-white shadow-glass'
                      : 'text-slate-300 hover:bg-white/5 hover:text-white'
                  }`
                }
                end={item.to === '/'}
              >
                {item.label}
              </NavLink>
            ))}
          </nav>
        </div>
      </header>

      <main className="mx-auto max-w-6xl px-6 pb-14 pt-8">
        <Routes>
          <Route path="/" element={<OverviewPage />} />
          <Route path="/health" element={<HealthPage />} />
          <Route path="/tests" element={<TestsPage />} />
          <Route path="/tech-debt" element={<TechDebtPage />} />
          <Route path="/architecture" element={<ArchitecturePage />} />
          <Route path="/infra" element={<InfraPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </div>
  );
}
