# ECHO - NPU Installation Plan

**Date:** 2025-11-29
**Status:** En cours - Redemarrage requis

---

## Status Installation

| Etape | Status | Notes |
|-------|--------|-------|
| Miniforge 25.9.1 | ✅ Complete | `C:\Users\sgagn\miniforge3` |
| VS2022 Build Tools C++ | ✅ Complete | Redemarrage PC requis |
| NPU Driver MCDM | ⏳ En attente | Telecharger depuis AMD |
| Ryzen AI SDK 1.6.1 | ⏳ En attente | `D:\Downloads\ryzenai-lt-1.6.1.exe` |

---

## Prochaines Etapes (apres redemarrage)

### 1. Installer NPU Driver
```powershell
# Telecharger: NPU_RAI1.6_304_WHQL.zip
# https://account.amd.com/en/forms/downloads/ryzenai-eula-public-xef.html?filename=NPU_RAI1.6_304_WHQL.zip

# Extraire et executer en admin:
.\npu_sw_installer.exe

# Verifier dans Task Manager > Performance > NPU0
```

### 2. Installer Ryzen AI SDK
```powershell
# Executer l'installeur
D:\Downloads\ryzenai-lt-1.6.1.exe

# Activer l'environnement
"C:\Users\sgagn\miniforge3\condabin\conda.bat" activate ryzenai-1.6.1

# Tester
cd "C:\Program Files\RyzenAI\1.6.1\quicktest"
python quicktest.py
# Attendu: "398 NPU operators" et "Actually running on NPU 1"
```

---

## Hardware Cible

- **Laptop**: ASUS Zenbook S 16 UM5606WA
- **CPU**: AMD Ryzen AI 9 HX 370 (12c/24t)
- **GPU**: AMD Radeon 890M (gfx1150 - NON supporte ROCm)
- **NPU**: AMD XDNA (50 TOPS) - Ryzen AI 300 series

---

## Strategie Transcription

```
Priorite: NPU (Ryzen AI) > CPU (faster-whisper)
GPU skip: Radeon 890M non supporte par ROCm
```

### Performance Attendue

| Modele | NPU (30s audio) | CPU (30s audio) |
|--------|-----------------|-----------------|
| base | ~2s | ~5s |
| medium | ~5s | ~15s |
| large-v3 | ~10s | ~45s |

---

## Fichiers Backend Deja Modifies

1. `backend/app/services/whisper_npu.py` - Service NPU ONNX Runtime
2. `backend/app/services/transcription_service.py` - Auto-detection NPU/CPU
3. `backend/app/config.py` - Variables WHISPER_*
4. `backend/requirements.txt` - onnxruntime, transformers, librosa
5. `docker-compose.dev.yml` - WHISPER_DEVICE=auto
6. `backend/app/api/endpoints/health.py` - Device info dans health check

---

## Pour Reprendre

Dire: "on continue l'installation NPU"

---

## References

- [AMD Ryzen AI SDK 1.6.1](https://ryzenai.docs.amd.com/en/latest/inst.html)
- [AMD Whisper NPU Article](https://www.amd.com/en/developer/resources/technical-articles/2025/unlocking-on-device-asr-with-whisper-on-ryzen-ai-npus.html)
- [ROCm gfx1150 Issue](https://github.com/ROCm/ROCm/issues/5108)
