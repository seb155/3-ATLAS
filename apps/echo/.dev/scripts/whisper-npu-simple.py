# -*- coding: utf-8 -*-
"""
Simple Whisper NPU Test
Uses ONNX Runtime with VitisAI Execution Provider for AMD NPU
"""
import os
import sys
import io
import time
import argparse
import numpy as np

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Set environment
os.environ['RYZEN_AI_INSTALLATION_PATH'] = r'C:\Program Files\RyzenAI\1.6.1'

def load_audio(path: str, target_sr: int = 16000):
    """Load audio file using soundfile (simpler than torchaudio)"""
    import soundfile as sf
    import librosa

    audio, sr = sf.read(path)

    # Convert to mono if stereo
    if len(audio.shape) > 1:
        audio = audio.mean(axis=1)

    # Resample if needed
    if sr != target_sr:
        audio = librosa.resample(audio, orig_sr=sr, target_sr=target_sr)

    return audio.astype(np.float32)

def check_onnx_providers():
    """Check available ONNX Runtime providers"""
    import onnxruntime as ort
    print("Available ONNX Runtime Providers:")
    for provider in ort.get_available_providers():
        print(f"  - {provider}")
    return ort.get_available_providers()

def transcribe_with_faster_whisper(audio_path: str, model_size: str = "base", device: str = "cpu"):
    """Use faster-whisper for transcription (CPU/CUDA)"""
    from faster_whisper import WhisperModel

    print(f"\n[LOAD] Loading faster-whisper '{model_size}' ({device})...")
    start = time.time()

    model = WhisperModel(
        model_size,
        device=device,
        compute_type="int8" if device == "cpu" else "float16"
    )
    print(f"       Loaded in {time.time() - start:.2f}s")

    print("\n[TRANSCRIBE] Processing...")
    start = time.time()

    segments, info = model.transcribe(
        audio_path,
        beam_size=5,
        vad_filter=False
    )

    text = ""
    for segment in segments:
        text += segment.text

    elapsed = time.time() - start

    return {
        "text": text.strip(),
        "language": info.language,
        "duration": info.duration,
        "elapsed": elapsed,
        "rtf": elapsed / info.duration if info.duration > 0 else 0,
        "device": device
    }

def main():
    parser = argparse.ArgumentParser(description="Whisper NPU Test")
    parser.add_argument("--audio", help="Path to audio file")
    parser.add_argument("--model", default="base", help="Model size (tiny, base, small, medium)")
    parser.add_argument("--device", default="cpu", choices=["cpu", "npu"], help="Device to use")
    parser.add_argument("--check-providers", action="store_true", help="List ONNX providers and exit")
    args = parser.parse_args()

    print("=" * 60)
    print("Whisper Transcription Test")
    print("=" * 60)

    if args.check_providers:
        check_onnx_providers()
        return

    # For now, use faster-whisper on CPU (proven to work)
    # NPU integration requires more setup
    if args.device == "npu":
        print("\n[INFO] NPU mode requires AMD Whisper ONNX models")
        print("       Falling back to CPU with faster-whisper")
        args.device = "cpu"

    result = transcribe_with_faster_whisper(args.audio, args.model, args.device)

    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    print(f"[LANG]   {result['language']}")
    print(f"[AUDIO]  {result['duration']:.2f}s")
    print(f"[TIME]   {result['elapsed']:.2f}s")
    print(f"[RTF]    {result['rtf']:.3f} (lower is better)")
    print(f"[SPEED]  {1/result['rtf']:.1f}x real-time")
    print(f"[DEVICE] {result['device']}")
    print("\n[TEXT]")
    print("-" * 60)
    print(result['text'] if result['text'] else "(No speech detected)")
    print("-" * 60)

if __name__ == "__main__":
    main()
