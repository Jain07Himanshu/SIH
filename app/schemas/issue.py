from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field

class LocationSummary(BaseModel):
    latitude: float
    longitude: float
    radius_meters: float = 0.0
    bounding_box: dict[str, float] = Field(default_factory=dict)
    geographic_concentration: str = "Unknown"

class PrioritySummary(BaseModel):
    high_count: int = 0
    medium_count: int = 0
    low_count: int = 0
    unspecified_count: int = 0
    dominant_priority: str = "MEDIUM"
    average_priority_score: float = 2.0

class TimeSummary(BaseModel):
    earliest_timestamp: datetime
    latest_timestamp: datetime
    span_days: float = 0.0

class IssueRecord(BaseModel):
    issue_id: str
    title: str
    category: Any | None = None  # CategoryPrediction | None
    department: Any | None = None  # DepartmentRecord | None
    keywords: list[str] = Field(default_factory=list)
    representative_complaint_id: str
    complaint_ids: list[str] = Field(default_factory=list)
    complaint_count: int = 1
    duplicate_count: int = 0
    similarity_score: float = 1.0
    location: LocationSummary | None = None
    priority_summary: PrioritySummary = Field(default_factory=PrioritySummary)
    status_summary: dict[str, int] = Field(default_factory=dict)
    time_summary: TimeSummary | None = None
    needs_review: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class IssueMergeRequest(BaseModel):
    target_issue_id: str
    source_issue_id: str
    reason: str | None = None

class IssueSplitRequest(BaseModel):
    parent_issue_id: str
    complaint_ids: list[str]
    new_issue_title: str | None = None
    reason: str | None = None

class IssueOperationResponse(BaseModel):
    success: bool
    message: str
    affected_issue_ids: list[str] = Field(default_factory=list)
    resulting_issues: list[IssueRecord] = Field(default_factory=list)
