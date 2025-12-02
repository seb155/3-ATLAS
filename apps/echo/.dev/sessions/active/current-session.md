# Session ECHO - 2025-12-01

## Objectif
Terminer l'application Echo avec focus sur:
1. Qualité de transcription FR-QC
2. Sélection modèle/device (NPU/GPU/CPU)
3. Desktop complet avec WASAPI loopback

## Status: IMPLÉMENTATION TERMINÉE

---

## Phase 1: Qualité de Transcription - COMPLÉTÉ

### 1.1 Sélecteur Modèle + Device
**Fichiers modifiés:**
- `backend/app/config.py` - Ajout WHISPER_MODELS, WHISPER_DEVICES, défaut large-v3
- `backend/app/services/device_detector.py` - **NOUVEAU** - Détection NPU/GPU/CPU
- `backend/app/api/endpoints/settings.py` - **NOUVEAU** - API REST pour settings
- `backend/app/main.py` - Router settings ajouté
- `frontend/src/services/api.ts` - Types et settingsApi
- `frontend/src/pages/SettingsPage.tsx` - UI complète sélecteur

**API Endpoints:**
```
GET  /api/v1/settings/whisper         # Obtenir config + devices disponibles
POST /api/v1/settings/whisper         # Changer modèle/device
GET  /api/v1/settings/whisper/devices # Info détaillée devices
POST /api/v1/settings/whisper/reload  # Forcer rechargement modèle
```

### 1.2 Initial Prompts Français Québécois
**Fichier:** `backend/app/services/whisper_local.py`

Ajout de prompts pour guider Whisper:
```python
INITIAL_PROMPTS = {
    "fr": "Transcription au Québec. Ben là, tsé, c'est vraiment pas évident...",
    "fr-CA": "...",
    "bilingual": "Okay, so on va faire le review du code, pis after...",
    "en": "Meeting transcript with technical discussion...",
}
```

### 1.3 Audio Padding (Mots Manquants)
**Fichier:** `backend/app/services/audio_preprocessor.py` - **NOUVEAU**

- Ajoute 500ms de silence avant l'audio
- Ajoute 300ms après
- Évite les mots coupés au début par le VAD
- Utilise context manager pour cleanup automatique

### 1.4 VAD Parameters Optimisés
**Fichier:** `backend/app/services/whisper_local.py`

```python
vad_parameters=dict(
    min_silence_duration_ms=400,   # était 500
    speech_pad_ms=500,             # était 400
    threshold=0.35,                # était 0.5
    min_speech_duration_ms=100,    # nouveau - capture "tsé", "ben"
)
```

### 1.5 Seuil Code-Switching
**Fichier:** `backend/app/services/whisper_npu.py` ligne ~598

```python
# De 5% à 15% pour éviter faux positifs
is_code_switched = fr_ratio >= 0.15 and en_ratio >= 0.15
```

---

## Phase 2: Desktop App - COMPLÉTÉ

### 2.1 WASAPI Loopback
**Fichiers:**
- `tauri/src-tauri/Cargo.toml` - Dépendance `windows` crate
- `tauri/src-tauri/src/wasapi_loopback.rs` - **NOUVEAU**

Capture audio système Windows via WASAPI loopback mode:
- Thread dédié avec Arc<AtomicBool> pour contrôle
- Buffer limité (10 min max) avec protection mémoire
- Support format float32

### 2.2 Intégration audio_capture.rs
**Fichier:** `tauri/src-tauri/src/audio_capture.rs`

- Import conditionnel `#[cfg(windows)]`
- Nouveau champ `loopback_capture: Option<LoopbackCapture>`
- Mixage audio (mic + system) pour mode "Both"
- Buffer avec limite mémoire MAX_SAMPLES

### 2.3 Global Hotkeys
**Fichiers:**
- `tauri/src-tauri/Cargo.toml` - Dépendance `tauri-plugin-global-shortcut`
- `tauri/src-tauri/src/hotkeys.rs` - **NOUVEAU**
- `tauri/src-tauri/src/main.rs` - Plugin et setup

Raccourcis:
- `Ctrl+Shift+R` - Toggle recording
- `Ctrl+Shift+P` - Pause/Resume
- `Ctrl+Shift+S` - Stop recording

### 2.4 Détection Tauri Frontend
**Fichier:** `frontend/src/hooks/useTauriEnvironment.ts` - **NOUVEAU**

```typescript
export function useTauriEnvironment(): TauriEnvironment {
  // Détecte __TAURI_INTERNALS__ ou __TAURI__
  return {
    isTauri,
    capabilities: {
      systemAudio: isTauri,
      globalHotkeys: isTauri,
      systemTray: isTauri,
    },
  };
}
```

### 2.5 RecordPage Integration
**Fichier:** `frontend/src/pages/RecordPage.tsx`

- Import useTauriEnvironment
- Boutons System/Both activés quand `capabilities.systemAudio`
- Tooltip "Requires desktop app" quand web

---

## Fichiers Créés (Nouveaux)

| Fichier | Description |
|---------|-------------|
| `backend/app/services/device_detector.py` | Détection NPU/GPU/CPU |
| `backend/app/services/audio_preprocessor.py` | Padding audio |
| `backend/app/api/endpoints/settings.py` | API settings Whisper |
| `tauri/src-tauri/src/wasapi_loopback.rs` | Capture WASAPI |
| `tauri/src-tauri/src/hotkeys.rs` | Hotkeys globaux |
| `frontend/src/hooks/useTauriEnvironment.ts` | Détection Tauri |

## Fichiers Modifiés

| Fichier | Changements |
|---------|-------------|
| `backend/app/config.py` | WHISPER_MODELS, WHISPER_DEVICES, large-v3 défaut |
| `backend/app/services/whisper_local.py` | Initial prompts, VAD, preprocessing |
| `backend/app/services/whisper_npu.py` | Seuil 15% code-switching |
| `backend/app/main.py` | Router settings |
| `tauri/src-tauri/Cargo.toml` | windows, global-shortcut |
| `tauri/src-tauri/src/main.rs` | Modules, plugins |
| `tauri/src-tauri/src/audio_capture.rs` | WASAPI integration |
| `frontend/src/services/api.ts` | settingsApi |
| `frontend/src/pages/SettingsPage.tsx` | UI sélecteur complet |
| `frontend/src/pages/RecordPage.tsx` | Tauri detection |

---

## Tests Recommandés

1. **Transcription FR-QC**: "Ben là, tsé, faque on va checker ça"
2. **Mots début**: Vérifier premiers mots pas coupés
3. **Bilingue**: "Okay so on va faire le review pis after..."
4. **Settings API**: GET/POST /api/v1/settings/whisper
5. **Device detection**: Vérifier NPU/GPU/CPU affichés
6. **WASAPI** (Windows): Capturer audio YouTube/Spotify
7. **Hotkeys** (Desktop): Ctrl+Shift+R depuis autre app

---

## Prochaines Étapes Potentielles

1. Améliorer tray.rs avec indicateur recording
2. Ajouter listener hotkeys dans RecordPage.tsx
3. Tests unitaires backend
4. Build et test Tauri Windows
5. Intégration NEXUS
