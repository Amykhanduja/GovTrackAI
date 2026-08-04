# GovTrack AI Architecture

```mermaid
graph TD
    A[Scraper Plugins] -->|Raw HTML/PDF| B(AI Processing Pipeline)
    B -->|Skills/Eligibility| C[(SQLite DB WAL)]
    C --> D[Excel Engine]
    C --> E[FastAPI REST API]
    E --> F[Web Dashboard]
    E --> G[Automation / Schedulers]
    G --> H[Notification Engine]
```
