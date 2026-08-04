# Excel Reporting Engine

## Architecture
GovTrack AI automatically builds a polished Microsoft Excel dashboard natively pulling from the SQLite source of truth.

## Modules
1. **`DataProvider`**: Connects via SQLAlchemy to fetch, join, aggregate and structure data.
2. **`FormattingEngine`**: Centralizes styling (colors, borders, conditional formatting thresholds).
3. **`ChartEngine`**: Generates XlsxWriter chart objects for Pie, Bar, Column, Line, Area graphs.
4. **`ExcelEngine`**: The orchestrator. Constructs the multi-sheet workbook, links the charts to hidden data sheets, and applies the formats.

## Updating the Dashboard
Do not edit the Excel file directly as a database. It is a one-way export from SQLite. To regenerate it, invoke `ExcelEngine.generate()`.
