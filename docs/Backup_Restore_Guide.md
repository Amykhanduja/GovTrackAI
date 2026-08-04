# Backup and Restore
GovTrack AI manages automated backups of your SQLite database and configuration files.

## Creating a Manual Backup
From the System Tray, select `Configuration -> Export Backup`. A timestamped folder will be created in `%APPDATA%/GovTrackAI/backups/`.

## Restoring
Simply close GovTrack AI, navigate to the backup folder, and replace `govtrack.sqlite` and the `config/` directory in your primary data path. Restart the application.
