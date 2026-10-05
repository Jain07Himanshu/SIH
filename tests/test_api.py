from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoint():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"

def test_analyze_single():
    payload = {
        "text": "Huge pothole near railway station causing severe traffic",
        "category": "ROAD_POTHOLE",
        "priority": "HIGH",
        "latitude": 28.6139,
        "longitude": 77.2090
    }
    resp = client.post("/api/v1/analyze", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "assigned_issue" in data
    assert data["assigned_issue"]["priority_summary"]["dominant_priority"] == "HIGH"

def test_similarity_compare():
    payload = {
        "complaint_a": {"text": "Large pothole on road near station", "category": "ROAD_POTHOLE"},
        "complaint_b": {"text": "Big deep road crater near station", "category": "ROAD_POTHOLE"}
    }
    resp = client.post("/api/v1/similarity/compare", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "similarity_score" in data
    assert data["similarity_score"] >= 0.50
    assert data["match_type"] in ("DUPLICATE", "POSSIBLY_SIMILAR")

def test_categories_endpoint():
    resp = client.get("/api/v1/categories")
    assert resp.status_code == 200
    assert len(resp.json()) >= 5
