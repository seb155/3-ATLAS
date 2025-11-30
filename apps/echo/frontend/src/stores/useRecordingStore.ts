import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export type AudioSource = 'microphone' | 'system' | 'both';
export type Folder = 'notes-perso' | 'meetings';
export type Language = 'auto' | 'fr' | 'en';

interface RecordingState {
  // Recording state
  isRecording: boolean;
  isPaused: boolean;
  currentRecordingId: string | null;
  duration: number;

  // Settings
  source: AudioSource;
  folder: Folder;
  language: Language;
  title: string;

  // Actions
  setSource: (source: AudioSource) => void;
  setFolder: (folder: Folder) => void;
  setLanguage: (language: Language) => void;
  setTitle: (title: string) => void;
  startRecording: (recordingId: string) => void;
  stopRecording: () => void;
  pauseRecording: () => void;
  resumeRecording: () => void;
  updateDuration: (duration: number) => void;
  reset: () => void;
}

const initialState = {
  isRecording: false,
  isPaused: false,
  currentRecordingId: null,
  duration: 0,
  source: 'microphone' as AudioSource,
  folder: 'notes-perso' as Folder,
  language: 'auto' as Language,
  title: '',
};

export const useRecordingStore = create<RecordingState>()(
  persist(
    (set) => ({
      ...initialState,

      setSource: (source) => set({ source }),
      setFolder: (folder) => set({ folder }),
      setLanguage: (language) => set({ language }),
      setTitle: (title) => set({ title }),

      startRecording: (recordingId) =>
        set({
          isRecording: true,
          isPaused: false,
          currentRecordingId: recordingId,
          duration: 0,
        }),

      stopRecording: () =>
        set({
          isRecording: false,
          isPaused: false,
          currentRecordingId: null,
          duration: 0,
          title: '',
        }),

      pauseRecording: () => set({ isPaused: true }),
      resumeRecording: () => set({ isPaused: false }),
      updateDuration: (duration) => set({ duration }),

      reset: () => set(initialState),
    }),
    {
      name: 'echo-recording',
      partialize: (state) => ({
        source: state.source,
        folder: state.folder,
        language: state.language,
      }),
    }
  )
);
