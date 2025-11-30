# ECHO - Voice Recording & Transcription

**ECHO** is a voice recording and transcription application for the AXIOM platform.

## Features

- **Microphone Recording**: Capture audio from your microphone
- **System Audio Capture**: Record system audio using WASAPI loopback (Windows)
- **GPU Transcription**: Fast, accurate transcription using faster-whisper
- **Bilingual Support**: French Canadian (FR-CA) and English (auto-detect)
- **Desktop App**: Native desktop application with system tray
- **Real-time Transcription**: See transcription as you speak

## Quick Start

### Prerequisites

- Docker with GPU support (NVIDIA Container Toolkit)
- FORGE infrastructure running
- Node.js 20+ (for frontend development)
- Rust toolchain (for Tauri development)

### Start with Docker

```powershell
# 1. Start FORGE (if not running)
cd D:\Projects\AXIOM\forge
docker-compose up -d

# 2. Start ECHO
cd D:\Projects\AXIOM\apps\echo
docker-compose -f docker-compose.dev.yml up -d
```

### Access

- **Frontend**: http://localhost:7200
- **API Docs**: http://localhost:7201/docs

## Architecture

```
ECHO
├── Backend (FastAPI + Python)
│   ├── Recording management
│   ├── Transcription service (faster-whisper)
│   └── WebSocket real-time
├── Frontend (React 19 + Vite)
│   ├── Recording UI
│   ├── Library browser
│   └── Settings
└── Desktop (Tauri + Rust)
    ├── WASAPI loopback capture
    ├── System tray
    └── Global hotkeys
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `WHISPER_MODEL` | large-v3 | Whisper model size |
| `WHISPER_DEVICE` | cuda | GPU (cuda) or CPU |
| `DEFAULT_LANGUAGE` | auto | auto, fr, en |
| `AUDIO_STORAGE_PATH` | /app/data | Audio file storage |

## Development

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Desktop App

```bash
cd tauri
npm run tauri dev
```

## API Reference

### Recordings

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/v1/recordings | List all recordings |
| POST | /api/v1/recordings | Create recording |
| GET | /api/v1/recordings/{id} | Get recording |
| DELETE | /api/v1/recordings/{id} | Delete recording |
| POST | /api/v1/recordings/{id}/transcribe | Transcribe |

### Transcriptions

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/v1/transcriptions/{id} | Get transcription |
| PATCH | /api/v1/transcriptions/{id} | Edit transcription |
| POST | /api/v1/transcriptions/{id}/export | Export (SRT, TXT) |

## File Organization

Audio files are organized in two folders:
- `notes-perso/` - Personal notes
- `meetings/` - Meeting recordings

Files are named with timestamp: `2025-01-29_meeting-standup.wav`

## License

Part of the AXIOM platform.

---

**Version**: 0.1.0
**Status**: MVP Development
