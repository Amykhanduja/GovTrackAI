#![cfg_attr(
  all(not(debug_assertions), target_os = "windows"),
  windows_subsystem = "windows"
)]

mod tray;
use tauri::{Manager, SystemTray, SystemTrayEvent, WindowEvent};
use tauri::api::process::{Command, CommandEvent};
use std::sync::{Arc, Mutex};

fn main() {
    let tray = tray::create_tray();

    tauri::Builder::default()
        .system_tray(tray)
        .on_system_tray_event(|app, event| {
            tray::handle_tray_event(app, event);
        })
        .setup(|app| {
            // Launch the FastAPI Backend as a Sidecar Process
            let window = app.get_window("main").unwrap();
            
            // In a real build, we would use sidecar("govtrack-api"). 
            // For development, we spawn Python.
            let (mut rx, child) = Command::new("python3")
                .args(vec!["../desktop_entry.py"])
                .spawn()
                .expect("Failed to spawn FastAPI backend");
                
            let child_arc = Arc::new(Mutex::new(child));
            
            // Listen to Backend Logs
            tauri::async_runtime::spawn(async move {
                while let Some(event) = rx.recv().await {
                    if let CommandEvent::Stdout(line) = event {
                        println!("API Log: {}", line);
                        if line.contains("Application startup complete") {
                            // Show window once API is ready
                            window.show().unwrap();
                        }
                    }
                }
            });
            
            Ok(())
        })
        .on_window_event(|event| match event.event() {
            // Intercept window close and hide to system tray instead (Background Mode)
            WindowEvent::CloseRequested { api, .. } => {
                event.window().hide().unwrap();
                api.prevent_close();
            }
            _ => {}
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
