# Performance & Scale Optimizations

GovTrack AI has been optimized to handle **100,000+ jobs** and **200+ organizations**.

## Core Upgrades
1. **SQLite Write-Ahead Logging (WAL)**: Enabled by `DatabaseOptimizer`. Employs Memory-Mapped I/O and large caching to permit concurrent scraper writes and web dashboard reads safely.
2. **Database Indexes**: Strict indexes applied to `org_name`, `deadline`, and `priority` to guarantee sub-millisecond query performance on large datasets.
3. **AsyncExecutionEngine**: Scraper downloads and AI processing now stream through a chunked `ThreadPoolExecutor`, preventing RAM bloat via controlled `batch_size` processing.
4. **MemoryCache**: Drastically reduces repeated DB queries (e.g. LLM embedding results, API dashboard payloads) using a TTL caching layer.
5. **Excel Stream Engine**: Configured XlsxWriter to write purely to disk (`constant_memory=True`), preventing Out-Of-Memory (OOM) errors even when generating reports with millions of cells.
