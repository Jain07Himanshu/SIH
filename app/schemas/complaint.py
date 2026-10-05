import uuid
from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field

class KeywordItem(BaseModel):
    term: str
    score: float = 1.0
    type: str = "issue" # "issue" | "location" | "impact" | "temporal"

class TextRepresentation(BaseModel):
    original: str
    clean: str
    semantic: str
    keyword: str

class ComplaintInput(BaseModel):
    complaint_id: str | None = None
    text: str
    category: str | None = None
    department: str | None = None
    priority: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    timestamp: datetime | None = None
    source: str | None = "WEB"
    metadata: dict[str, Any] | None = None

    def to_record(self) -> "ComplaintRecord":
        return ComplaintRecord(
            complaint_id=self.complaint_id or f"CMP-{uuid.uuid4().hex[:8].upper()}",
            text=self.text,
            category=self.category,
            department=self.department,
            priority=self.priority,
            latitude=self.latitude,
            longitude=self.longitude,
            timestamp=self.timestamp or datetime.utcnow(),
            source=self.source,
            metadata=self.metadata or {}
        )

class ComplaintRecord(BaseModel):
    complaint_id: str
    text: str
    category: str | None = None
    department: str | None = None
    priority: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    timestamp: datetime | None = None
    source: str | None = "WEB"
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class NormalizedComplaint(BaseModel):
    complaint_id: str
    raw_record: ComplaintRecord
    text: TextRepresentation
    tokens: list[str] = Field(default_factory=list)
    language: str = "en"
    language_confidence: float = 1.0
    keywords: list[KeywordItem] = Field(default_factory=list)

class BatchProcessingReport(BaseModel):
    job_id: str
    total: int
    successful: int
    failed: int
    duration_seconds: float
    errors: list[dict[str, Any]] = Field(default_factory=list)
