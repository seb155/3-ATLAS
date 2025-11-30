# -*- coding: utf-8 -*-
"""
ECHO - Record and Transcribe Test Script
Records audio from microphone and transcribes using faster-whisper (CPU) or Whisper NPU

Usage:
    python record-and-transcribe.py [--duration 10] [--device cpu|npu]
"""

import os
import sys
import io
import time
import wave
import tempfile
import argparse
from pathlib import Path

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Check and install dependencies
def check_dependencies():
    missing = []
    try:
        import sounddevice
    except ImportError:
        missing.append("sounddevice")
    try:
        import numpy
    except ImportError:
        missing.append("numpy")
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        missing.append("faster-whisper")

    if missing:
        print(f"Missing dependencies: {', '.join(missing)}")
        print("Installing...")
        import subprocess
        for pkg in missing:
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])
        print("Dependencies installed. Please run the script again.")
        sys.exit(0)

check_dependencies()

import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel

def list_audio_devices():
    """List available audio input devices"""
    print("\n=== Available Audio Devices ===")
    devices = sd.query_devices()
    for i, device in enumerate(devices):
        if device['max_input_channels'] > 0:
            print(f"  [{i}] {device['name']} (inputs: {device['max_input_channels']})")
    print()

def record_audio(duration: int = 10, sample_rate: int = 16000) -> np.ndarray:
    """Record audio from default microphone"""
    print(f"\n[MIC] Recording for {duration} seconds...")
    print("      Speak now!")
    print()

    # Start recording
    audio_data = sd.rec(
        int(duration * sample_rate),
        samplerate=sample_rate,
        channels=1,
        dtype=np.float32
    )

    # Progress bar
    for i in range(duration):
        remaining = duration - i
        bar = "#" * (i + 1) + "-" * remaining
        print(f"\r      [{bar}] {remaining}s remaining", end="", flush=True)
        time.sleep(1)

    sd.wait()
    print(f"\r      Recording complete!{' ' * 30}")

    return audio_data.flatten()

def save_wav(audio_data: np.ndarray, filepath: str, sample_rate: int = 16000):
    """Save audio data to WAV file"""
    # Convert float32 to int16
    audio_int16 = (audio_data * 32767).astype(np.int16)

    with wave.open(filepath, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(sample_rate)
        wf.writeframes(audio_int16.tobytes())

    print(f"      Saved to: {filepath}")

def transcribe_cpu(audio_path: str, model_size: str = "base") -> dict:
    """Transcribe using faster-whisper on CPU"""
    print(f"\n[LOAD] Loading Whisper model '{model_size}' (CPU)...")
    start_load = time.time()

    model = WhisperModel(
        model_size,
        device="cpu",
        compute_type="int8"
    )

    load_time = time.time() - start_load
    print(f"       Model loaded in {load_time:.2f}s")

    print("\n[TRANSCRIBE] Processing audio...")
    start_transcribe = time.time()

    segments, info = model.transcribe(
        audio_path,
        language=None,  # Auto-detect
        beam_size=5,
        vad_filter=False,  # Disabled to capture all audio
        word_timestamps=True
    )

    # Collect all segments
    full_text = ""
    all_segments = []
    for segment in segments:
        full_text += segment.text
        all_segments.append({
            "start": segment.start,
            "end": segment.end,
            "text": segment.text
        })

    transcribe_time = time.time() - start_transcribe

    return {
        "text": full_text.strip(),
        "language": info.language,
        "language_probability": info.language_probability,
        "duration": info.duration,
        "segments": all_segments,
        "transcribe_time": transcribe_time,
        "load_time": load_time,
        "device": "CPU"
    }

def main():
    parser = argparse.ArgumentParser(description="Record and transcribe audio")
    parser.add_argument("--duration", type=int, default=10, help="Recording duration in seconds")
    parser.add_argument("--device", choices=["cpu", "npu"], default="cpu", help="Transcription device")
    parser.add_argument("--model", default="base", help="Whisper model size (tiny, base, small, medium, large-v3)")
    parser.add_argument("--list-devices", action="store_true", help="List audio devices and exit")
    args = parser.parse_args()

    print("=" * 60)
    print("ECHO - Record and Transcribe Test")
    print("=" * 60)

    if args.list_devices:
        list_audio_devices()
        return

    # Show audio devices
    list_audio_devices()

    # Record audio
    audio_data = record_audio(duration=args.duration)

    # Save to temp file
    temp_dir = Path(tempfile.gettempdir())
    audio_path = temp_dir / f"echo_test_{int(time.time())}.wav"
    save_wav(audio_data, str(audio_path))

    # Transcribe
    if args.device == "cpu":
        result = transcribe_cpu(str(audio_path), model_size=args.model)
    else:
        print("\n[WARN] NPU transcription not yet implemented")
        print("       Using CPU fallback...")
        result = transcribe_cpu(str(audio_path), model_size=args.model)

    # Display results
    print("\n" + "=" * 60)
    print("TRANSCRIPTION RESULTS")
    print("=" * 60)
    print(f"\n[LANG] Language: {result['language']} ({result['language_probability']:.1%} confidence)")
    print(f"[TIME] Audio duration: {result['duration']:.2f}s")
    print(f"[DEV]  Device: {result['device']}")
    print(f"[PERF] Transcription time: {result['transcribe_time']:.2f}s")
    print(f"[SPEED] {result['duration']/result['transcribe_time']:.1f}x real-time")

    print("\n[TEXT] Transcription:")
    print("-" * 60)
    print(result['text'] if result['text'] else "(No speech detected)")
    print("-" * 60)

    if result['segments']:
        print("\n[SEGMENTS]")
        for seg in result['segments'][:5]:  # Show first 5 segments
            print(f"   [{seg['start']:.1f}s - {seg['end']:.1f}s] {seg['text']}")
        if len(result['segments']) > 5:
            print(f"   ... and {len(result['segments']) - 5} more segments")

    # Cleanup info
    print(f"\n[FILE] Audio saved: {audio_path}")

    print("\n" + "=" * 60)
    print("[OK] Test complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()
