# Run NPU Quicktest Script
# Sets environment variables and runs the AMD Ryzen AI quicktest

$env:RYZEN_AI_INSTALLATION_PATH = "C:\Program Files\RyzenAI\1.6.1"
$env:Path = "C:\Program Files\RyzenAI\1.6.1;" + $env:Path

Write-Host "=== NPU Quicktest ===" -ForegroundColor Cyan
Write-Host "RYZEN_AI_INSTALLATION_PATH: $env:RYZEN_AI_INSTALLATION_PATH"
Write-Host ""

# Use the ryzen-ai conda environment Python
$pythonPath = "C:\Users\sgagn\miniforge3\envs\ryzen-ai-1.6.1\python.exe"
$testScript = "C:\Program Files\RyzenAI\1.6.1\quicktest\quicktest.py"

Write-Host "Running: $pythonPath $testScript" -ForegroundColor Yellow
Write-Host ""

& $pythonPath $testScript

Write-Host ""
Write-Host "=== Done ===" -ForegroundColor Cyan
