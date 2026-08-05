# GovTrack AI Build System

This document outlines the production build pipeline for GovTrack AI on Windows.

## Build Prerequisites

To compile the application, you need a Windows machine with the following installed:
- **Python 3.10+**: Must be in your system `PATH`.
- **Node.js 18+ & npm**: Required to build the frontend.
- **Rust & Cargo**: Required by Tauri (Install via `rustup`).
- **Tauri CLI**: Installed locally via npm or globally via Cargo.
- **Visual Studio Build Tools**: C++ build tools for compiling native extensions and Tauri UI wrapper.

## Build Steps

The build system is entirely automated and idempotent.

Run the PowerShell build script from the project root:
```powershell
.\build_windows.ps1
```

The script will automatically:
1. Clean previous artifacts.
2. Initialize and activate the Python virtual environment.
3. Validate all system dependencies.
4. Install and upgrade Python packages (`requirements.txt`).
5. Run PyInstaller using `govtrack.spec` to bundle the backend sidecar.
6. Verify the backend's health endpoint locally.
7. Install npm dependencies and build the frontend.
8. Compile the Tauri application.
9. Package everything into a standalone MSI installer.
10. Generate a detailed Build Report and logs.

## Troubleshooting

- **Python Not Found**: Ensure Python is added to your environment `PATH` variable.
- **Rust/Cargo Missing**: Install Rust from rustup.rs.
- **Backend Health Check Fails**: Check `logs/backend_test.log` for Uvicorn exceptions. Often caused by missing hidden imports. Update `govtrack.spec`.
- **MSI Build Fails**: Make sure you have WiX Toolset installed, though Tauri v1+ bundles it automatically for Windows.

## Release Process

1. Update the version in `package.json` and `src-tauri/tauri.conf.json`.
2. Run `.\build_windows.ps1`.
3. Locate the MSI installer in `src-tauri/target/release/bundle/msi/`.
4. Create a new Release on GitHub matching the version (e.g. `v1.0.0`).
5. Upload the MSI to the release assets.
6. The Tauri auto-updater will automatically detect the new version for existing users.

## Adding New Features (Scrapers, Models, etc.)

The build script `build_windows.ps1` should **never** be manually modified for regular changes.

To bundle new resources (e.g., a new data folder, a new scraper config directory), simply edit the `datas` array in `govtrack.spec` and re-run the build script. To add new dependencies that PyInstaller misses, add them to `hiddenimports` in `govtrack.spec`.
