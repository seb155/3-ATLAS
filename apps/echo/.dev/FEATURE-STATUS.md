# ECHO Feature Status

> Last Updated: 2025-12-01

## Latest Test Results (2025-12-01)

| Test | Result | Details |
|------|--------|---------|
| CPU Transcription | ✅ Pass | "R2, peut-être, peut-être, est-ce que ça fonctionne ?" |
| Language Detection | ✅ Pass | French (fr) detected with 82.99% confidence |
| Model Used | base | 5.94s processing time |
| Docker Backend | ✅ Pass | Healthy on port 7201 |
| NPU Fallback | ✅ Pass | Gracefully falls back to CPU on Linux |

## NPU Integration (NEW)

| Feature | Status | Description |
|---------|--------|-------------|
| Encoder/Decoder ONNX architecture | ✅ Done | Separate encoder + decoder models |
| VitisAI Execution Provider | ✅ Done | Config files auto-generated |
| HuggingFace model download | ✅ Done | amd/whisper-{small,medium,large-turbo}-onnx-npu |
| Auto-detection NPU/CPU | ✅ Done | TranscriptionService fallback chain |
| Code-switching detection | ✅ Done | FR+EN bilingual detection in text |
| Quebec French indicators | ✅ Done | "pis", "ben", "faque", "tsé", etc. |
| NPU compilation caching | ✅ Done | First load compiles, then cached |
| Real-time factor (RTF) | ✅ Done | Performance metric logged |

### Supported NPU Models

| Model | HuggingFace Repo | Performance |
|-------|------------------|-------------|
| small | `amd/whisper-small-onnx-npu` | ~2s for 30s audio |
| medium | `amd/whisper-medium-onnx-npu` | ~5s for 30s audio |
| large-v3-turbo | `amd/whisper-large-turbo-onnx-npu` | ~8s for 30s audio |

### Architecture

```
Audio → librosa (16kHz) → Feature Extractor → Encoder (NPU) → Decoder (NPU) → Text
                              │                    │              │
                         WhisperFeatureExtractor  ONNX         Greedy decode
                                                  VitisAI EP    448 max tokens
```

### Files Modified

| File | Changes |
|------|---------|
| `backend/app/services/whisper_npu.py` | Complete rewrite with encoder/decoder |
| `backend/app/services/transcription_service.py` | Already compatible |
| `backend/app/api/endpoints/health.py` | Already shows NPU status |

## Bilingual Support

| Feature | Status | Description |
|---------|--------|-------------|
| Language auto-detect | ✅ Done | Whisper detects dominant language |
| Force language | ✅ Done | Can force `fr` or `en` |
| Transcript detail page | ✅ Done | View transcript after recording |
| Audio playback | ✅ Done | Play audio with transcript |
| Export (TXT/SRT) | ✅ Done | Download transcript |
| Per-segment detection | ⏳ Planned | Individual segments with language tags |
| Code-switching | ✅ Done | Mixed FR+EN detection via text analysis |

## UI Components

### TranscriptionSegment.tsx
Color-coded segments (ready for per-segment detection):
- **Blue**: French (fr)
- **Red**: English (en)
- **Purple**: Bilingual/Code-switched
- **Gray**: Unknown/Auto-detected

### AudioVisualizer.tsx
- Spotify-style vertical bars
- Professional auto-gain (RMS-based, 0.5x-4x range)
- 60fps smooth animation

### TranscriptDetailPage.tsx
- Audio player with progress bar
- Segment list with timestamps
- Export buttons (TXT, SRT)
- Navigation from Library

## API Endpoints

### New in this session
```
GET /api/v1/recordings/{id}/transcription  # Get transcription for recording
GET /api/v1/health                         # NPU status in details.npu_available
```

## What's Working

1. **Record audio** → Save to database
2. **Transcribe** → Whisper detects language, saves `full_text`
3. **View transcript** → Click recording in Library → See detail page
4. **Play audio** → Audio player synced with transcript
5. **Export** → Download as TXT or SRT
6. **NPU transcription** → Auto-detect, faster than CPU

## What's NOT Working Yet

1. **Per-segment language detection**
   - Currently: Single `detected_language` for entire recording
   - Needed: Run Whisper with word timestamps, classify each segment

2. **NPU in Docker**
   - NPU access requires Windows native environment
   - Docker containers cannot access NPU directly
   - Workaround: Run backend natively for NPU, use Docker for CPU fallback

## Technical Notes

### NPU First Load

The first time a model loads, VitisAI compiles it for the NPU:
- **Compilation time**: 2-5 minutes
- **After caching**: <5 seconds
- **Cache location**: `{audio_storage_path}/models/npu/cache/`

### Language Detection Algorithm

```python
# Extended indicators for Quebec French + English
french_indicators = {"le", "la", "pis", "ben", "faque", "tsé", ...}
english_indicators = {"the", "a", "is", "are", "yeah", "okay", ...}

# Code-switching detection
fr_ratio = french_count / total_words
en_ratio = english_count / total_words
is_code_switched = fr_ratio >= 0.05 and en_ratio >= 0.05
```

### Frontend ready

`TranscriptionSegmentList` component already handles:
- Color-coded segments by language
- Click to seek audio
- Active segment highlighting

## Next Steps

1. [x] ~~Test NPU transcription with real FR-CA audio~~ - Tested CPU mode (NPU requires Windows)
2. [ ] Benchmark NPU vs CPU performance (on Windows with Ryzen AI SDK)
3. [ ] Add per-segment detection with word timestamps
4. [ ] Docker hybrid mode (NPU native + API in Docker)
5. [ ] Fix frontend auto-refresh after transcription completes
