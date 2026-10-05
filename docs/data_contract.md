# Data Contract & Schemas

## Canonical Complaint Schema
```json
{
  "complaint_id": "string (unique)",
  "text": "string (non-empty raw description)",
  "category": "string (optional category id)",
  "priority": "HIGH | MEDIUM | LOW | null",
  "latitude": "float | null",
  "longitude": "float | null",
  "timestamp": "ISO-8601 datetime | null",
  "source": "MOBILE_APP | WEB_PORTAL | CALL_CENTER | TWITTER | null",
  "metadata": "object | null"
}
```

## Canonical Issue Schema
```json
{
  "issue_id": "string (unique ISS-XXX)",
  "title": "string (evidence-generated concise title)",
  "category": { "category_id": "string", "category_name": "string", "confidence": 0.95 },
  "department": { "id": "string", "name": "string" },
  "keywords": ["pothole", "railway station", "accidents"],
  "representative_complaint_id": "CMP-001",
  "complaint_ids": ["CMP-001", "CMP-002", "CMP-003"],
  "complaint_count": 3,
  "duplicate_count": 2,
  "similarity_score": 0.91,
  "location": {
    "latitude": 28.6140,
    "longitude": 77.2091,
    "radius_meters": 14.5,
    "geographic_concentration": "High"
  },
  "priority_summary": {
    "high_count": 3,
    "medium_count": 0,
    "low_count": 0,
    "dominant_priority": "HIGH",
    "average_priority_score": 3.0
  }
}
```
