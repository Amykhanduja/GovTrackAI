# GovTrack AI
> The Multi-Domain Intelligent Government Recruitment Platform

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)

GovTrack AI is a production-grade, native desktop application designed to automate the aggregation, tracking, and AI-driven analysis of hundreds of official government recruitment portals across India.

## ✨ Features
- **Multi-Domain Ecosystem**: Simultaneously track Cyber Security, Technology, and Foreign Language careers in isolated dashboards.
- **Native Desktop Application**: Built on Tauri (Rust) for minimal footprint and maximum performance. Runs silently in your System Tray.
- **AI Intelligence**: Powered by RAG and semantic search to automatically classify your eligibility against highly complex PDFs.
- **Excel Business Intelligence**: Exports interactive PowerBI-style dashboards instantly.
- **Portable Mode Support**: Run directly from a USB stick without installation.
- **Offline Data**: 100% of your data (SQLite DB, Logs, Configs) lives securely on your local machine (`%APPDATA%/GovTrackAI`).

## 🚀 Quick Start (For Users)
1. Head to the **Releases** tab.
2. Download `GovTrack_AI_1.0.0.msi`.
3. Run the installer.
4. Launch the application. The **Setup Wizard** will guide you through selecting your preferred domains.

## 🛠 Compilation (For Developers)
To compile the standalone binaries and installer from source:
```powershell
./build_windows.ps1
```

## 📚 Documentation
- [Installation Guide](docs/Installation_Guide.md)
- [Backup & Restore Guide](docs/Backup_Restore_Guide.md)
- [Architecture Guide](docs/MultiDomain_Architecture.md)
