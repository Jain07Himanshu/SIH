from typing import Any
from pydantic import BaseModel, Field

class OverviewAnalytics(BaseModel):
    total_complaints: int = 0
    unique_issues: int = 0
    duplicate_complaints: int = 0
    duplicate_rate: float = 0.0
    average_cluster_size: float = 0.0
    high_priority_issues: int = 0
    needs_review_count: int = 0

class CategoryAnalyticsItem(BaseModel):
    category_id: str
    category_name: str
    complaints: int = 0
    issues: int = 0
    duplicate_rate: float = 0.0
    department_id: str | None = None
    dominant_priority: str = "MEDIUM"

class DepartmentAnalyticsItem(BaseModel):
    department_id: str
    department_name: str
    complaints: int = 0
    unique_issues: int = 0
    high_priority_issues: int = 0
    duplicate_rate: float = 0.0
    average_issue_size: float = 0.0

class TrendDataPoint(BaseModel):
    period: str
    complaint_count: int = 0
    issue_count: int = 0
    duplicate_count: int = 0

class TrendAnalytics(BaseModel):
    interval: str = "daily"
    trends: list[TrendDataPoint] = Field(default_factory=list)

class HotspotRecord(BaseModel):
    hotspot_id: str
    category: str
    issue_count: int = 0
    complaint_count: int = 0
    center: dict[str, float] = Field(default_factory=dict)
    radius_meters: float = 0.0
    priority: str = "HIGH"
    dominant_keywords: list[str] = Field(default_factory=list)

class HotspotListResponse(BaseModel):
    total_hotspots: int = 0
    hotspots: list[HotspotRecord] = Field(default_factory=list)
