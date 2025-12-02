import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:7201';

export const api = axios.create({
  baseURL: `${API_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Types
export interface Recording {
  id: string;
  user_id: string;
  filename: string;
  file_path: string;
  folder: string;
  file_size_bytes: number;
  duration_seconds: number;
  sample_rate: number;
  channels: number;
  format: string;
  source_type: string;
  title: string | null;
  description: string | null;
  status: string;
  recorded_at: string;
  created_at: string;
  updated_at: string;
}

export interface RecordingListResponse {
  items: Recording[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

export interface Transcription {
  id: string;
  recording_id: string;
  full_text: string;
  language_code: string;
  detected_language: string | null;
  model_used: string;
  processing_time_seconds: number | null;
  word_count: number;
  status: string;
  error_message: string | null;
  started_at: string | null;
  completed_at: string | null;
  created_at: string;
  updated_at: string;
}

// API Functions
export const recordingsApi = {
  list: async (params?: {
    folder?: string;
    status?: string;
    page?: number;
    page_size?: number;
  }) => {
    const { data } = await api.get<RecordingListResponse>('/recordings', { params });
    return data;
  },

  get: async (id: string) => {
    const { data } = await api.get<Recording>(`/recordings/${id}`);
    return data;
  },

  create: async (recording: {
    title?: string;
    description?: string;
    folder: string;
    source_type: string;
  }) => {
    const { data } = await api.post<Recording>('/recordings', recording);
    return data;
  },

  update: async (id: string, updates: {
    title?: string;
    description?: string;
    folder?: string;
  }) => {
    const { data } = await api.patch<Recording>(`/recordings/${id}`, updates);
    return data;
  },

  delete: async (id: string, permanent = false) => {
    await api.delete(`/recordings/${id}`, { params: { permanent } });
  },

  transcribe: async (id: string, language = 'auto') => {
    const { data } = await api.post(`/recordings/${id}/transcribe`, null, {
      params: { language },
    });
    return data;
  },
};

export const audioApi = {
  start: async (params: {
    title?: string;
    folder: string;
    source_type: string;
    language: string;
  }) => {
    const { data } = await api.post('/audio/start', params);
    return data;
  },

  stop: async (recordingId: string, duration: number, fileSize: number) => {
    const { data } = await api.post(`/audio/stop/${recordingId}`, null, {
      params: { duration_seconds: duration, file_size_bytes: fileSize },
    });
    return data;
  },

  upload: async (recordingId: string, audioBlob: Blob) => {
    const formData = new FormData();
    formData.append('file', audioBlob, 'recording.webm');
    const { data } = await api.post(`/audio/upload/${recordingId}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return data;
  },

  getDevices: async () => {
    const { data } = await api.get('/audio/devices');
    return data;
  },
};

export const transcriptionsApi = {
  get: async (id: string) => {
    const { data } = await api.get<Transcription>(`/transcriptions/${id}`);
    return data;
  },

  getStatus: async (id: string) => {
    const { data } = await api.get(`/transcriptions/${id}/status`);
    return data;
  },

  update: async (id: string, fullText: string) => {
    const { data } = await api.patch<Transcription>(`/transcriptions/${id}`, {
      full_text: fullText,
    });
    return data;
  },

  export: async (id: string, format: 'txt' | 'srt' | 'vtt' | 'json') => {
    const { data } = await api.post(`/transcriptions/${id}/export`, { format });
    return data;
  },
};

export const healthApi = {
  check: async () => {
    const { data } = await api.get('/health');
    return data;
  },
};

// Whisper Settings Types
export interface WhisperModelInfo {
  name: string;
  size: string;
  vram: string;
  speed: string;
  quality: string;
}

export interface DeviceStatus {
  name: string;
  status: 'available' | 'unavailable' | 'error';
  details?: string;
}

export interface WhisperSettings {
  model: string;
  device: string;
  active_device: string;
  model_loaded: boolean;
  available_models: WhisperModelInfo[];
  available_devices: string[];
  device_info: Record<string, DeviceStatus>;
}

export interface WhisperSettingsUpdate {
  model?: string;
  device?: string;
}

export interface WhisperSettingsUpdateResponse {
  success: boolean;
  message: string;
  model: string;
  device: string;
  active_device: string;
  reload_required: boolean;
}

export const settingsApi = {
  getWhisperSettings: async (): Promise<WhisperSettings> => {
    const { data } = await api.get<WhisperSettings>('/settings/whisper');
    return data;
  },

  updateWhisperSettings: async (update: WhisperSettingsUpdate): Promise<WhisperSettingsUpdateResponse> => {
    const { data } = await api.post<WhisperSettingsUpdateResponse>('/settings/whisper', update);
    return data;
  },

  getDevices: async () => {
    const { data } = await api.get('/settings/whisper/devices');
    return data;
  },

  reloadModel: async () => {
    const { data } = await api.post('/settings/whisper/reload');
    return data;
  },
};
