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
            
            let (mut rx, child) = Command::new_sidecar("govtrack-api")
                .expect("Failed to create sidecar command")
                .spawn()
                .expect("Failed to spawn FastAPI backend sidecar");
                
            app.manage(child);
            
            // Listen to Backend Logs
            tauri::async_runtime::spawn(async move {
                let mut started = false;
                while let Some(event) = rx.recv().await {
                    match event {
                        CommandEvent::Stdout(line) => {
                            println!("API Log: {}", line);
                            if !started && line.contains("Application startup complete") {
                                started = true;
                                window.show().unwrap();
                            }
                        }
                        CommandEvent::Stderr(line) => {
                            eprintln!("API Error: {}", line);
                        }
                        CommandEvent::Error(err) => {
                            eprintln!("Sidecar Error: {}", err);
                        }
                        CommandEvent::Terminated(payload) => {
                            eprintln!("Sidecar Terminated: {:?}", payload);
                            std::process::exit(1);
                        }
                        _ => {}
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
