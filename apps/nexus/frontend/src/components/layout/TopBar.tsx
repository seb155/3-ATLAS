import { Menu } from 'lucide-react';
import { useAppStore } from '@/stores/useAppStore';
import { ThemeSelector } from '@/components/theme/ThemeSelector';

export function TopBar() {
  const { toggleSidebar } = useAppStore();

  return (
    <header className="h-14 border-b border-border bg-card px-4 flex items-center justify-between">
      <div className="flex items-center gap-4">
        <button
          onClick={toggleSidebar}
          className="p-2 rounded-lg hover:bg-accent transition-colors"
          aria-label="Toggle sidebar"
        >
          <Menu className="h-5 w-5" />
        </button>
        <h1 className="text-xl font-bold text-gradient">
          Nexus
        </h1>
      </div>

      <ThemeSelector />
    </header>
  );
}
