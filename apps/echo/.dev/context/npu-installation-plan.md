# ECHO - NPU Installation Plan

**Date:** 2025-11-29
**Status:** ✅ COMPLETE - NPU fonctionnel!

---

## Installation Status

| Étape | Status | Notes |
|-------|--------|-------|
| Miniforge 25.9.1 | ✅ Complete | `C:\Users\sgagn\miniforge3` |
| VS2022 Build Tools C++ | ✅ Complete | Requis pour compilation |
| NPU Driver MCDM | ✅ Complete | `NPU Compute Accelerator Device - OK` |
| Ryzen AI SDK 1.6.1 | ✅ Complete | `C:\Program Files\RyzenAI\1.6.1` |
| Quicktest Validation | ✅ Complete | 398 NPU operators, Test Passed |

---

## Hardware Confirmé

- **Laptop**: ASUS Zenbook S 16 UM5606WA
- **CPU**: AMD Ryzen AI 9 HX 370 (12c/24t)
- **GPU**: AMD Radeon 890M (gfx1150 - NON supporté ROCm)
- **NPU**: AMD XDNA (50 TOPS) - Ryzen AI 300 series (STX)

---

## Quicktest Results

```
[Vitis AI EP] No. of Operators :   NPU   398 VITIS_EP_CPU     2
[Vitis AI EP] No. of Subgraphs :   NPU     1 Actually running on NPU      1
Test Passed
```

---

## Configuration

### Conda Environment

```powershell
# Activer l'environnement
conda activate ryzen-ai-1.6.1

# Ou avec chemin complet
C:\Users\sgagn\miniforge3\envs\ryzen-ai-1.6.1\python.exe
```

### Variables d'environnement requises

```powershell
$env:RYZEN_AI_INSTALLATION_PATH = "C:\Program Files\RyzenAI\1.6.1"
```

### Script de test NPU

```powershell
# Exécuter le quicktest
powershell -ExecutionPolicy Bypass -File "D:\Projects\AXIOM\apps\echo\.dev\scripts\run-npu-quicktest.ps1"
```

---

## Stratégie Transcription ECHO

```
Priorité: NPU (Ryzen AI XDNA) > CPU (faster-whisper)
GPU skip: Radeon 890M non supporté par ROCm
```

### Performance Attendue (30s audio)

| Modèle | NPU | CPU |
|--------|-----|-----|
| base | ~2s | ~5s |
| medium | ~5s | ~15s |
| large-v3 | ~10s | ~45s |

---

## Fichiers Backend ECHO

| Fichier | Purpose |
|---------|---------|
| `backend/app/services/whisper_npu.py` | Service NPU ONNX Runtime |
| `backend/app/services/transcription_service.py` | Auto-detection NPU/CPU |
| `backend/app/config.py` | Variables WHISPER_* |
| `backend/requirements.txt` | onnxruntime, transformers, librosa |
| `docker-compose.dev.yml` | WHISPER_DEVICE=auto |
| `backend/app/api/endpoints/health.py` | Device info dans health check |

---

## Prochaines Étapes (ECHO Development)

1. [ ] Intégrer Whisper ONNX optimisé NPU dans `whisper_npu.py`
2. [ ] Télécharger modèle Whisper quantifié pour NPU
3. [ ] Tester transcription réelle avec audio FR-CA
4. [ ] Benchmark NPU vs CPU
5. [ ] Intégrer dans Docker (si possible) ou mode hybride

---

## Références

- [AMD Ryzen AI SDK 1.6.1 Docs](https://ryzenai.docs.amd.com/en/latest/inst.html)
- [AMD Whisper NPU Article](https://www.amd.com/en/developer/resources/technical-articles/2025/unlocking-on-device-asr-with-whisper-on-ryzen-ai-npus.html)
- [ROCm gfx1150 Issue](https://github.com/ROCm/ROCm/issues/5108)

---

**Installation terminée:** 2025-11-29 22:43
