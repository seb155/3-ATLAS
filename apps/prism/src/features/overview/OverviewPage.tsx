import { Card } from '../../shared/components/Card';
import { useHealthScores, useTechDebtItems, useTestRuns } from '../../shared/api/hooks';
import { dashboards } from '../../shared/config/links';

export default function OverviewPage() {
  const { data: health } = useHealthScores();
  const { data: tests } = useTestRuns();
  const { data: debt } = useTechDebtItems();

  const summaryScores = [
    { label: 'Reliability', value: health?.[0]?.reliability ?? 4.2, accent: 'from-emerald-400/60 to-green-500/40' },
    { label: 'DX', value: health?.[0]?.dx ?? 4.0, accent: 'from-blue-400/60 to-indigo-500/40' },
    { label: 'Observability', value: health?.[0]?.observability ?? 4.5, accent: 'from-cyan-400/60 to-sky-500/40' },
    { label: 'UX', value: health?.[0]?.ux ?? 3.9, accent: 'from-amber-300/60 to-orange-500/40' },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-slate-400">Snapshot</p>
          <h1 className="text-2xl font-semibold text-white">Owner Overview</h1>
          <p className="text-sm text-slate-500">Demo data — wire to owner APIs next.</p>
        </div>
        <div className="rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-sm text-slate-200">
          Version: v0.2.2 (demo)
        </div>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {summaryScores.map((score) => (
          <Card
            key={score.label}
            title={score.label}
            className="relative overflow-hidden"
            description="Average score"
          >
            <div
              className={`absolute inset-0 bg-gradient-to-br ${score.accent} opacity-20 blur-2xl`}
              aria-hidden
            />
            <p className="text-3xl font-semibold text-white">{score.value.toFixed(1)}</p>
          </Card>
        ))}
      </div>

      <div className="grid gap-4 lg:grid-cols-3">
        <Card title="Latest Test Runs" description="Backend, Frontend, E2E status" className="lg:col-span-2">
          <div className="divide-y divide-white/5">
            {tests?.map((run) => (
              <div key={run.id} className="flex items-center justify-between py-3">
                <div>
                  <p className="font-medium text-white">{run.component}</p>
                  <p className="text-sm text-slate-400">
                    {run.total} tests · {run.failed} failed
                  </p>
                </div>
                <div className="flex items-center gap-3">
                  <span
                    className={`rounded-full px-3 py-1 text-xs font-semibold ${
                      run.failed === 0
                        ? 'bg-emerald-400/20 text-emerald-200'
                        : 'bg-amber-400/20 text-amber-100'
                    }`}
                  >
                    {run.failed === 0 ? 'Pass' : 'Warn'}
                  </span>
                  <a className="text-sm text-emerald-200 hover:text-emerald-100" href={run.reportUrl}>
                    View
                  </a>
                </div>
              </div>
            ))}
          </div>
        </Card>

        <Card title="Top Tech Debt" description="High-impact review items">
          <div className="space-y-3">
            {debt?.map((item) => (
              <div key={item.code} className="rounded-lg border border-white/5 bg-white/5 p-3">
                <p className="text-xs text-slate-400">{item.code}</p>
                <p className="text-sm font-semibold text-white">{item.title}</p>
                <span className="mt-2 inline-flex rounded-full bg-emerald-400/15 px-2 py-1 text-xs font-medium text-emerald-200">
                  {item.impact} impact · {item.area}
                </span>
              </div>
            ))}
          </div>
        </Card>
      </div>

      <div className="grid gap-4 lg:grid-cols-3">
        <Card
          title="Test Dashboard"
          description="Open ReportPortal for detailed analysis"
          className="lg:col-span-3"
        >
          <div className="flex flex-wrap gap-3">
            <a
              href={dashboards.reportPortalRoot}
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-2 rounded-lg bg-sky-500/20 px-4 py-2 text-sm font-medium text-sky-100 hover:bg-sky-500/30"
            >
              ReportPortal – Launches
            </a>
          </div>
        </Card>
      </div>
    </div>
  );
}
