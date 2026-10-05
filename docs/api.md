# REST API Reference Manual

Base URL: `http://localhost:8000/api/v1`

## Ingestion & Analysis

### `POST /analyze`
Analyzes a single complaint in real time.
```json
{
  "complaint_id": "CMP-001",
  "text": "Deep dangerous pothole near railway station causing bike accidents",
  "category": "ROAD_POTHOLE",
  "priority": "HIGH",
  "latitude": 28.6139,
  "longitude": 77.2090,
  "timestamp": "2026-09-01T10:00:00Z"
}
```

### `POST /similarity/compare`
Compares two complaints across all 6 similarity dimensions.

### `GET /issues`
Lists canonical issues with optional filters (`category_id`, `department_id`, `dominant_priority`).

### `POST /issues/merge`
Merges two canonical issues.

### `POST /issues/split`
Splits selected complaints from a canonical issue into a new issue.

### `GET /analytics/overview`
Returns high-level platform statistics including duplicate reduction percentage.

### `GET /analytics/hotspots`
Returns GIS hotspot clusters with coordinates, radius, and dominant categories.
