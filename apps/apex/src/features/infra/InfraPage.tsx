import { Card } from '../../shared/components/Card';
import { links } from '../../shared/config/links';

const tools = [
  { name: 'Synapse UI', url: links.synapseUI, desc: 'Frontend application' },
  { name: 'API Docs', url: links.apiDocs, desc: 'FastAPI docs' },
  { name: 'Grafana', url: links.grafana, desc: 'Metrics & logs dashboards' },
  { name: 'Vitest UI', url: dashboards.vitestUI, desc: 'Portal unit tests (Vitest)' },
  { name: 'pgAdmin', url: links.pgadmin, desc: 'Postgres admin UI' },
];

export default function InfraPage() {
  return (
    <div className="space-y-6">
      <div>
        <p className="text-sm text-slate-400">Tools</p>
        <h1 className="text-2xl font-semibold text-white">Workspace Access</h1>
        <p className="text-sm text-slate-500">
          Quick links to core services. Replace with live status pings later.
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        {tools.map((tool) => (
          <Card key={tool.name} title={tool.name} description={tool.desc}>
            <a className="text-sm text-emerald-200 hover:text-emerald-100" href={tool.url}>
              Open
            </a>
          </Card>
        ))}
      </div>
    </div>
  );
}
