import { Activity } from 'lucide-react';

export function StatusBar() {
  return (
    <footer className="h-8 border-t border-border bg-card px-4 flex items-center justify-between text-xs text-muted-foreground">
      <div className="flex items-center gap-4">
        <span className="flex items-center gap-1">
          <Activity className="h-3 w-3" />
          Ready
        </span>
        <span>Nexus v0.1.0-alpha</span>
      </div>
      <div className="flex items-center gap-4">
        <span>Knowledge Graph Portal</span>
      </div>
    </footer>
  );
}
