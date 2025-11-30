# -*- coding: utf-8 -*-
"""Quick mic test - records 3 seconds and shows audio level"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import numpy as np
import sounddevice as sd

print("=== Microphone Test ===\n")

# Show default device
default_input = sd.query_devices(kind='input')
print(f"Default input device: {default_input['name']}")
print(f"Sample rate: {int(default_input['default_samplerate'])} Hz")
print(f"Channels: {default_input['max_input_channels']}")

print("\nRecording 3 seconds... SPEAK NOW!")
audio = sd.rec(int(3 * 16000), samplerate=16000, channels=1, dtype=np.float32)
sd.wait()

# Check audio levels
audio_flat = audio.flatten()
max_level = np.max(np.abs(audio_flat))
rms = np.sqrt(np.mean(audio_flat**2))

print(f"\n=== Audio Analysis ===")
print(f"Max amplitude: {max_level:.4f} (1.0 = max)")
print(f"RMS level: {rms:.6f}")

if max_level < 0.01:
    print("\n[PROBLEM] Audio level very low! Check:")
    print("  - Is the microphone enabled in Windows?")
    print("  - Is the correct input device selected?")
    print("  - Try speaking louder or closer to mic")
elif max_level < 0.1:
    print("\n[WARNING] Audio level is low but might work")
else:
    print("\n[OK] Good audio level detected!")

# Show level bar
bar_len = int(max_level * 50)
print(f"\nLevel: [{'#' * bar_len}{'-' * (50 - bar_len)}] {max_level:.1%}")
