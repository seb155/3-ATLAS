# Run Whisper on AMD NPU
# Usage: .\run-whisper-npu.ps1 -Device cpu|npu -Model whisper-small|whisper-medium|whisper-large-v3-turbo -AudioFile path\to\file.wav

param(
    [string]$Device = "npu",
    [string]$Model = "whisper-small",
    [string]$AudioFile = "audio_files\1089-134686-0000.wav"
)

$env:RYZEN_AI_INSTALLATION_PATH = "C:\Program Files\RyzenAI\1.6.1"
$env:Path = "C:\Program Files\RyzenAI\1.6.1\voe-4.0-win_amd64\bin;" + $env:Path
$env:XLNX_VART_FIRMWARE = "C:\Program Files\RyzenAI\1.6.1\voe-4.0-win_amd64\xclbins\phoenix\4x4.xclbin"
$env:XLNX_TARGET_NAME = "AMD_AIE2_Nx4_Overlay"

$pythonPath = "C:\Users\sgagn\miniforge3\envs\ryzen-ai-1.6.1\python.exe"
$whisperDir = "D:\Projects\AXIOM\apps\echo\models\RyzenAI-SW\demo\ASR\Whisper"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  AMD Whisper ASR - NPU Transcription Test" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Model: $Model"
Write-Host "Device: $Device"
Write-Host "Audio: $AudioFile"
Write-Host ""

Push-Location $whisperDir
try {
    & $pythonPath run_whisper.py --model-type $Model --device $Device --input $AudioFile
} finally {
    Pop-Location
}

Write-Host ""
Write-Host "=== Done ===" -ForegroundColor Cyan
