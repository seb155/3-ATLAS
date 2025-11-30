/**
 * TranscriptDetailPage
 *
 * Displays the full transcript of a recording with:
 * - Audio playback controls
 * - Transcription segments with timestamps
 * - Export options (TXT, SRT)
 */

import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { ArrowLeft, Play, Pause, Download, FileText, Clock, Loader2 } from 'lucide-react';
import { useState, useRef, useEffect } from 'react';
import { recordingsApi, transcriptionsApi, api } from '@/services/api';
import { TranscriptionSegmentList, TranscriptionSegmentData } from '@/components/transcription/TranscriptionSegment';
import { cn, formatDuration } from '@/lib/utils';

export function TranscriptDetailPage() {
  const { recordingId } = useParams<{ recordingId: string }>();
  const navigate = useNavigate();
  const audioRef = useRef<HTMLAudioElement>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);

  // Fetch recording
  const { data: recording, isLoading: recordingLoading } = useQuery({
    queryKey: ['recording', recordingId],
    queryFn: () => recordingsApi.get(recordingId!),
    enabled: !!recordingId,
  });

  // Fetch transcription by recording ID
  const { data: transcription, isLoading: transcriptionLoading } = useQuery({
    queryKey: ['transcription', recordingId],
    queryFn: async () => {
      const { data } = await api.get(`/recordings/${recordingId}/transcription`);
      return data;
    },
    enabled: !!recordingId,
  });

  // Audio time update
  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;

    const handleTimeUpdate = () => setCurrentTime(audio.currentTime);
    const handlePlay = () => setIsPlaying(true);
    const handlePause = () => setIsPlaying(false);
    const handleEnded = () => {
      setIsPlaying(false);
      setCurrentTime(0);
    };

    audio.addEventListener('timeupdate', handleTimeUpdate);
    audio.addEventListener('play', handlePlay);
    audio.addEventListener('pause', handlePause);
    audio.addEventListener('ended', handleEnded);

    return () => {
      audio.removeEventListener('timeupdate', handleTimeUpdate);
      audio.removeEventListener('play', handlePlay);
      audio.removeEventListener('pause', handlePause);
      audio.removeEventListener('ended', handleEnded);
    };
  }, []);

  const togglePlayPause = () => {
    const audio = audioRef.current;
    if (!audio) return;

    if (isPlaying) {
      audio.pause();
    } else {
      audio.play();
    }
  };

  const handleSeek = (time: number) => {
    const audio = audioRef.current;
    if (audio) {
      audio.currentTime = time;
      if (!isPlaying) {
        audio.play();
      }
    }
  };

  const handleExport = async (format: 'txt' | 'srt') => {
    if (!transcription?.id) return;

    try {
      const result = await transcriptionsApi.export(transcription.id, format);
      // Create and download file
      const blob = new Blob([result.content], { type: 'text/plain' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${recording?.title || 'transcript'}.${format}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Export failed:', err);
    }
  };

  // Parse segments from transcription (if available)
  const segments: TranscriptionSegmentData[] = transcription?.segments || [];

  // If no segments, create a single segment from full text
  const displaySegments: TranscriptionSegmentData[] = segments.length > 0
    ? segments
    : transcription?.full_text
      ? [{
          id: 'full',
          start_time: 0,
          end_time: recording?.duration_seconds || 0,
          text: transcription.full_text,
          language_detected: transcription.detected_language,
        }]
      : [];

  const isLoading = recordingLoading || transcriptionLoading;

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <Loader2 className="w-8 h-8 text-echo-500 animate-spin" />
      </div>
    );
  }

  if (!recording) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-slate-400">
        <FileText className="w-12 h-12 mb-4" />
        <p>Recording not found</p>
        <button
          onClick={() => navigate('/library')}
          className="mt-4 text-echo-500 hover:text-echo-400"
        >
          Back to library
        </button>
      </div>
    );
  }

  const audioUrl = recording.file_path
    ? `${import.meta.env.VITE_API_URL || 'http://localhost:7201'}/api/v1/recordings/${recording.id}/download`
    : null;

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center gap-4 mb-6">
        <button
          onClick={() => navigate('/library')}
          className="p-2 rounded-lg hover:bg-slate-700 transition-smooth"
        >
          <ArrowLeft className="w-5 h-5 text-slate-400" />
        </button>
        <div className="flex-1">
          <h1 className="text-xl font-semibold text-white">
            {recording.title || recording.filename}
          </h1>
          <div className="flex items-center gap-4 text-sm text-slate-400 mt-1">
            <span className="flex items-center gap-1">
              <Clock className="w-3 h-3" />
              {formatDuration(recording.duration_seconds)}
            </span>
            {transcription?.word_count && (
              <span>{transcription.word_count} words</span>
            )}
            {transcription?.detected_language && (
              <span className="capitalize">{transcription.detected_language}</span>
            )}
          </div>
        </div>
      </div>

      {/* Audio Player */}
      {audioUrl && (
        <div className="glass rounded-lg p-4 mb-6">
          <div className="flex items-center gap-4">
            <button
              onClick={togglePlayPause}
              className={cn(
                'w-12 h-12 rounded-full flex items-center justify-center transition-smooth',
                'bg-echo-500 hover:bg-echo-600'
              )}
            >
              {isPlaying ? (
                <Pause className="w-5 h-5 text-white" />
              ) : (
                <Play className="w-5 h-5 text-white ml-0.5" />
              )}
            </button>

            {/* Progress bar */}
            <div className="flex-1">
              <div className="relative h-2 bg-slate-700 rounded-full overflow-hidden">
                <div
                  className="absolute h-full bg-echo-500 transition-all duration-100"
                  style={{
                    width: `${(currentTime / (recording.duration_seconds || 1)) * 100}%`,
                  }}
                />
              </div>
              <div className="flex justify-between text-xs text-slate-400 mt-1">
                <span>{formatDuration(currentTime)}</span>
                <span>{formatDuration(recording.duration_seconds)}</span>
              </div>
            </div>
          </div>

          <audio ref={audioRef} src={audioUrl} preload="metadata" />
        </div>
      )}

      {/* Export buttons */}
      <div className="flex gap-2 mb-6">
        <button
          onClick={() => handleExport('txt')}
          className={cn(
            'flex items-center gap-2 px-4 py-2 rounded-lg transition-smooth',
            'bg-slate-800 text-slate-300 hover:bg-slate-700'
          )}
        >
          <Download className="w-4 h-4" />
          Export TXT
        </button>
        <button
          onClick={() => handleExport('srt')}
          className={cn(
            'flex items-center gap-2 px-4 py-2 rounded-lg transition-smooth',
            'bg-slate-800 text-slate-300 hover:bg-slate-700'
          )}
        >
          <Download className="w-4 h-4" />
          Export SRT
        </button>
      </div>

      {/* Transcription */}
      <div className="flex-1 overflow-y-auto">
        {!transcription ? (
          <div className="flex flex-col items-center justify-center h-64 text-slate-400">
            <FileText className="w-12 h-12 mb-4" />
            <p>No transcription available</p>
            {recording.status !== 'transcribed' && (
              <p className="text-sm mt-2">
                Status: <span className="capitalize">{recording.status}</span>
              </p>
            )}
          </div>
        ) : displaySegments.length > 0 ? (
          <TranscriptionSegmentList
            segments={displaySegments}
            onSeek={handleSeek}
            currentTime={currentTime}
            showLanguageBadges={true}
          />
        ) : (
          <div className="glass rounded-lg p-6">
            <p className="text-slate-300 whitespace-pre-wrap leading-relaxed">
              {transcription.full_text || 'Empty transcription'}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

export default TranscriptDetailPage;
