import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Folder, Search, Play, FileText, Trash2, Clock, HardDrive } from 'lucide-react';
import { recordingsApi, Recording } from '@/services/api';
import { cn, formatDuration, formatFileSize, formatDate } from '@/lib/utils';

type FolderFilter = 'all' | 'notes-perso' | 'meetings';

export function LibraryPage() {
  const [folder, setFolder] = useState<FolderFilter>('all');
  const [search, setSearch] = useState('');

  const { data, isLoading, error } = useQuery({
    queryKey: ['recordings', folder, search],
    queryFn: () =>
      recordingsApi.list({
        folder: folder === 'all' ? undefined : folder,
        page: 1,
        page_size: 50,
      }),
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-semibold text-white">Recordings</h2>
        <div className="text-sm text-slate-400">
          {data?.total || 0} recordings
        </div>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-4">
        {/* Search */}
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search recordings..."
            className={cn(
              'w-full pl-10 pr-4 py-2 bg-slate-800 border border-slate-700 rounded-lg',
              'text-white placeholder-slate-500',
              'focus:outline-none focus:border-echo-500'
            )}
          />
        </div>

        {/* Folder Filter */}
        <div className="flex gap-2">
          <FolderButton
            label="All"
            active={folder === 'all'}
            onClick={() => setFolder('all')}
          />
          <FolderButton
            label="Notes perso"
            active={folder === 'notes-perso'}
            onClick={() => setFolder('notes-perso')}
          />
          <FolderButton
            label="Meetings"
            active={folder === 'meetings'}
            onClick={() => setFolder('meetings')}
          />
        </div>
      </div>

      {/* Recording List */}
      {isLoading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin w-8 h-8 border-2 border-echo-500 border-t-transparent rounded-full" />
        </div>
      ) : error ? (
        <div className="flex items-center justify-center h-64 text-red-400">
          Failed to load recordings
        </div>
      ) : data?.items.length === 0 ? (
        <div className="flex flex-col items-center justify-center h-64 text-slate-400">
          <Folder className="w-12 h-12 mb-4" />
          <p>No recordings yet</p>
          <p className="text-sm">Start recording to see your files here</p>
        </div>
      ) : (
        <div className="space-y-2">
          {data?.items.map((recording) => (
            <RecordingCard key={recording.id} recording={recording} />
          ))}
        </div>
      )}
    </div>
  );
}

interface FolderButtonProps {
  label: string;
  active: boolean;
  onClick: () => void;
}

function FolderButton({ label, active, onClick }: FolderButtonProps) {
  return (
    <button
      onClick={onClick}
      className={cn(
        'px-4 py-2 rounded-lg text-sm transition-smooth',
        active
          ? 'bg-echo-500 text-white'
          : 'bg-slate-800 text-slate-400 hover:bg-slate-700'
      )}
    >
      {label}
    </button>
  );
}

interface RecordingCardProps {
  recording: Recording;
}

function RecordingCard({ recording }: RecordingCardProps) {
  const statusColors: Record<string, string> = {
    recording: 'bg-red-500',
    completed: 'bg-green-500',
    transcribing: 'bg-yellow-500',
    transcribed: 'bg-echo-500',
    error: 'bg-red-500',
  };

  return (
    <div className="glass rounded-lg p-4 hover:bg-slate-700/50 transition-smooth">
      <div className="flex items-center gap-4">
        {/* Play Button */}
        <button className="w-10 h-10 rounded-full bg-echo-500 hover:bg-echo-600 flex items-center justify-center transition-smooth">
          <Play className="w-5 h-5 text-white ml-0.5" />
        </button>

        {/* Info */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <h3 className="font-medium text-white truncate">
              {recording.title || recording.filename}
            </h3>
            <div
              className={cn(
                'w-2 h-2 rounded-full',
                statusColors[recording.status] || 'bg-slate-500'
              )}
              title={recording.status}
            />
          </div>
          <div className="flex items-center gap-4 text-sm text-slate-400 mt-1">
            <span className="flex items-center gap-1">
              <Clock className="w-3 h-3" />
              {formatDuration(recording.duration_seconds)}
            </span>
            <span className="flex items-center gap-1">
              <HardDrive className="w-3 h-3" />
              {formatFileSize(recording.file_size_bytes)}
            </span>
            <span className="flex items-center gap-1">
              <Folder className="w-3 h-3" />
              {recording.folder === 'notes-perso' ? 'Notes' : 'Meetings'}
            </span>
          </div>
        </div>

        {/* Date */}
        <div className="text-sm text-slate-400">
          {formatDate(recording.recorded_at)}
        </div>

        {/* Actions */}
        <div className="flex items-center gap-2">
          {recording.status === 'transcribed' && (
            <button
              className="p-2 rounded-lg hover:bg-slate-600 transition-smooth"
              title="View transcription"
            >
              <FileText className="w-4 h-4 text-slate-400" />
            </button>
          )}
          <button
            className="p-2 rounded-lg hover:bg-red-500/20 transition-smooth"
            title="Delete"
          >
            <Trash2 className="w-4 h-4 text-slate-400 hover:text-red-400" />
          </button>
        </div>
      </div>
    </div>
  );
}
