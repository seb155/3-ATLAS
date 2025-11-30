# ECHO Feature Status

> Last Updated: 2025-11-30

## Bilingual Support

| Feature | Status | Description |
|---------|--------|-------------|
| Language auto-detect | ✅ Done | Whisper detects dominant language |
| Force language | ✅ Done | Can force `fr` or `en` |
| Transcript detail page | ✅ Done | View transcript after recording |
| Audio playback | ✅ Done | Play audio with transcript |
| Export (TXT/SRT) | ✅ Done | Download transcript |
| Per-segment detection | ⏳ Planned | Individual segments with language tags |
| Code-switching | ⏳ Planned | Mixed FR+EN detection in same recording |

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
```

## What's Working

1. **Record audio** → Save to database
2. **Transcribe** → Whisper detects language, saves `full_text`
3. **View transcript** → Click recording in Library → See detail page
4. **Play audio** → Audio player synced with transcript
5. **Export** → Download as TXT or SRT

## What's NOT Working Yet

1. **Per-segment language detection**
   - Currently: Single `detected_language` for entire recording
   - Needed: Run Whisper with word timestamps, classify each segment

2. **Code-switching detection**
   - Currently: No segment-level analysis
   - Needed: Language classifier per segment + `is_code_switched` flag

## Technical Notes

### Why segments don't work yet

The `transcription_segments` table schema exists but isn't populated because:

1. Whisper returns segments but we only store `full_text`
2. No language classifier runs on individual segments
3. Frontend expects `segments` array but API returns none

### To implement per-segment detection

```python
# In transcription_service.py
result = model.transcribe(audio, word_timestamps=True)

for segment in result.segments:
    # Detect language per segment
    lang = classify_language(segment.text)

    # Save to transcription_segments table
    db_segment = TranscriptionSegment(
        transcription_id=transcription.id,
        start_time=segment.start,
        end_time=segment.end,
        text=segment.text,
        language_detected=lang,
    )
```

### Frontend ready

`TranscriptionSegmentList` component already handles:
- Color-coded segments by language
- Click to seek audio
- Active segment highlighting
