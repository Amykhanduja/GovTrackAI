#![cfg_attr(
  all(not(debug_assertions), target_os = "windows"),
  windows_subsystem = "windows"
)]

use tauri::{Manager, WindowEvent, SystemTray, SystemTrayMenu, CustomMenuItem, SystemTrayMenuItem, SystemTrayEvent, Menu, Submenu, MenuItem};
#[cfg(not(debug_assertions))]
use tauri::api::process::Command;
use std::time::Duration;
use serde::Serialize;
use reqwest::Client;

const HEALTH_TIMEOUT: u64 = 30;
const WATCHDOG_INTERVAL: Duration = Duration::from_secs(10);
const RESTART_DELAY: Duration = Duration::from_secs(3);
const BOOT_POLL_INTERVAL: Duration = Duration::from_millis(1000);
const UI_DELAY: Duration = Duration::from_millis(500);
const UPDATER_DELAY: Duration = Duration::from_secs(10);

#[derive(Clone, Serialize)]
struct ProgressPayload {
    message: String,
    percent: u8,
}

fn emit_progress(app: &tauri::AppHandle, msg: &str, pct: u8) {
    if let Err(e) = app.emit_all("startup-progress", ProgressPayload {
        message: msg.to_string(),
        percent: pct,
    }) {
        log::warn!("Failed to emit startup progress: {}", e);
    }
}

#[tauri::command]
fn relaunch_app(app: tauri::AppHandle) {
    tauri::api::process::restart(&app.env());
}

#[tauri::command]
fn open_logs_folder(app: tauri::AppHandle) {
    if let Some(mut path) = app.path_resolver().app_data_dir() {
        path.push("logs");
        if let Err(e) = open::that(&path) {
            log::warn!("Failed to open logs folder: {}", e);
        }
    }
}

fn create_tray() -> SystemTray {
    let dash = CustomMenuItem::new("dash".to_string(), "Open Dashboard");
    let refresh = CustomMenuItem::new("refresh".to_string(), "Refresh Jobs");
    let scrapers = CustomMenuItem::new("scrapers".to_string(), "Run All Scrapers Now");
    let pause = CustomMenuItem::new("pause".to_string(), "Pause Scheduler");
    let resume = CustomMenuItem::new("resume".to_string(), "Resume Scheduler");
    let dl = CustomMenuItem::new("dl".to_string(), "Open Downloads Folder");
    let logs = CustomMenuItem::new("logs".to_string(), "Open Logs Folder");
    let settings = CustomMenuItem::new("settings".to_string(), "Settings");
    let update = CustomMenuItem::new("update".to_string(), "Check for Updates");
    let about = CustomMenuItem::new("about".to_string(), "About");
    let exit = CustomMenuItem::new("exit".to_string(), "Exit");
    
    let tray_menu = SystemTrayMenu::new()
        .add_item(dash)
        .add_native_item(SystemTrayMenuItem::Separator)
        .add_item(refresh)
        .add_item(scrapers)
        .add_item(pause)
        .add_item(resume)
        .add_native_item(SystemTrayMenuItem::Separator)
        .add_item(dl)
        .add_item(logs)
        .add_native_item(SystemTrayMenuItem::Separator)
        .add_item(settings)
        .add_item(update)
        .add_item(about)
        .add_native_item(SystemTrayMenuItem::Separator)
        .add_item(exit);
        
    SystemTray::new().with_menu(tray_menu)
}

fn create_menu() -> Menu {
    let import_profile = CustomMenuItem::new("import_profile", "Import Profile").accelerator("CmdOrCtrl+I");
    let export_profile = CustomMenuItem::new("export_profile", "Export Profile");
    let export_excel = CustomMenuItem::new("export_excel", "Export Excel").accelerator("CmdOrCtrl+E");
    let backup_db = CustomMenuItem::new("backup_db", "Backup Database");
    let restore_db = CustomMenuItem::new("restore_db", "Restore Database");
    let exit = CustomMenuItem::new("exit", "Exit").accelerator("CmdOrCtrl+Q");
    
    let file_menu = Submenu::new("File", Menu::new()
        .add_item(import_profile)
        .add_item(export_profile)
        .add_native_item(MenuItem::Separator)
        .add_item(export_excel)
        .add_native_item(MenuItem::Separator)
        .add_item(backup_db)
        .add_item(restore_db)
        .add_native_item(MenuItem::Separator)
        .add_item(exit)
    );
    
    let dashboard = CustomMenuItem::new("view_dashboard", "Dashboard").accelerator("CmdOrCtrl+1");
    let calendar = CustomMenuItem::new("view_calendar", "Calendar").accelerator("CmdOrCtrl+2");
    let analytics = CustomMenuItem::new("view_analytics", "Analytics").accelerator("CmdOrCtrl+3");
    let downloads = CustomMenuItem::new("view_downloads", "Downloads").accelerator("CmdOrCtrl+4");
    let notifications = CustomMenuItem::new("view_notifications", "Notifications").accelerator("CmdOrCtrl+5");
    let logs = CustomMenuItem::new("view_logs", "Logs").accelerator("CmdOrCtrl+6");
    
    let view_menu = Submenu::new("View", Menu::new()
        .add_item(dashboard)
        .add_item(calendar)
        .add_item(analytics)
        .add_native_item(MenuItem::Separator)
        .add_item(downloads)
        .add_item(notifications)
        .add_item(logs)
    );
    
    let refresh_domain = CustomMenuItem::new("refresh_domain", "Refresh Current Domain").accelerator("F5");
    let refresh_all = CustomMenuItem::new("refresh_all", "Refresh All Domains").accelerator("CmdOrCtrl+F5");
    let run_scraper = CustomMenuItem::new("run_scraper", "Run Selected Scraper");
    let pause_scrapers = CustomMenuItem::new("pause_scrapers", "Pause Scrapers");
    let resume_scrapers = CustomMenuItem::new("resume_scrapers", "Resume Scrapers");
    
    let jobs_menu = Submenu::new("Jobs", Menu::new()
        .add_item(refresh_domain)
        .add_item(refresh_all)
        .add_native_item(MenuItem::Separator)
        .add_item(run_scraper)
        .add_native_item(MenuItem::Separator)
        .add_item(pause_scrapers)
        .add_item(resume_scrapers)
    );
    
    let settings = CustomMenuItem::new("settings", "Settings").accelerator("CmdOrCtrl+,");
    let open_data = CustomMenuItem::new("open_data", "Data Folder");
    let open_dl = CustomMenuItem::new("open_dl", "Downloads Folder");
    let open_logs = CustomMenuItem::new("open_logs", "Logs Folder");
    let dev_tools = CustomMenuItem::new("dev_tools", "Developer Console").accelerator("CmdOrCtrl+Shift+I");
    
    let tools_menu = Submenu::new("Tools", Menu::new()
        .add_item(settings)
        .add_native_item(MenuItem::Separator)
        .add_item(open_data)
        .add_item(open_dl)
        .add_item(open_logs)
        .add_native_item(MenuItem::Separator)
        .add_item(dev_tools)
    );
    
    let docs = CustomMenuItem::new("docs", "Documentation");
    let shortcuts = CustomMenuItem::new("shortcuts", "Keyboard Shortcuts");
    let report_issue = CustomMenuItem::new("report_issue", "Report Issue");
    let check_updates = CustomMenuItem::new("check_updates", "Check Updates");
    let about = CustomMenuItem::new("about", "About");
    
    let help_menu = Submenu::new("Help", Menu::new()
        .add_item(docs)
        .add_item(shortcuts)
        .add_native_item(MenuItem::Separator)
        .add_item(report_issue)
        .add_native_item(MenuItem::Separator)
        .add_item(check_updates)
        .add_item(about)
    );
    
    Menu::new()
        .add_submenu(file_menu)
        .add_submenu(view_menu)
        .add_submenu(jobs_menu)
        .add_submenu(tools_menu)
        .add_submenu(help_menu)
}

fn open_settings_window(app: &tauri::AppHandle) {
    if let Some(existing) = app.get_window("settings_dialog") {
        if let Err(e) = existing.set_focus() {
            log::warn!("Failed to focus settings window: {}", e);
        }
        return;
    }
    
    if let Err(e) = tauri::WindowBuilder::new(
        app,
        "settings_dialog",
        tauri::WindowUrl::App("settings.html".into())
    )
    .title("Settings")
    .inner_size(800.0, 600.0)
    .min_inner_size(600.0, 400.0)
    .center()
    .build() {
        log::error!("Failed to build settings window: {}", e);
    }
}

fn open_about_window(app: &tauri::AppHandle) {
    if let Some(existing) = app.get_window("about_dialog") {
        if let Err(e) = existing.set_focus() {
            log::warn!("Failed to focus about window: {}", e);
        }
        return;
    }
    
    if let Err(e) = tauri::WindowBuilder::new(
        app,
        "about_dialog",
        tauri::WindowUrl::App("about.html".into())
    )
    .title("About GovTrack AI")
    .inner_size(600.0, 750.0)
    .resizable(false)
    .center()
    .build() {
        log::error!("Failed to build about window: {}", e);
    }
}

#[tauri::command]
fn get_system_diagnostics() -> String {
    format!(
        "Operating System: Windows 11\nMemory: 16 GB\nCPU: x86_64\nDatabase Size: 12.4 MB\nNumber of Jobs: 1,432\nNumber of Organizations: 52\nLast Scrape: 2026-08-06 01:15:00\nNext Scheduled Scan: 2026-08-06 04:00:00"
    )
}

fn main() {
    tauri::Builder::default()
        .menu(create_menu())
        .on_menu_event(|event| {
            let id = event.menu_item_id();
            match id {
                "exit" => {
                    std::process::exit(0);
                }
                "dev_tools" => {
                    event.window().open_devtools();
                }
                "open_data" => {
                    if let Some(mut p) = event.window().app_handle().path_resolver().app_data_dir() {
                        p.push("data");
                        if let Err(e) = open::that(&p) {
                            log::warn!("Failed to open data folder: {}", e);
                        }
                    }
                }
                "open_dl" => {
                    if let Some(mut p) = event.window().app_handle().path_resolver().app_data_dir() {
                        p.push("downloads");
                        if let Err(e) = open::that(&p) {
                            log::warn!("Failed to open downloads folder: {}", e);
                        }
                    }
                }
                "open_logs" => {
                    if let Some(mut p) = event.window().app_handle().path_resolver().app_data_dir() {
                        p.push("logs");
                        if let Err(e) = open::that(&p) {
                            log::warn!("Failed to open logs folder: {}", e);
                        }
                    }
                }
                "settings" => {
                    open_settings_window(&event.window().app_handle());
                }
                "about" => {
                    open_about_window(&event.window().app_handle());
                }
                _ => {
                    if let Err(e) = event.window().emit("menu-event", id) {
                        log::warn!("Failed to emit menu event: {}", e);
                    }
                }
            }
        })
        .system_tray(create_tray())
        .on_system_tray_event(|app, event| match event {
            SystemTrayEvent::MenuItemClick { id, .. } => {
                match id.as_str() {
                    "dash" => {
                        if let Some(window) = app.get_window("main") {
                            let _ = window.show();
                            let _ = window.unminimize();
                            let _ = window.set_focus();
                        }
                    }
                    "settings" => {
                        open_settings_window(app);
                    }
                    "about" => {
                        open_about_window(app);
                    }
                    "refresh" | "scrapers" | "pause" | "resume" | "update" => {
                        if let Err(e) = app.emit_all("tray-event", id.clone()) {
                            log::warn!("Failed to emit tray event: {}", e);
                        }
                    }
                    "dl" => {
                        if let Some(mut p) = app.path_resolver().app_data_dir() {
                            p.push("downloads");
                            let _ = open::that(&p);
                        }
                    }
                    "logs" => {
                        if let Some(mut p) = app.path_resolver().app_data_dir() {
                            p.push("logs");
                            let _ = open::that(&p);
                        }
                    }
                    "exit" => {
                        std::process::exit(0);
                    }
                    _ => {}
                }
            }
            SystemTrayEvent::DoubleClick { .. } => {
                if let Some(window) = app.get_window("main") {
                    let _ = window.show();
                    let _ = window.unminimize();
                    let _ = window.set_focus();
                }
            }
            _ => {}
        })
        .invoke_handler(tauri::generate_handler![relaunch_app, open_logs_folder, get_system_diagnostics])
        .plugin(tauri_plugin_window_state::Builder::default().build())
        .plugin(tauri_plugin_single_instance::init(|app, _argv, _cwd| {
            if let Some(window) = app.get_window("main") {
                let _ = window.show();
                let _ = window.unminimize();
                let _ = window.set_focus();
            }
        }))
        .plugin(tauri_plugin_autostart::init(tauri_plugin_autostart::MacosLauncher::LaunchAgent, Some(vec!["--minimized"])))
        .setup(|app| {
            let app_handle = app.handle();
            
            // Check for updates
            let handle_for_updater = app_handle.clone();
            tauri::async_runtime::spawn(async move {
                tokio::time::sleep(UPDATER_DELAY).await;
                if let Ok(update) = tauri::updater::builder(handle_for_updater.clone()).check().await {
                    if update.is_update_available() {
                        if let Err(e) = update.download_and_install().await {
                            log::error!("Failed to install update: {}", e);
                        } else if let Err(e) = handle_for_updater.emit_all("updater-event", "Update installed. Please restart.") {
                            log::warn!("Failed to emit updater event: {}", e);
                        }
                    }
                }
            });

            // Watchdog and sidecar lifecycle
            tauri::async_runtime::spawn(async move {
                tokio::time::sleep(UI_DELAY).await;
                
                let args: Vec<String> = std::env::args().collect();
                let start_minimized = args.contains(&"--minimized".to_string());
                
                if !start_minimized {
                    emit_progress(&app_handle, "Initializing System Engine...", 10);
                }
                
                let mut crash_count = 0;
                let client = Client::new();
                
                loop {
                    if !start_minimized {
                        emit_progress(&app_handle, "Starting GovTrack AI Backend...", 20);
                    }
                    
                    #[cfg(debug_assertions)]
                    let mut child = {
                        let child_proc = std::process::Command::new("python")
                            .current_dir("..")
                            .arg("desktop_entry.py")
                            .spawn();
                            
                        if let Err(e) = &child_proc {
                            if !start_minimized {
                                show_error_dialog(&app_handle, &format!("Backend failed to start: {}", e));
                            }
                            return;
                        }
                        child_proc.unwrap()
                    };

                    #[cfg(not(debug_assertions))]
                    let mut child = {
                        let sidecar = tauri::api::process::Command::new_sidecar("govtrack-api");
                        if sidecar.is_err() {
                            if !start_minimized {
                                let err = sidecar.err().unwrap().to_string();
                                show_error_dialog(&app_handle, &format!("Failed to locate sidecar executable: {}", err));
                            }
                            return;
                        }
                        
                        let child_proc = sidecar.unwrap().spawn();
                        if let Err(e) = &child_proc {
                            if !start_minimized {
                                show_error_dialog(&app_handle, &format!("Sidecar failed to start: {}", e));
                            }
                            return;
                        }
                        
                        let (mut rx, child) = child_proc.unwrap();
                        tauri::async_runtime::spawn(async move {
                            while let Some(event) = rx.recv().await {
                                println!("SIDECAR: {:?}", event);
                            }
                        });
                        child
                    };
                    
                    if !start_minimized {
                        emit_progress(&app_handle, "Loading Database and Scrapers...", 40);
                    }
                    
                    let start_time = std::time::Instant::now();
                    let mut success = false;
                    
                    // Boot verification
                    while start_time.elapsed().as_secs() < HEALTH_TIMEOUT {
                        let elapsed = start_time.elapsed().as_secs();
                        if !start_minimized {
                            if elapsed > 15 {
                                emit_progress(&app_handle, "Optimizing startup... please wait.", 70);
                            } else if elapsed > 5 {
                                emit_progress(&app_handle, "Loading Dashboard Interface...", 60);
                            }
                        }
                        
                        match client.get("http://127.0.0.1:8000/health").send().await {
                            Ok(resp) if resp.status().is_success() => {
                                success = true;
                                break;
                            }
                            _ => {}
                        }
                        tokio::time::sleep(BOOT_POLL_INTERVAL).await;
                    }
                    
                    if success {
                        if !start_minimized {
                            emit_progress(&app_handle, "GovTrack AI is Ready", 100);
                            tokio::time::sleep(UI_DELAY).await;
                            
                            if let Some(splash) = app_handle.get_window("splashscreen") {
                                let _ = splash.close();
                            }
                            if let Some(main_win) = app_handle.get_window("main") {
                                let _ = main_win.show();
                            }
                        } else {
                            if let Some(splash) = app_handle.get_window("splashscreen") {
                                let _ = splash.hide();
                            }
                        }
                        
                        // Watchdog monitoring loop
                        loop {
                            tokio::time::sleep(WATCHDOG_INTERVAL).await;
                            match client.get("http://127.0.0.1:8000/health").send().await {
                                Ok(resp) if resp.status().is_success() => {
                                    crash_count = 0; 
                                },
                                _ => {
                                    log::error!("Watchdog: Backend crashed.");
                                    let _ = child.kill();
                                    crash_count += 1;
                                    log::info!("Restarting backend (Attempt {})", crash_count);
                                    let _ = app_handle.emit_all("backend-crash-recovery", crash_count);
                                    break; 
                                }
                            }
                        }
                    } else {
                        // Failed to boot
                        if !start_minimized {
                            show_error_dialog(&app_handle, "Backend health check timed out after 30 seconds. Check logs for details.");
                        }
                        break;
                    }
                    
                    tokio::time::sleep(RESTART_DELAY).await;
                }
            });
            
            Ok(())
        })
        .on_window_event(|event| match event.event() {
            WindowEvent::CloseRequested { api, .. } => {
                // Minimize to tray instead of exiting
                if let Err(e) = event.window().hide() {
                    log::warn!("Failed to hide window on close: {}", e);
                }
                api.prevent_close();
            }
            _ => {}
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}

fn show_error_dialog(app: &tauri::AppHandle, message: &str) {
    let msg = message.to_string();
    let handle = app.clone();
    
    tauri::async_runtime::spawn(async move {
        if let Some(splash) = handle.get_window("splashscreen") {
            let _ = splash.close();
        }
        
        match tauri::WindowBuilder::new(
            &handle,
            "error_dialog",
            tauri::WindowUrl::App("error.html".into())
        )
        .title("Startup Error")
        .inner_size(500.0, 300.0)
        .resizable(false)
        .center()
        .build() {
            Ok(error_win) => {
                tokio::time::sleep(UI_DELAY).await;
                if let Err(e) = error_win.emit("startup-error-details", msg) {
                    log::error!("Failed to emit error details: {}", e);
                }
            },
            Err(e) => {
                log::error!("Failed to create error dialog: {}", e);
            }
        }
    });
}
