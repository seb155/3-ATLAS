import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Mic, Square, Pause, Play, Monitor, Volume2, Loader2, FileText } from 'lucide-react';
import { useRecordingStore, Folder, Language } from '@/stores/useRecordingStore';
import { audioApi, recordingsApi } from '@/services/api';
import { cn, formatDuration } from '@/lib/utils';
import { useAudioRecorder } from '@/hooks/useAudioRecorder';
import { AudioVisualizer } from '@/components/AudioVisualizer';

type RecordingPhase = 'idle' | 'recording' | 'uploading' | 'transcribing' | 'done' | 'error';

export function RecordPage() {
  const navigate = useNavigate();
  const {
    source,
    folder,
    language,
    title,
    currentRecordingId,
    setSource,
    setFolder,
    setLanguage,
    setTitle,
    startRecording: storeStartRecording,
    stopRecording: storeStopRecording,
  } = useRecordingStore();

  const [phase, setPhase] = useState<RecordingPhase>('idle');
  const [error, setError] = useState<string | null>(null);
  const [statusMessage, setStatusMessage] = useState<string>('');
  const [completedRecordingId, setCompletedRecordingId] = useState<string | null>(null);

  // Use the audio recorder hook
  const {
    isRecording,
    isPaused,
    audioBlob,
    error: recorderError,
    duration,
    startRecording: recorderStart,
    stopRecording: recorderStop,
    pauseRecording: recorderPause,
    resumeRecording: recorderResume,
    getWaveformData,
    clearRecording,
  } = useAudioRecorder();

  // Handle recorder errors
  useEffect(() => {
    if (recorderError) {
      setError(recorderError);
      setPhase('error');
    }
  }, [recorderError]);

  // Handle audio blob ready (after recording stops)
  useEffect(() => {
    if (audioBlob && currentRecordingId && phase === 'recording') {
      handleUploadAndTranscribe();
    }
  }, [audioBlob, currentRecordingId, phase]);

  const handleStartRecording = useCallback(async () => {
    setError(null);
    setPhase('idle');

    try {
      // Create recording entry in backend
      const response = await audioApi.start({
        title: title || undefined,
        folder,
        source_type: source,
        language,
      });

      storeStartRecording(response.recording_id);
      setPhase('recording');

      // Start actual audio recording
      await recorderStart();
    } catch (err) {
      setError('Failed to start recording');
      setPhase('error');
      console.error(err);
    }
  }, [title, folder, source, language, storeStartRecording, recorderStart]);

  const handleStopRecording = useCallback(() => {
    // Stop the audio recorder (this will trigger audioBlob to be set)
    recorderStop();
  }, [recorderStop]);

  const handleUploadAndTranscribe = useCallback(async () => {
    if (!audioBlob || !currentRecordingId) return;

    try {
      // Phase 1: Upload audio
      setPhase('uploading');
      setStatusMessage('Uploading audio...');

      await audioApi.upload(currentRecordingId, audioBlob);

      // Note: audioApi.stop() removed - upload() already sets status to COMPLETED
      // and reads WAV metadata (duration, sample_rate, channels)

      // Phase 2: Start transcription
      setPhase('transcribing');
      setStatusMessage('Transcribing audio...');

      await recordingsApi.transcribe(currentRecordingId, language);

      // Done!
      setPhase('done');
      setStatusMessage('Transcription complete!');
      setCompletedRecordingId(currentRecordingId);

    } catch (err) {
      console.error('Upload/transcription failed:', err);
      setError('Failed to process recording');
      setPhase('error');
    }
  }, [audioBlob, currentRecordingId, duration, language, storeStopRecording, clearRecording]);

  const handleReset = useCallback(() => {
    storeStopRecording();
    clearRecording();
    setPhase('idle');
    setError(null);
    setStatusMessage('');
    setCompletedRecordingId(null);
  }, [storeStopRecording, clearRecording]);

  const handleViewTranscript = useCallback(() => {
    if (completedRecordingId) {
      navigate(`/library/${completedRecordingId}`);
    }
  }, [completedRecordingId, navigate]);

  const isDisabled = phase !== 'idle' && phase !== 'recording';

  return (
    <div className="flex flex-col items-center justify-center h-full max-w-2xl mx-auto p-6">
      {/* Title Input */}
      <div className="w-full mb-8">
        <input
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="Recording title (optional)"
          disabled={isRecording || isDisabled}
          className={cn(
            'w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-lg',
            'text-white placeholder-slate-500',
            'focus:outline-none focus:border-echo-500',
            'disabled:opacity-50 disabled:cursor-not-allowed'
          )}
        />
      </div>

      {/* Waveform Visualizer */}
      <div className="w-full h-48 bg-slate-800 rounded-lg mb-8 flex items-center justify-center overflow-hidden">
        {phase === 'idle' && !isRecording ? (
          <span className="text-slate-500">Click record to start</span>
        ) : phase === 'uploading' || phase === 'transcribing' ? (
          <div className="flex items-center gap-3 text-echo-400">
            <Loader2 className="w-6 h-6 animate-spin" />
            <span>{statusMessage}</span>
          </div>
        ) : phase === 'done' ? (
          <div className="flex items-center gap-3 text-green-400">
            <span>{statusMessage}</span>
          </div>
        ) : (
          <AudioVisualizer
            getWaveformData={getWaveformData}
            isActive={isRecording}
            isPaused={isPaused}
            className="w-full h-full"
          />
        )}
      </div>

      {/* Duration Display */}
      <div className="text-4xl font-mono text-white mb-8">
        {formatDuration(duration)}
      </div>

      {/* Main Controls */}
      <div className="flex items-center gap-6 mb-8">
        {phase === 'idle' ? (
          <button
            onClick={handleStartRecording}
            className={cn(
              'w-20 h-20 rounded-full flex items-center justify-center',
              'bg-red-500 hover:bg-red-600 transition-smooth'
            )}
          >
            <Mic className="w-8 h-8 text-white" />
          </button>
        ) : phase === 'recording' ? (
          <>
            {/* Pause/Resume */}
            <button
              onClick={isPaused ? recorderResume : recorderPause}
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
              className={cn(
                'w-20 h-20 rounded-full flex items-center justify-center',
                'bg-red-500 hover:bg-red-600 transition-smooth recording-indicator'
              )}
            >
              <Square className="w-8 h-8 text-white" />
            </button>

            {/* Volume indicator placeholder */}
            <button
              className={cn(
                'w-14 h-14 rounded-full flex items-center justify-center',
                'bg-slate-700 hover:bg-slate-600 transition-smooth'
              )}
            >
              <Volume2 className="w-6 h-6 text-white" />
            </button>
          </>
        ) : phase === 'uploading' || phase === 'transcribing' ? (
          <div className="w-20 h-20 rounded-full flex items-center justify-center bg-slate-700">
            <Loader2 className="w-8 h-8 text-echo-400 animate-spin" />
          </div>
        ) : phase === 'done' ? (
          <>
            {/* View Transcript */}
            <button
              onClick={handleViewTranscript}
              className={cn(
                'flex items-center gap-2 px-6 py-3 rounded-full',
                'bg-echo-500 hover:bg-echo-600 transition-smooth'
              )}
            >
              <FileText className="w-5 h-5 text-white" />
              <span className="text-white font-medium">Voir transcript</span>
            </button>

            {/* New Recording */}
            <button
              onClick={handleReset}
              className={cn(
                'w-14 h-14 rounded-full flex items-center justify-center',
                'bg-slate-700 hover:bg-slate-600 transition-smooth'
              )}
              title="Nouvel enregistrement"
            >
              <Mic className="w-6 h-6 text-white" />
            </button>
          </>
        ) : phase === 'error' ? (
          <button
            onClick={handleReset}
            className={cn(
              'w-20 h-20 rounded-full flex items-center justify-center',
              'bg-red-500 hover:bg-red-600 transition-smooth'
            )}
          >
            <Mic className="w-8 h-8 text-white" />
          </button>
        ) : null}
      </div>

      {/* Source Selection */}
      <div className="flex gap-4 mb-6">
        <SourceButton
          icon={<Mic className="w-5 h-5" />}
          label="Microphone"
          active={source === 'microphone'}
          onClick={() => setSource('microphone')}
          disabled={isRecording || isDisabled}
        />
        <SourceButton
          icon={<Monitor className="w-5 h-5" />}
          label="System Audio"
          active={source === 'system'}
          onClick={() => setSource('system')}
          disabled={true}
          tooltip="Requires desktop app"
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
          disabled={true}
          tooltip="Requires desktop app"
        />
      </div>

      {/* Settings Row */}
      <div className="flex gap-4">
        {/* Folder */}
        <select
          value={folder}
          onChange={(e) => setFolder(e.target.value as Folder)}
          disabled={isRecording || isDisabled}
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
          disabled={isRecording || isDisabled}
          className={cn(
            'px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg',
            'text-white focus:outline-none focus:border-echo-500',
            'disabled:opacity-50 disabled:cursor-not-allowed'
          )}
        >
          <option value="auto">Auto-detect</option>
          <option value="fr">Francais</option>
          <option value="en">English</option>
          <option value="bilingual">Bilingue (FR + EN)</option>
        </select>
      </div>

      {/* Error Message */}
      {error && (
        <div className="mt-4 px-4 py-2 bg-red-500/20 border border-red-500 rounded-lg text-red-400">
          {error}
        </div>
      )}

      {/* Status Message */}
      {statusMessage && phase !== 'done' && !error && (
        <div className="mt-4 px-4 py-2 bg-echo-500/20 border border-echo-500 rounded-lg text-echo-400">
          {statusMessage}
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
  tooltip?: string;
}

function SourceButton({ icon, label, active, onClick, disabled, tooltip }: SourceButtonProps) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      title={tooltip}
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
