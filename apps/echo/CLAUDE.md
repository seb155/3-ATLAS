# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**ECHO** - Voice Recording & Transcription Application
**Version:** 0.1.0
**Status:** MVP Development
**Location:** `apps/echo/` in AXIOM monorepo

## Features

- **Audio Recording**: Microphone + System Audio (WASAPI loopback)
- **Transcription**: Hardware auto-detection (NPU > CPU)
- **Languages**: French Canadian (FR-CA) + English (auto-detect)
- **Organization**: Hybrid (folders + metadata DB)
- **Interfaces**: Web + Desktop (Tauri)

## Hardware Acceleration

| Priority | Device | Status | Performance (30s audio) |
|----------|--------|--------|-------------------------|
| 1 | AMD Ryzen AI NPU (XDNA) | Supported | ~5s (medium model) |
| 2 | NVIDIA GPU (CUDA) | Supported | ~3s (large-v3) |
| 3 | CPU (faster-whisper) | Always available | ~5s (base) / ~15s (medium) |

**Note**: AMD Radeon 890M (gfx1150) is NOT supported by ROCm - GPU skipped for this hardware.

## Quick Start

### Development Mode (Docker)

```powershell
# Start FORGE infrastructure first
cd D:\Projects\AXIOM\forge
docker-compose up -d

# Start ECHO
cd D:\Projects\AXIOM\apps\echo
docker-compose -f docker-compose.dev.yml up -d
```

### Access

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:7200 | React UI |
| Backend | http://localhost:7201/docs | FastAPI Swagger |

### Desktop App (Tauri)

```powershell
cd D:\Projects\AXIOM\apps\echo\tauri
npm run tauri dev
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    TAURI DESKTOP APP                        │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Rust Backend (audio_capture.rs)                      │  │
│  │  - WASAPI Loopback (system audio)                     │  │
│  │  - Microphone capture (cpal)                          │  │
│  │  - Audio mixing (both sources)                        │  │
│  └───────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  React Frontend                                       │  │
│  │  - Waveform visualization                             │  │
│  │  - Recording controls                                 │  │
│  │  - Real-time transcription                            │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              PYTHON BACKEND (FastAPI + Docker)              │
│  - faster-whisper (GPU) pour transcription locale           │
│  - PostgreSQL pour metadata                                 │
│  - WebSocket pour real-time transcription                   │
└─────────────────────────────────────────────────────────────┘
```

## Project Structure

```
apps/echo/
├── backend/
│   └── app/
│       ├── main.py                   # FastAPI entry point
│       ├── config.py                 # Settings
│       ├── database.py               # DB connection
│       ├── api/endpoints/
│       │   ├── recordings.py         # Recording CRUD
│       │   ├── transcriptions.py     # Transcription endpoints
│       │   ├── audio.py              # Audio control
│       │   └── health.py             # Health checks
│       ├── models/
│       │   ├── recording.py          # Recording model
│       │   ├── transcription.py      # Transcription models
│       │   └── tag.py                # Tags
│       ├── schemas/                  # Pydantic schemas
│       └── services/
│           ├── whisper_local.py      # faster-whisper
│           └── transcription.py      # Transcription service
├── frontend/
│   └── src/
│       ├── pages/
│       │   ├── RecordPage.tsx        # Main recording UI
│       │   ├── LibraryPage.tsx       # Recording list
│       │   └── SettingsPage.tsx      # Settings
│       ├── components/
│       │   └── layout/               # Layout components
│       ├── stores/
│       │   └── useRecordingStore.ts  # Zustand store
│       └── services/
│           └── api.ts                # API client
├── tauri/
│   └── src-tauri/
│       └── src/
│           ├── main.rs               # Tauri entry
│           ├── audio_capture.rs      # WASAPI/cpal
│           └── tray.rs               # System tray
├── data/
│   ├── notes-perso/                  # Personal notes
│   └── meetings/                     # Meeting recordings
├── docker-compose.dev.yml
└── CLAUDE.md
```

## Development Commands

### Backend

```bash
# Run locally
cd backend
uvicorn app.main:app --reload --port 8000

# Run tests
pytest

# Format
ruff check . --fix
```

### Frontend

```bash
cd frontend
npm install
npm run dev        # Development server
npm run build      # Production build
npm run lint       # Lint check
```

### Tauri

```bash
cd tauri
npm run tauri dev     # Development with hot reload
npm run tauri build   # Build executable
```

## API Endpoints

### Recordings
```
GET    /api/v1/recordings              # List recordings
POST   /api/v1/recordings              # Create recording
GET    /api/v1/recordings/{id}         # Get recording
PATCH  /api/v1/recordings/{id}         # Update recording
DELETE /api/v1/recordings/{id}         # Delete recording
POST   /api/v1/recordings/{id}/transcribe  # Start transcription
GET    /api/v1/recordings/{id}/download    # Download audio
```

### Transcriptions
```
GET    /api/v1/transcriptions/{id}     # Get transcription
PATCH  /api/v1/transcriptions/{id}     # Edit transcription
POST   /api/v1/transcriptions/{id}/export  # Export (SRT, TXT, JSON)
WS     /api/v1/transcriptions/live/{id}    # Real-time WebSocket
```

### Audio Control
```
GET    /api/v1/audio/devices           # List devices
POST   /api/v1/audio/start             # Start recording
POST   /api/v1/audio/stop/{id}         # Stop recording
```

## Configuration

### Environment Variables

```env
# Database
DATABASE_URL=postgresql://postgres:postgres@forge-postgres:5432/echo

# Whisper (Auto-detection: NPU > CPU)
WHISPER_DEVICE=auto           # auto, npu, cpu
WHISPER_MODEL=base            # CPU fallback model
WHISPER_MODEL_NPU=medium      # NPU model (faster with BFP16)
WHISPER_COMPUTE_TYPE=int8     # CPU compute type
WHISPER_PRECISION=bfp16       # NPU native precision

# Audio
AUDIO_STORAGE_PATH=/app/data
DEFAULT_SAMPLE_RATE=44100
DEFAULT_LANGUAGE=auto
```

### NPU Setup (AMD Ryzen AI 300 series)

```powershell
# 1. Verify NPU in Task Manager > Performance > NPU0

# 2. Download Ryzen AI SDK 1.6.1
# https://www.amd.com/en/developer/resources/ryzen-ai-software.html

# 3. Install
.\ryzenai-lt-1.6.1.exe

# 4. Activate environment
conda activate ryzenai-1.6.1

# 5. Verify
python -c "import onnxruntime; print(onnxruntime.get_available_providers())"
```

## Database Schema

### recordings
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| filename | VARCHAR | Audio filename |
| folder | VARCHAR | 'notes-perso' or 'meetings' |
| source_type | VARCHAR | 'microphone', 'system', 'both' |
| duration_seconds | FLOAT | Recording duration |
| status | VARCHAR | 'recording', 'transcribed', etc. |

### transcriptions
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| recording_id | UUID | FK -> recordings |
| full_text | TEXT | Complete transcription |
| language_code | VARCHAR | 'fr-CA', 'en', 'auto' |
| detected_language | VARCHAR | Actual detected language |

### transcription_segments
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| transcription_id | UUID | FK -> transcriptions |
| start_time | FLOAT | Segment start (seconds) |
| end_time | FLOAT | Segment end (seconds) |
| text | TEXT | Segment text |
| words | JSONB | Word-level timing |

## Whisper Configuration

### Auto-Detection Priority
1. **NPU** (AMD Ryzen AI XDNA) - Most efficient
2. **GPU** (NVIDIA CUDA only) - Fastest
3. **CPU** (faster-whisper) - Always available

### Models by Device
| Device | Model | Precision | Notes |
|--------|-------|-----------|-------|
| NPU | medium | BFP16 | Ryzen AI SDK required |
| GPU | large-v3 | float16 | NVIDIA only |
| CPU | base | int8 | Fastest fallback |

### Features
- **VAD**: Enabled (Voice Activity Detection)
- **Word Timestamps**: Enabled
- **Languages**: FR-CA, EN, auto-detect

## Port Allocation

| Service | Port | Internal |
|---------|------|----------|
| Frontend | 7200 | 5173 |
| Backend | 7201 | 8000 |

## Tech Stack

### Backend
- Python 3.11+
- FastAPI 0.109
- SQLAlchemy 2.0
- faster-whisper 1.0
- PostgreSQL 15

### Frontend
- React 19
- TypeScript 5.6
- Vite 6
- Zustand 5
- TanStack Query 5
- Tailwind CSS 4

### Desktop
- Tauri 2
- Rust
- cpal (audio)
- hound (WAV)

## Known Issues

1. **WASAPI Loopback**: Requires native Windows API integration for proper system audio capture. Current cpal implementation is a placeholder.

2. **AMD Radeon 890M (gfx1150)**: NOT supported by ROCm. GPU acceleration skipped for this hardware. Use NPU instead.

3. **First Startup**: Downloads Whisper models on first use:
   - base: ~150MB
   - medium: ~1.5GB
   - large-v3: ~3GB

4. **NPU in Docker**: NPU access from Docker containers requires special configuration. Consider running backend locally for NPU acceleration.

## Next Steps (Phase 2)

- [ ] Complete WASAPI loopback implementation
- [ ] Tags system
- [ ] Full-text search
- [ ] Export functionality
- [ ] Transcription editor
- [ ] Global hotkeys
- [ ] NEXUS integration

---

**Repository:** https://github.com/seb155/AXIOM
**Last Updated:** 2025-11-29
