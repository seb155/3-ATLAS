import { useQuery } from '@tanstack/react-query';
import { ArchitectureCheckpoint, HealthScore, TechDebtItem, TestRun } from './types';
import { client } from './client';

// Simple fallback to mock data to keep UI usable if backend not ready
async function mockDelay<T>(data: T, delay = 80): Promise<T> {
  return new Promise((resolve) => setTimeout(() => resolve(data), delay));
}

export function useHealthScores() {
  return useQuery({
    queryKey: ['health-scores'],
    queryFn: async () => {
      try {
        const { data } = await client.get<HealthScore[]>('/api/v1/owner/health-scorecards');
        return data;
      } catch (err) {
        return mockDelay<HealthScore[]>([
          {
            area: 'Backend',
            reliability: 4.3,
            dx: 4.1,
            observability: 4.6,
            ux: 3.8,
            version: 'v0.2.2',
            created_at: new Date().toISOString(),
          },
          {
            area: 'Frontend',
            reliability: 4.0,
            dx: 4.2,
            observability: 4.2,
            ux: 4.0,
            version: 'v0.2.2',
            created_at: new Date().toISOString(),
          },
          {
            area: 'Infra',
            reliability: 4.5,
            dx: 4.0,
            observability: 4.7,
            ux: 3.7,
            version: 'v0.2.2',
            created_at: new Date().toISOString(),
          },
        ]);
      }
    },
  });
}

export function useTestRuns() {
  return useQuery({
    queryKey: ['test-runs'],
    queryFn: async () => {
      try {
        const { data } = await client.get<TestRun[]>('/api/v1/owner/test-runs');
        return data.map((run) => ({
          ...run,
          passRate: run.total ? `${Math.round(((run.total - run.failed) / run.total) * 100)}%` : '—',
        }));
      } catch (err) {
        return mockDelay<TestRun[]>([
          { id: 'run-001', component: 'Backend', suite: 'regression', passRate: '95%', total: 130, failed: 6, passed: 124, skipped: 0, reportUrl: '#', version: 'v0.2.2', origin: 'demo' },
          { id: 'run-002', component: 'Frontend', suite: 'smoke', passRate: '94%', total: 104, failed: 6, passed: 98, skipped: 0, reportUrl: '#', version: 'v0.2.2', origin: 'demo' },
          { id: 'run-003', component: 'E2E', suite: 'full', passRate: '100%', total: 42, failed: 0, passed: 42, skipped: 0, reportUrl: '#', version: 'v0.2.2', origin: 'demo' },
        ]);
      }
    },
  });
}

export function useTechDebtItems() {
  return useQuery({
    queryKey: ['tech-debt'],
    queryFn: async () => {
      try {
        const { data } = await client.get<TechDebtItem[]>('/api/v1/owner/tech-debt-items');
        return data;
      } catch (err) {
        return mockDelay<TechDebtItem[]>([
          { code: 'CR-20251126-01', title: 'Stabilize import error handling', area: 'backend', impact: 'high', status: 'open', target: 'v0.2.3' },
          { code: 'CR-20251126-02', title: 'Standardize logging fields', area: 'cross-cutting', impact: 'medium', status: 'in_progress', target: 'v0.2.4' },
        ]);
      }
    },
  });
}

export function useArchitectureCheckpoints() {
  return useQuery({
    queryKey: ['architecture-checkpoints'],
    queryFn: async () => {
        try {
          const { data } = await client.get<ArchitectureCheckpoint[]>('/api/v1/owner/architecture-checkpoints');
          return data;
        } catch (err) {
          return mockDelay<ArchitectureCheckpoint[]>([
            { version: 'v0.2.3', status: 'planned', summary: '3-tier asset model readiness review', risks: 'Data model alignment with procurement' },
            { version: 'v0.2.4', status: 'done', summary: 'Breakdown structures navigation', risks: 'Tree performance at scale' },
          ]);
        }
      },
  });
}
