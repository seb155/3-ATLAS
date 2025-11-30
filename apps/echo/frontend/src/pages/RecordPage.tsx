import { useState, useEffect, useRef, useCallback } from 'react';
import { Mic, MicOff, Square, Pause, Play, Monitor, Volume2 } from 'lucide-react';
import { useRecordingStore, AudioSource, Folder, Language } from '@/stores/useRecordingStore';
import { audioApi } from '@/services/api';
import { cn, formatDuration } from '@/lib/utils';

export function RecordPage() {
  const {
    isRecording,
    isPaused,
    duration,
    source,
    folder,
    language,
    title,
    currentRecordingId,
    setSource,
    setFolder,
    setLanguage,
    setTitle,
    startRecording,
    stopRecording,
    pauseRecording,
    resumeRecording,
    updateDuration,
  } = useRecordingStore();

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const timerRef = useRef<number | null>(null);

  // Duration timer
  useEffect(() => {
    if (isRecording && !isPaused) {
      timerRef.current = window.setInterval(() => {
        updateDuration(duration + 1);
      }, 1000);
    }

    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    };
  }, [isRecording, isPaused, duration, updateDuration]);

  const handleStartRecording = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await audioApi.start({
        title: title || undefined,
        folder,
        source_type: source,
        language,
      });

      startRecording(response.recording_id);

      // TODO: Trigger Tauri audio capture
      console.log('Started recording:', response);
    } catch (err) {
      setError('Failed to start recording');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  }, [title, folder, source, language, startRecording]);

  const handleStopRecording = useCallback(async () => {
    if (!currentRecordingId) return;

    setIsLoading(true);
    try {
      await audioApi.stop(currentRecordingId, duration, 0);

      // TODO: Stop Tauri audio capture
      stopRecording();
    } catch (err) {
      setError('Failed to stop recording');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  }, [currentRecordingId, duration, stopRecording]);

  return (
    <div className="flex flex-col items-center justify-center h-full max-w-2xl mx-auto">
      {/* Title Input */}
      <div className="w-full mb-8">
        <input
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="Recording title (optional)"
          disabled={isRecording}
          className={cn(
            'w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-lg',
            'text-white placeholder-slate-500',
            'focus:outline-none focus:border-echo-500',
            'disabled:opacity-50 disabled:cursor-not-allowed'
          )}
        />
      </div>

      {/* Waveform Placeholder */}
      <div className="w-full h-32 bg-slate-800 rounded-lg mb-8 flex items-center justify-center">
        {isRecording ? (
          <div className="flex items-center gap-1">
            {[...Array(20)].map((_, i) => (
              <div
                key={i}
                className="w-1 bg-echo-500 rounded-full animate-pulse"
                style={{
                  height: `${Math.random() * 60 + 20}%`,
                  animationDelay: `${i * 0.1}s`,
                }}
              />
            ))}
          </div>
        ) : (
          <span className="text-slate-500">Waveform will appear here</span>
        )}
      </div>

      {/* Duration Display */}
      <div className="text-4xl font-mono text-white mb-8">
        {formatDuration(duration)}
      </div>

      {/* Main Controls */}
      <div className="flex items-center gap-6 mb-8">
        {!isRecording ? (
          <button
            onClick={handleStartRecording}
            disabled={isLoading}
            className={cn(
              'w-20 h-20 rounded-full flex items-center justify-center',
              'bg-red-500 hover:bg-red-600 transition-smooth',
              'disabled:opacity-50 disabled:cursor-not-allowed'
            )}
          >
            <Mic className="w-8 h-8 text-white" />
          </button>
        ) : (
          <>
            {/* Pause/Resume */}
            <button
              onClick={isPaused ? resumeRecording : pauseRecording}
              className={cn(
                'w-14 h-14 rounded-full flex items-center justify-center',
                'bg-slate-700 hover:bg-slate-600 transition-smooth'
              )}
            >
              {isPaused ? (
                <Play className="w-6 h-6 text-white" />
              ) : (
                <Pause className="w-6 h-6 text-white" />
              )}
            </button>

            {/* Stop */}
            <button
              onClick={handleStopRecording}
              disabled={isLoading}
              className={cn(
                'w-20 h-20 rounded-full flex items-center justify-center',
                'bg-red-500 hover:bg-red-600 transition-smooth recording-indicator',
                'disabled:opacity-50 disabled:cursor-not-allowed'
              )}
            >
              <Square className="w-8 h-8 text-white" />
            </button>

            {/* Mute placeholder */}
            <button
              className={cn(
                'w-14 h-14 rounded-full flex items-center justify-center',
                'bg-slate-700 hover:bg-slate-600 transition-smooth'
              )}
            >
              <Volume2 className="w-6 h-6 text-white" />
            </button>
          </>
        )}
      </div>

      {/* Source Selection */}
      <div className="flex gap-4 mb-6">
        <SourceButton
          icon={<Mic className="w-5 h-5" />}
          label="Microphone"
          active={source === 'microphone'}
          onClick={() => setSource('microphone')}
          disabled={isRecording}
        />
        <SourceButton
          icon={<Monitor className="w-5 h-5" />}
          label="System Audio"
          active={source === 'system'}
          onClick={() => setSource('system')}
          disabled={isRecording}
        />
        <SourceButton
          icon={
            <div className="flex">
              <Mic className="w-4 h-4" />
              <Monitor className="w-4 h-4 -ml-1" />
            </div>
          }
          label="Both"
          active={source === 'both'}
          onClick={() => setSource('both')}
          disabled={isRecording}
        />
      </div>

      {/* Settings Row */}
      <div className="flex gap-4">
        {/* Folder */}
        <select
          value={folder}
          onChange={(e) => setFolder(e.target.value as Folder)}
          disabled={isRecording}
          className={cn(
            'px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg',
            'text-white focus:outline-none focus:border-echo-500',
            'disabled:opacity-50 disabled:cursor-not-allowed'
          )}
        >
          <option value="notes-perso">Notes perso</option>
          <option value="meetings">Meetings</option>
        </select>

        {/* Language */}
        <select
          value={language}
          onChange={(e) => setLanguage(e.target.value as Language)}
          disabled={isRecording}
          className={cn(
            'px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg',
            'text-white focus:outline-none focus:border-echo-500',
            'disabled:opacity-50 disabled:cursor-not-allowed'
          )}
        >
          <option value="auto">Auto-detect</option>
          <option value="fr">Francais</option>
          <option value="en">English</option>
        </select>
      </div>

      {/* Error Message */}
      {error && (
        <div className="mt-4 px-4 py-2 bg-red-500/20 border border-red-500 rounded-lg text-red-400">
          {error}
        </div>
      )}
    </div>
  );
}

interface SourceButtonProps {
  icon: React.ReactNode;
  label: string;
  active: boolean;
  onClick: () => void;
  disabled?: boolean;
}

function SourceButton({ icon, label, active, onClick, disabled }: SourceButtonProps) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={cn(
        'flex items-center gap-2 px-4 py-2 rounded-lg transition-smooth',
        active
          ? 'bg-echo-500 text-white'
          : 'bg-slate-800 text-slate-400 hover:bg-slate-700',
        'disabled:opacity-50 disabled:cursor-not-allowed'
      )}
    >
      {icon}
      <span className="text-sm">{label}</span>
    </button>
  );
}
