import { Card } from '../../shared/components/Card';
import { useTestRuns } from '../../shared/api/hooks';

export default function TestsPage() {
  const { data: runs } = useTestRuns();

  return (
    <div className="space-y-6">
      <div>
        <p className="text-sm text-slate-400">Tests</p>
        <h1 className="text-2xl font-semibold text-white">Test Runs</h1>
        <p className="text-sm text-slate-500">Demo data — wire to owner.test_runs.</p>
      </div>

      <Card title="Recent Runs" description="Pass rate by component">
        <div className="divide-y divide-white/5">
          {runs?.map((run) => (
            <div key={run.id} className="grid gap-3 py-3 sm:grid-cols-5 sm:items-center">
              <div>
                <p className="text-sm font-semibold text-white">{run.component}</p>
                <p className="text-xs text-slate-400">Suite: {run.suite}</p>
              </div>
              <div className="text-sm text-slate-300 sm:text-center">
                <span className="font-semibold text-emerald-200">{run.passRate}</span>
                <span className="text-slate-500"> pass rate</span>
              </div>
              <div className="text-sm text-slate-300 sm:text-center">
                {run.total} total · {run.failed} failed
              </div>
              <div className="text-sm text-slate-400 sm:text-center">Origin: demo</div>
              <div className="text-sm sm:text-right">
                <a className="text-emerald-200 hover:text-emerald-100" href={run.reportUrl}>
                  View report
                </a>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}
