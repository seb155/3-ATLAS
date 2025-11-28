import { Card } from '../../shared/components/Card';
import { useTechDebtItems } from '../../shared/api/hooks';

export default function TechDebtPage() {
  const { data: debtItems } = useTechDebtItems();

  return (
    <div className="space-y-6">
      <div>
        <p className="text-sm text-slate-400">Tech Debt</p>
        <h1 className="text-2xl font-semibold text-white">Review Items</h1>
        <p className="text-sm text-slate-500">Demo data — wire to owner.tech_debt_items.</p>
      </div>

      <Card title="Open Items" description="Filtered by impact/status">
        <div className="divide-y divide-white/5">
          {debtItems?.map((item) => (
            <div key={item.code} className="flex items-start justify-between gap-3 py-3">
              <div>
                <p className="text-xs text-slate-400">{item.code}</p>
                <p className="text-sm font-semibold text-white">{item.title}</p>
                <p className="text-xs text-slate-500">
                  Area: {item.area} · Target: {item.target}
                </p>
              </div>
              <div className="flex items-center gap-2">
                <Badge kind={item.impact}>{item.impact}</Badge>
                <Badge kind={item.status}>{item.status}</Badge>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}

function Badge({ kind, children }: { kind: string; children: string }) {
  const styles: Record<string, string> = {
    high: 'bg-rose-400/20 text-rose-100',
    medium: 'bg-amber-400/20 text-amber-100',
    low: 'bg-slate-400/20 text-slate-200',
    open: 'bg-emerald-400/20 text-emerald-100',
    in_progress: 'bg-blue-400/20 text-blue-100',
    done: 'bg-slate-500/20 text-slate-100',
  };
  return (
    <span className={`rounded-full px-3 py-1 text-xs font-semibold ${styles[kind] || ''}`}>
      {children}
    </span>
  );
}
