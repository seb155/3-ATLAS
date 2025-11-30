//! System tray functionality for ECHO

use tauri::{
    menu::{MenuBuilder, MenuItemBuilder},
    tray::{TrayIconBuilder, TrayIconEvent},
    AppHandle, Manager,
};

/// Setup the system tray icon and menu
pub fn setup_tray(app: &AppHandle) -> Result<(), Box<dyn std::error::Error>> {
    // Create menu items
    let show = MenuItemBuilder::new("Show ECHO")
        .id("show")
        .build(app)?;

    let record = MenuItemBuilder::new("Quick Record")
        .id("record")
        .build(app)?;

    let quit = MenuItemBuilder::new("Quit")
        .id("quit")
        .build(app)?;

    // Build the menu
    let menu = MenuBuilder::new(app)
        .item(&show)
        .separator()
        .item(&record)
        .separator()
        .item(&quit)
        .build()?;

    // Create tray icon
    let _tray = TrayIconBuilder::new()
        .menu(&menu)
        .tooltip("ECHO - Voice Recording")
        .on_menu_event(|app, event| {
            match event.id().as_ref() {
                "show" => {
                    if let Some(window) = app.get_webview_window("main") {
                        let _ = window.show();
                        let _ = window.set_focus();
                    }
                }
                "record" => {
                    // TODO: Trigger quick record
                    log::info!("Quick record triggered from tray");
                }
                "quit" => {
                    app.exit(0);
                }
                _ => {}
            }
        })
        .on_tray_icon_event(|tray, event| {
            if let TrayIconEvent::Click { .. } = event {
                if let Some(window) = tray.app_handle().get_webview_window("main") {
                    let _ = window.show();
                    let _ = window.set_focus();
                }
            }
        })
        .build(app)?;

    log::info!("System tray initialized");

    Ok(())
}
