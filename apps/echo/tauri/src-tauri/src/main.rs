//! ECHO - Voice Recording & Transcription
//!
//! Tauri application for audio capture using WASAPI loopback
//! (system audio) and microphone input.

#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

mod audio_capture;
mod hotkeys;
mod tray;
#[cfg(windows)]
mod wasapi_loopback;

use audio_capture::{AudioCapture, AudioSource};
use std::sync::{Arc, Mutex};
use tauri::{Manager, State};

/// Application state shared across commands
struct AppState {
    audio_capture: Arc<Mutex<AudioCapture>>,
}

/// Start recording audio
#[tauri::command]
async fn start_recording(
    state: State<'_, AppState>,
    recording_id: String,
    source: String,
    output_path: String,
) -> Result<(), String> {
    let source = match source.as_str() {
        "microphone" => AudioSource::Microphone,
        "system" => AudioSource::System,
        "both" => AudioSource::Both,
        _ => return Err("Invalid audio source".into()),
    };

    let mut capture = state
        .audio_capture
        .lock()
        .map_err(|e| e.to_string())?;

    capture
        .start(recording_id, source, output_path)
        .map_err(|e| e.to_string())
}

/// Stop recording audio
#[tauri::command]
async fn stop_recording(state: State<'_, AppState>) -> Result<RecordingResult, String> {
    let mut capture = state
        .audio_capture
        .lock()
        .map_err(|e| e.to_string())?;

    capture.stop().map_err(|e| e.to_string())
}

/// Get recording status
#[tauri::command]
async fn get_recording_status(state: State<'_, AppState>) -> Result<RecordingStatus, String> {
    let capture = state
        .audio_capture
        .lock()
        .map_err(|e| e.to_string())?;

    Ok(capture.status())
}

/// List available audio devices
#[tauri::command]
async fn list_audio_devices() -> Result<AudioDevices, String> {
    AudioCapture::list_devices().map_err(|e| e.to_string())
}

/// Recording result returned when stopping
#[derive(serde::Serialize)]
struct RecordingResult {
    recording_id: String,
    duration_seconds: f64,
    file_size_bytes: u64,
    output_path: String,
}

/// Current recording status
#[derive(serde::Serialize)]
struct RecordingStatus {
    is_recording: bool,
    recording_id: Option<String>,
    duration_seconds: f64,
    source: Option<String>,
}

/// Available audio devices
#[derive(serde::Serialize)]
struct AudioDevices {
    input_devices: Vec<AudioDevice>,
    output_devices: Vec<AudioDevice>,
}

#[derive(serde::Serialize)]
struct AudioDevice {
    id: String,
    name: String,
    is_default: bool,
}

fn main() {
    env_logger::init();

    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_global_shortcut::Builder::new().build())
        .setup(|app| {
            // Initialize audio capture
            let audio_capture = AudioCapture::new();

            // Store state
            app.manage(AppState {
                audio_capture: Arc::new(Mutex::new(audio_capture)),
            });

            // Setup system tray
            #[cfg(desktop)]
            {
                let handle = app.handle();
                tray::setup_tray(handle)?;
            }

            // Setup global hotkeys
            #[cfg(desktop)]
            {
                if let Err(e) = hotkeys::setup_hotkeys(app.handle()) {
                    log::warn!("Failed to setup global hotkeys: {}", e);
                }
            }

            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            start_recording,
            stop_recording,
            get_recording_status,
            list_audio_devices,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
