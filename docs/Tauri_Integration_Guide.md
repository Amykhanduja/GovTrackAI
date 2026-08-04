# Desktop Application Architecture (Tauri)

## Overview
GovTrack AI has been wrapped into a native Desktop Application using **Tauri** (Rust + WebView).
The desktop app acts as a highly optimized Orchestrator that manages the FastAPI background processes and renders the Glassmorphism frontend in a native window.

## Process Management
- **Sidecar Execution**: The Rust backend (`src/main.rs`) spawns `desktop_entry.py` (the FastAPI server) as a managed child process.
- **Crash Recovery**: Tauri monitors the child process `stdout`. If the backend crashes, Tauri can automatically restart the sidecar.
- **Graceful Shutdown**: When the user exits via the System Tray, Tauri sends a SIGTERM to the FastAPI sidecar, ensuring the SQLite WAL database writes are safely flushed before exiting.
- **Port Security**: FastAPI is strictly bound to `127.0.0.1`, preventing external access on the local network.

## Background Mode & System Tray
When the user clicks the 'X' to close the window, the `WindowEvent::CloseRequested` event is intercepted. The application prevents termination and instead calls `.hide()`, dropping into **Background Mode**.
The System Tray (`src/tray.rs`) provides quick access to force scrapers, export Excel, and reopen the Dashboard.

## Native Notifications
The Automation Engine can trigger Tauri's native OS notifications (Windows/macOS/Linux) to alert the user of critical deadlines, scraper failures, or high-priority job discoveries.

## Building for Production
1. Compile the FastAPI backend into a single executable using `PyInstaller`.
2. Move the executable to `src-tauri/bin/govtrack-api-x86_64-pc-windows-msvc.exe`.
3. Run `npm run tauri build`.
Tauri will bundle the Rust orchestrator, the UI, and the Python backend into a single portable `.msi` or `.AppImage`.
