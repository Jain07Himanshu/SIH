import pytest
import uuid
from fastapi.testclient import TestClient
from app.main import app
from app.db.session import init_db

@pytest.fixture(scope="module", autouse=True)
def setup_database():
    init_db()

@pytest.fixture
def client():
    return TestClient(app)

def test_full_civic_lifecycle(client):
    suffix = uuid.uuid4().hex[:6]
    # 1. Register Citizen
    cit_email = f"citizen_{suffix}@example.com"
    res_cit_reg = client.post("/api/v1/auth/register/citizen", json={
        "name": "Pooja Sharma",
        "email": cit_email,
        "password": "password123"
    })
    assert res_cit_reg.status_code == 201
    cit_token = res_cit_reg.json()["access_token"]
    assert cit_token is not None

    # 2. Login Citizen
    res_cit_login = client.post("/api/v1/auth/login", json={
        "email": cit_email,
        "password": "password123",
        "role": "citizen"
    })
    assert res_cit_login.status_code == 200
    assert res_cit_login.json()["user"]["email"] == cit_email

    # 3. Register Authority
    auth_email = f"officer_{suffix}@gov.in"
    res_auth_reg = client.post("/api/v1/auth/register/authority", json={
        "name": "Officer Verma",
        "designation": "Ward Officer",
        "department": "Public Works Department",
        "employeeId": f"PWD-{suffix}",
        "email": auth_email,
        "phone": "9876543210",
        "password": "password123"
    })
    assert res_auth_reg.status_code == 201
    auth_token = res_auth_reg.json()["access_token"]
    assert auth_token is not None

    # 4. Login Authority
    res_auth_login = client.post("/api/v1/auth/login", json={
        "email": auth_email,
        "password": "password123",
        "role": "authority"
    })
    assert res_auth_login.status_code == 200
    assert res_auth_login.json()["user"]["role"] == "AUTHORITY"

    # 5. File Complaint 1 (Pothole at MG Road)
    res_c1 = client.post("/api/v1/complaints", json={
        "category": "roads",
        "description": "Large dangerous pothole on MG Road near city hospital causing traffic jams.",
        "locality": "Andheri West",
        "ward": "Ward 12",
        "landmark": "Near City Hospital",
        "priority": "high",
        "is_anonymous": False,
        "full_name": "Pooja Sharma",
        "phone": "9876543210",
        "latitude": 19.1136,
        "longitude": 72.8697
    }, headers={"Authorization": f"Bearer {cit_token}"})

    assert res_c1.status_code == 201
    c1_data = res_c1.json()
    c1_id = c1_data["complaint_id"]
    assert c1_id.startswith("SS-")
    assert c1_data["status"] == "SUBMITTED"

    # 6. Track Complaint 1
    res_track = client.get(f"/api/v1/complaints/track/{c1_id}")
    assert res_track.status_code == 200
    track_data = res_track.json()
    assert track_data["complaint_id"] == c1_id
    assert track_data["stage_index"] == 0
    assert "Roads" in track_data["category_name"]

    # 7. File Complaint 2 (Duplicate pothole complaint at same MG road location)
    res_c2 = client.post("/api/v1/complaints", json={
        "category": "roads",
        "description": "Severe deep pothole at MG Road junction near hospital, 2 wheelers slipping.",
        "locality": "Andheri West",
        "ward": "Ward 12",
        "landmark": "City Hospital MG Road",
        "priority": "high",
        "is_anonymous": True,
        "latitude": 19.1137,
        "longitude": 72.8698
    })
    assert res_c2.status_code == 201
    c2_data = res_c2.json()
    c2_id = c2_data["complaint_id"]
    assert c2_id.startswith("SS-")
    # AI Duplicate engine should assign/link this
    assert c2_data["is_duplicate"] is True or c2_data["matched_issue_id"] is not None

    # 8. Authority Map & Clusters check
    res_map = client.get("/api/v1/authority/complaints/map")
    assert res_map.status_code == 200
    map_data = res_map.json()
    assert map_data["total"] >= 2

    res_clusters = client.get("/api/v1/authority/clusters")
    assert res_clusters.status_code == 200
    clusters = res_clusters.json()
    assert len(clusters) >= 1

    # 9. Authority update status of Complaint 1
    res_update = client.patch(f"/api/v1/authority/complaints/{c1_id}/status", json={
        "status": "IN_PROGRESS",
        "comment": "Road repair team dispatched to MG Road"
    }, headers={"Authorization": f"Bearer {auth_token}"})
    assert res_update.status_code == 200
    assert res_update.json()["status"] == "IN_PROGRESS"

    # 10. Re-track Complaint 1 to verify status updated to stage 2 (In Progress)
    res_track_updated = client.get(f"/api/v1/complaints/track/{c1_id}")
    assert res_track_updated.status_code == 200
    assert res_track_updated.json()["stage_index"] == 2
    assert res_track_updated.json()["stage_label"] == "In Progress"
