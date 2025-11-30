import { useLocation } from 'react-router-dom';
import { Folder, Clock } from 'lucide-react';
import { useRecordingStore } from '@/stores/useRecordingStore';
import { formatDuration } from '@/lib/utils';

const pageTitles: Record<string, string> = {
  '/': 'Record',
  '/library': 'Library',
  '/settings': 'Settings',
};

export function TopBar() {
  const location = useLocation();
  const { isRecording, duration, folder } = useRecordingStore();
  const title = pageTitles[location.pathname] || 'ECHO';

  return (
    <header className="h-14 bg-slate-800 border-b border-slate-700 flex items-center justify-between px-6">
      {/* Left: Page title */}
      <div className="flex items-center gap-4">
        <h1 className="text-lg font-semibold text-white">{title}</h1>

        {/* Recording indicator */}
        {isRecording && (
          <div className="flex items-center gap-2 px-3 py-1 bg-red-500/20 rounded-full">
            <div className="w-2 h-2 bg-red-500 rounded-full recording-indicator" />
            <span className="text-red-400 text-sm font-medium">
              {formatDuration(duration)}
            </span>
          </div>
        )}
      </div>

      {/* Right: Status info */}
      <div className="flex items-center gap-4 text-sm text-slate-400">
        {/* Current folder */}
        <div className="flex items-center gap-2">
          <Folder className="w-4 h-4" />
          <span>{folder === 'notes-perso' ? 'Notes perso' : 'Meetings'}</span>
        </div>
      </div>
    </header>
  );
}
