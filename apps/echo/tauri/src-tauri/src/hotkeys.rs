//! Global hotkey registration for ECHO.
//!
//! Provides system-wide keyboard shortcuts for quick recording control:
//! - Ctrl+Shift+R: Toggle recording
//! - Ctrl+Shift+P: Pause/Resume
//! - Ctrl+Shift+S: Stop recording

use tauri::{AppHandle, Emitter};
use tauri_plugin_global_shortcut::{GlobalShortcutExt, Shortcut, ShortcutState};

/// Setup global hotkeys for the application
pub fn setup_hotkeys(app: &AppHandle) -> Result<(), Box<dyn std::error::Error>> {
    let shortcut_manager = app.global_shortcut();

    // Toggle recording: Ctrl+Shift+R
    let toggle_shortcut = "CommandOrControl+Shift+R".parse::<Shortcut>()?;
    shortcut_manager.on_shortcut(toggle_shortcut.clone(), |app, _shortcut, event| {
        if event.state == ShortcutState::Pressed {
            log::info!("Hotkey: Toggle recording (Ctrl+Shift+R)");
            if let Err(e) = app.emit("hotkey:toggle-recording", ()) {
                log::error!("Failed to emit toggle-recording event: {}", e);
            }
        }
    })?;
    shortcut_manager.register(toggle_shortcut)?;

    // Pause/Resume: Ctrl+Shift+P
    let pause_shortcut = "CommandOrControl+Shift+P".parse::<Shortcut>()?;
    shortcut_manager.on_shortcut(pause_shortcut.clone(), |app, _shortcut, event| {
        if event.state == ShortcutState::Pressed {
            log::info!("Hotkey: Pause/Resume (Ctrl+Shift+P)");
            if let Err(e) = app.emit("hotkey:pause-resume", ()) {
                log::error!("Failed to emit pause-resume event: {}", e);
            }
        }
    })?;
    shortcut_manager.register(pause_shortcut)?;

    // Stop recording: Ctrl+Shift+S
    let stop_shortcut = "CommandOrControl+Shift+S".parse::<Shortcut>()?;
    shortcut_manager.on_shortcut(stop_shortcut.clone(), |app, _shortcut, event| {
        if event.state == ShortcutState::Pressed {
            log::info!("Hotkey: Stop recording (Ctrl+Shift+S)");
            if let Err(e) = app.emit("hotkey:stop-recording", ()) {
                log::error!("Failed to emit stop-recording event: {}", e);
            }
        }
    })?;
    shortcut_manager.register(stop_shortcut)?;

    log::info!("Global hotkeys registered:");
    log::info!("  - Ctrl+Shift+R: Toggle recording");
    log::info!("  - Ctrl+Shift+P: Pause/Resume");
    log::info!("  - Ctrl+Shift+S: Stop recording");

    Ok(())
}

/// Unregister all hotkeys (called on shutdown)
#[allow(dead_code)]
pub fn cleanup_hotkeys(app: &AppHandle) -> Result<(), Box<dyn std::error::Error>> {
    let shortcut_manager = app.global_shortcut();

    // Unregister all shortcuts
    let toggle_shortcut = "CommandOrControl+Shift+R".parse::<Shortcut>()?;
    let pause_shortcut = "CommandOrControl+Shift+P".parse::<Shortcut>()?;
    let stop_shortcut = "CommandOrControl+Shift+S".parse::<Shortcut>()?;

    let _ = shortcut_manager.unregister(toggle_shortcut);
    let _ = shortcut_manager.unregister(pause_shortcut);
    let _ = shortcut_manager.unregister(stop_shortcut);

    log::info!("Global hotkeys unregistered");

    Ok(())
}
