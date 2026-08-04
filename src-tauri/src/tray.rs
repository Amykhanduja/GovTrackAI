use tauri::{AppHandle, CustomMenuItem, Manager, SystemTray, SystemTrayMenu, SystemTrayMenuItem, SystemTrayEvent};
use tauri::api::notification::Notification;

pub fn create_tray() -> SystemTray {
    let open_dash = CustomMenuItem::new("open_dash".to_string(), "Open Dashboard");
    let force_scrape = CustomMenuItem::new("force_scrape".to_string(), "Run Scrapers Now");
    let generate_excel = CustomMenuItem::new("generate_excel".to_string(), "Generate Excel Report");
    let pause_scheduler = CustomMenuItem::new("pause_scheduler".to_string(), "Pause Scheduler");
    let quit = CustomMenuItem::new("quit".to_string(), "Exit Application");

    let tray_menu = SystemTrayMenu::new()
        .add_item(open_dash)
        .add_native_item(SystemTrayMenuItem::Separator)
        .add_item(force_scrape)
        .add_item(generate_excel)
        .add_native_item(SystemTrayMenuItem::Separator)
        .add_item(pause_scheduler)
        .add_native_item(SystemTrayMenuItem::Separator)
        .add_item(quit);

    SystemTray::new().with_menu(tray_menu)
}

pub fn handle_tray_event(app: &AppHandle, event: SystemTrayEvent) {
    match event {
        SystemTrayEvent::MenuItemClick { id, .. } => {
            match id.as_str() {
                "open_dash" => {
                    let window = app.get_window("main").unwrap();
                    window.show().unwrap();
                    window.set_focus().unwrap();
                }
                "force_scrape" => {
                    Notification::new(&app.config().tauri.bundle.identifier)
                        .title("GovTrack AI")
                        .body("Scrapers initiated in background.")
                        .show()
                        .unwrap();
                    // IPC trigger to backend would go here
                }
                "quit" => {
                    app.exit(0);
                }
                _ => {}
            }
        }
        SystemTrayEvent::DoubleClick { .. } => {
            let window = app.get_window("main").unwrap();
            window.show().unwrap();
            window.set_focus().unwrap();
        }
        _ => {}
    }
}
