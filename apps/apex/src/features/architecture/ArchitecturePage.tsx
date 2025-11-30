import { Card } from '../../shared/components/Card';
import { useArchitectureCheckpoints } from '../../shared/api/hooks';

export default function ArchitecturePage() {
  const { data: checkpoints } = useArchitectureCheckpoints();

  return (
    <div className="space-y-6">
      <div>
        <p className="text-sm text-slate-400">Architecture</p>
        <h1 className="text-2xl font-semibold text-white">Checkpoints</h1>
        <p className="text-sm text-slate-500">Demo data — wire to owner.architecture_checkpoints.</p>
      </div>

      <Card title="Timeline" description="Planned vs done">
        <div className="space-y-4">
          {checkpoints.map((cp) => (
            <div
              key={cp.version}
              className="rounded-lg border border-white/5 bg-white/5 p-4 flex items-start justify-between"
            >
              <div>
                <p className="text-xs text-slate-400">Version</p>
                <p className="text-sm font-semibold text-white">{cp.version}</p>
                <p className="text-xs text-slate-500 mt-1">{cp.summary}</p>
                <p className="text-xs text-slate-500">Risks: {cp.risks}</p>
              </div>
              <StatusBadge status={cp.status} />
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  const styles: Record<string, string> = {
    planned: 'bg-slate-400/20 text-slate-100',
    in_progress: 'bg-blue-400/20 text-blue-100',
    done: 'bg-emerald-400/20 text-emerald-100',
    skipped: 'bg-amber-400/20 text-amber-100',
  };
  return (
    <span className={`rounded-full px-3 py-1 text-xs font-semibold ${styles[status] || ''}`}>
      {status}
    </span>
  );
}
