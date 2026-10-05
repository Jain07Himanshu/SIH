import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_normalization_endpoint():
    # Test colloquial Hindi/Hinglish text normalization
    res = client.post("/api/v1/complaints/normalize", json={
        "text": "Bohot bada khadda hai sadak pe and paani leakage ho raha hai call 9876543210"
    })
    assert res.status_code == 200
    data = res.json()
    assert "pothole" in data["canonical_text"] or "water" in data["canonical_text"] or "pothole" in data["tokens"]
    assert len(data["tokens"]) > 0
    assert "9876543210" not in data["clean"]  # PII redacted

def test_tracking_and_gis_map_flow():
    # 1. Create a complaint
    res_create = client.post("/api/v1/complaints", json={
        "category": "roads",
        "description": "Deep dangerous pothole near railway crossing causing two wheeler accidents.",
        "locality": "Borivali West",
        "ward": "Ward R-Central",
        "landmark": "Near Railway Crossing",
        "priority": "high",
        "latitude": 19.2307,
        "longitude": 72.8567
    })
    assert res_create.status_code == 201
    created = res_create.json()
    cid = created["complaint_id"]
    assert cid.startswith("SS-")

    # 2. Track complaint
    res_track = client.get(f"/api/v1/complaints/track/{cid}")
    assert res_track.status_code == 200
    track_info = res_track.json()
    assert track_info["complaint_id"] == cid
    assert track_info["stage_index"] == 0
    assert track_info["stage_label"] == "Submitted"
    assert "Roads" in track_info["category_name"]
    assert track_info["locality"] == "Borivali West"

    # 3. Verify on GIS Map API
    res_map = client.get("/api/v1/authority/complaints/map")
    assert res_map.status_code == 200
    map_data = res_map.json()
    complaint_ids = [c["complaint_id"] for c in map_data["complaints"]]
    assert cid in complaint_ids

    # 4. Update status via Authority Officer Action
    res_update = client.patch(f"/api/v1/authority/complaints/{cid}/status", json={
        "status": "IN_PROGRESS",
        "comment": "Road repair contractor dispatched with asphalt mixer"
    })
    assert res_update.status_code == 200

    # 5. Verify tracking reflects step 2 (In Progress)
    res_track_updated = client.get(f"/api/v1/complaints/track/{cid}")
    assert res_track_updated.status_code == 200
    updated_track = res_track_updated.json()
    assert updated_track["stage_index"] == 2
    assert updated_track["stage_label"] == "In Progress"
    assert len(updated_track["history"]) >= 2
