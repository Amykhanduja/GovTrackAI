# GovTrack AI - API Guide
The FastAPI application provides a fully typed REST interface.
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Endpoints
- `GET /api/v1/jobs` - Paginated job list. Supports `?search=` filtering.
- `GET /api/v1/analytics` - Returns JSON representation of KPIs.
- `GET /api/v1/profile` - Returns JSON User profile configurations.
