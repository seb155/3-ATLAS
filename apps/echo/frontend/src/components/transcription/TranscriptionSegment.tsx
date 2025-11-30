/**
 * TranscriptionSegment Component
 *
 * Displays a transcription segment with color-coded language detection.
 * Supports bilingual (French + English) code-switching visualization.
 *
 * Color coding:
 * - Blue: French (fr)
 * - Red: English (en)
 * - Purple: Bilingual/Code-switched (both languages in segment)
 * - Gray: Unknown/Auto-detected
 */

import { cn } from '@/lib/utils';

// Language color mapping
const LANGUAGE_STYLES: Record<string, { bg: string; border: string; text: string; badge: string }> = {
  fr: {
    bg: 'bg-blue-50 dark:bg-blue-900/20',
    border: 'border-blue-300 dark:border-blue-700',
    text: 'text-blue-800 dark:text-blue-200',
    badge: 'bg-blue-500',
  },
  en: {
    bg: 'bg-red-50 dark:bg-red-900/20',
    border: 'border-red-300 dark:border-red-700',
    text: 'text-red-800 dark:text-red-200',
    badge: 'bg-red-500',
  },
  bilingual: {
    bg: 'bg-purple-50 dark:bg-purple-900/20',
    border: 'border-purple-300 dark:border-purple-700',
    text: 'text-purple-800 dark:text-purple-200',
    badge: 'bg-purple-500',
  },
  auto: {
    bg: 'bg-slate-50 dark:bg-slate-800/50',
    border: 'border-slate-300 dark:border-slate-600',
    text: 'text-slate-700 dark:text-slate-300',
    badge: 'bg-slate-500',
  },
};

// Language display names
const LANGUAGE_NAMES: Record<string, string> = {
  fr: 'Francais',
  en: 'English',
  bilingual: 'Bilingue',
  auto: 'Auto',
};

export interface TranscriptionSegmentData {
  id: string;
  start_time: number;
  end_time: number;
  text: string;
  language_detected?: string | null;
  language_confidence?: number | null;
  is_code_switched?: boolean;
  confidence?: number | null;
}

interface TranscriptionSegmentProps {
  segment: TranscriptionSegmentData;
  onSeek?: (time: number) => void;
  showLanguageBadge?: boolean;
  showTimestamp?: boolean;
  isActive?: boolean;
}

export function TranscriptionSegment({
  segment,
  onSeek,
  showLanguageBadge = true,
  showTimestamp = true,
  isActive = false,
}: TranscriptionSegmentProps) {
  const language = segment.language_detected || 'auto';
  const styles = LANGUAGE_STYLES[language] || LANGUAGE_STYLES.auto;
  const languageName = LANGUAGE_NAMES[language] || language;

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div
      className={cn(
        'rounded-lg border p-3 transition-all duration-200',
        styles.bg,
        styles.border,
        isActive && 'ring-2 ring-echo-500 ring-offset-2 dark:ring-offset-slate-900',
        onSeek && 'cursor-pointer hover:shadow-md'
      )}
      onClick={() => onSeek?.(segment.start_time)}
    >
      {/* Header with timestamp and language badge */}
      <div className="flex items-center justify-between mb-2">
        {showTimestamp && (
          <span className="text-xs text-slate-500 dark:text-slate-400 font-mono">
            {formatTime(segment.start_time)} - {formatTime(segment.end_time)}
          </span>
        )}

        {showLanguageBadge && (
          <div className="flex items-center gap-2">
            {segment.is_code_switched && (
              <span className="text-xs text-purple-600 dark:text-purple-400 font-medium">
                Code-switched
              </span>
            )}
            <span
              className={cn(
                'px-2 py-0.5 rounded-full text-xs font-medium text-white',
                styles.badge
              )}
            >
              {languageName}
            </span>
            {segment.language_confidence != null && segment.language_confidence > 0 && (
              <span className="text-xs text-slate-400">
                {Math.round(segment.language_confidence * 100)}%
              </span>
            )}
          </div>
        )}
      </div>

      {/* Segment text */}
      <p className={cn('text-sm leading-relaxed', styles.text)}>
        {segment.text}
      </p>
    </div>
  );
}

// List component for multiple segments
interface TranscriptionSegmentListProps {
  segments: TranscriptionSegmentData[];
  onSeek?: (time: number) => void;
  currentTime?: number;
  showLanguageBadges?: boolean;
}

export function TranscriptionSegmentList({
  segments,
  onSeek,
  currentTime = 0,
  showLanguageBadges = true,
}: TranscriptionSegmentListProps) {
  const getActiveSegmentId = (): string | null => {
    const active = segments.find(
      (seg) => currentTime >= seg.start_time && currentTime < seg.end_time
    );
    return active?.id || null;
  };

  const activeId = getActiveSegmentId();

  if (segments.length === 0) {
    return (
      <div className="text-center py-8 text-slate-400">
        No transcription segments available
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {segments.map((segment) => (
        <TranscriptionSegment
          key={segment.id}
          segment={segment}
          onSeek={onSeek}
          showLanguageBadge={showLanguageBadges}
          isActive={segment.id === activeId}
        />
      ))}
    </div>
  );
}

// Export language utilities for use elsewhere
export { LANGUAGE_STYLES, LANGUAGE_NAMES };
