from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Any
from datetime import datetime

class ComplaintCreateRequest(BaseModel):
    category: str = Field(..., description="Civic category code e.g. roads, garbage, water")
    description: str = Field(..., min_length=5, description="Full grievance text")
    locality: str = Field(..., description="Locality or area name")
    ward: Optional[str] = None
    landmark: Optional[str] = None
    priority: Optional[str] = "medium"
    is_anonymous: bool = False
    full_name: Optional[str] = None
    phone: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    image_url: Optional[str] = None

class StatusHistoryItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    old_status: str
    new_status: str
    changed_by: Optional[str] = None
    comment: Optional[str] = None
    timestamp: datetime

class ComplaintDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    complaint_id: str
    citizen_id: Optional[str] = None
    text: str
    clean_text: Optional[str] = None
    category_id: Optional[str] = None
    category_name: Optional[str] = None
    department_id: Optional[str] = None
    department_name: Optional[str] = None
    locality: Optional[str] = None
    ward: Optional[str] = None
    landmark: Optional[str] = None
    priority: str = "MEDIUM"
    status: str = "SUBMITTED"
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    image_url: Optional[str] = None
    is_anonymous: bool = False
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None
    timestamp: Optional[datetime] = None
    created_at: Optional[datetime] = None
    matched_issue_id: Optional[str] = None
    matched_complaint_id: Optional[str] = None
    duplicate_status: Optional[str] = None
    similarity_score: Optional[float] = None
    match_type: Optional[str] = None
    confidence: Optional[float] = None
    status_history: list[StatusHistoryItem] = []
    history: list[StatusHistoryItem] = []

class ComplaintTrackResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    complaint_id: str
    category_name: str
    locality: str
    landmark: Optional[str] = None
    filed_date: str
    department_name: str
    status: str
    stage_index: int  # 0=submitted, 1=assigned, 2=progress, 3=resolved
    stage_label: str
    status_note: str
    is_duplicate: bool = False
    linked_issue_id: Optional[str] = None
    history: list[StatusHistoryItem] = []
    status_history: list[StatusHistoryItem] = []

class StatusUpdateRequest(BaseModel):
    status: str = Field(..., description="New status e.g. ASSIGNED, IN_PROGRESS, RESOLVED, REJECTED")
    comment: Optional[str] = None

class MapComplaintItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    complaint_id: str
    text: str
    category: str
    category_name: str
    status: str
    priority: str
    latitude: float
    longitude: float
    locality: Optional[str] = None
    created_at: datetime
    cluster_id: Optional[int] = None
    issue_id: Optional[str] = None

class MapComplaintsResponse(BaseModel):
    total: int
    complaints: list[MapComplaintItem]
