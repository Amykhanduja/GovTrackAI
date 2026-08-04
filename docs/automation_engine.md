# Automation & Notification Engine

## Overview
GovTrack AI uses an autonomous execution environment designed to run invisibly in the background. It orchestrates Scrapers, AI Pipelines, and Excel Generators on strict schedules while proactively managing system health and backups.

## Architecture
- **`TaskScheduler`**: Independently queues and tracks interval-based cron tasks (Hourly, Daily, Weekly). Includes failure isolation and historical execution logs.
- **`AutomationEngine`**: The master orchestrator that stitches together Scrapers -> AI Pipeline -> DB Cleanup -> Excel Engine.
- **`HealthMonitor` & `BackupManager`**: Ensures Database integrity and copies `.sqlite` backups timestamped before every major execution cycle.
- **`NotificationEngine`**: A Dependency-Injected provider framework (Desktop, Telegram, Slack, Webhook). 
- **`ReminderSystem`**: Evaluates upcoming deadlines (30, 15, 7, 3, 1 day marks) and routes urgent alerts through the Notification Engine.

## Fault Tolerance
If a single scraper organization crashes, the Automation Engine isolates the fault, logs the stack trace, and proceeds with the remaining organizations.
