from typing import Any
from pydantic import BaseModel, Field

class ClusterRecord(BaseModel):
    cluster_id: int | None = None
    complaint_ids: list[str] = Field(default_factory=list)
    size: int = 1
    representative_complaint_id: str
    representative_keywords: list[str] = Field(default_factory=list)
    category_id: str | None = None
    is_noise: bool = False
    centroid_similarity: float = 1.0

class ClusterSummary(BaseModel):
    total_clusters: int = 0
    clustered_complaints: int = 0
    noise_complaints: int = 0
    clusters: list[ClusterRecord] = Field(default_factory=list)
