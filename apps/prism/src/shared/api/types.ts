export type HealthScore = {
  area: string;
  reliability: number;
  dx: number;
  observability: number;
  ux: number;
  version: string;
  created_at: string;
};

export type TestRun = {
  id: string;
  started_at?: string;
  finished_at?: string;
  component: string;
  suite: string;
  total: number;
  failed: number;
  passed: number;
  skipped: number;
  reportUrl?: string;
  version: string;
  origin: string;
  passRate?: string; // derived client-side
};

export type TechDebtItem = {
  code: string;
  title: string;
  area: string;
  impact: 'high' | 'medium' | 'low';
  status: 'open' | 'in_progress' | 'done' | 'wont_fix';
  target?: string;
};

export type ArchitectureCheckpoint = {
  version: string;
  status: 'planned' | 'in_progress' | 'done' | 'skipped';
  summary: string;
  risks?: string;
};
