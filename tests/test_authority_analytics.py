import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_overview_kpis():
    response = client.get("/api/v1/authority/analytics/overview")
    assert response.status_code == 200
    data = response.json()
    assert "total_complaints" in data
    assert "pending_complaints" in data
    assert "in_progress_complaints" in data
    assert "resolved_complaints" in data
    assert "active_clusters" in data
    assert "noise_reduction_pct" in data
    assert isinstance(data["total_complaints"], int)
    assert data["total_complaints"] >= 0

def test_category_analytics():
    response = client.get("/api/v1/authority/analytics/categories")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        cat = data[0]
        assert "category" in cat
        assert "count" in cat
        assert "percentage" in cat
        assert "color" in cat
        assert cat["percentage"] >= 0.0

def test_trend_analytics():
    response = client.get("/api/v1/authority/analytics/trends?days=14")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 14
    for day in data:
        assert "date" in day
        assert "day_label" in day
        assert "count" in day
        assert day["count"] >= 0

def test_department_workload():
    response = client.get("/api/v1/authority/analytics/departments")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        dept = data[0]
        assert "department" in dept
        assert "open_issues" in dept
        assert "total_complaints" in dept

def test_map_complaints_gis():
    response = client.get("/api/v1/authority/complaints/map")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "complaints" in data
    assert isinstance(data["complaints"], list)
    if data["total"] > 0:
        c = data["complaints"][0]
        assert "complaint_id" in c
        assert "latitude" in c
        assert "longitude" in c
        assert "category" in c
        assert "status" in c

def test_clusters_list():
    response = client.get("/api/v1/authority/clusters")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        cl = data[0]
        assert "id" in cl
        assert "title" in cl
        assert "count" in cl
        assert "confidence" in cl
        assert "complaints" in cl
        assert isinstance(cl["complaints"], list)
