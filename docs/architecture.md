# GovTrack AI Architecture

## Folder Structure
- core/: Engine orchestration and exceptions.
- config/: YAML configuration and manager.
- db/: Database models and connections.
- scrapers/: Plugin-based scraper framework.
- parsers/: Extractor framework for various file types.
- ai/: Interfaces for LLM integration.
- excel/: Excel generation and formatting.
- notifications/: Alerting channels.
- scheduler/: Job scheduling.
- logger/: Structured rotating logs.
- storage/: Downloads and caching.
- utils/: Reusable helpers.
- tests/: Project testing framework.

## Data Models
Standardized models across the app: Job, Organization, Application, Exam, Notification, DownloadedFile, AISummary.

## Extension Points
- Add a new scraper in `scrapers/plugins/`
- Add a new notification channel in `notifications/channels/`
- Implement AI interfaces in `ai/`
