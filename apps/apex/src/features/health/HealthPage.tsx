import { Card } from '../../shared/components/Card';
import { useHealthScores } from '../../shared/api/hooks';

export default function HealthPage() {
  const { data: scores } = useHealthScores();

  return (
    <div className="space-y-6">
      <div>
        <p className="text-sm text-slate-400">Health</p>
        <h1 className="text-2xl font-semibold text-white">Health Scorecards</h1>
        <p className="text-sm text-slate-500">Demo data — wire to owner.health_scorecards.</p>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        {scores?.map((item) => (
          <Card key={item.area} title={item.area} description="Scores by area" className="border-white/10">
            <div className="grid grid-cols-2 gap-3 text-sm">
              <Metric label="Reliability" value={item.reliability} />
              <Metric label="DX" value={item.dx} />
              <Metric label="Observability" value={item.observability} />
              <Metric label="UX" value={item.ux} />
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}

function Metric({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-lg border border-white/5 bg-white/5 p-3">
      <p className="text-xs text-slate-400">{label}</p>
      <p className="text-lg font-semibold text-white">{value.toFixed(1)}</p>
    </div>
  );
}
