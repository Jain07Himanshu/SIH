from typing import Any
from pydantic import BaseModel

class SimilarityComponents(BaseModel):
    semantic_similarity: float = 0.0
    lexical_similarity: float = 0.0
    keyword_similarity: float = 0.0
    category_similarity: float = 0.0
    geographic_similarity: float | None = None
    temporal_similarity: float | None = None

class MatchExplanation(BaseModel):
    semantic_match: str = ""
    shared_keywords: list[str] = []
    same_category: bool = False
    distance_meters: float | None = None
    location_match: bool = False
    temporal_gap_days: float | None = None
    summary: str = ""

class MatchEvidence(BaseModel):
    match_type: str  # "DUPLICATE" | "POSSIBLY_SIMILAR" | "NEW_ISSUE"
    confidence: float
    explanation: MatchExplanation
    needs_review: bool = False

class SimilarityMatchResult(BaseModel):
    complaint_id: str
    matched_complaint_id: str
    similarity_score: float
    match_type: str
    components: SimilarityComponents
    evidence: MatchEvidence

class SimilarityCompareInput(BaseModel):
    text: str
    category: str | None = None
    priority: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    timestamp: str | None = None

class SimilarityCompareRequest(BaseModel):
    complaint_a: SimilarityCompareInput
    complaint_b: SimilarityCompareInput

class SimilarityCompareResponse(BaseModel):
    similarity_score: float
    match_type: str
    components: SimilarityComponents
    evidence: MatchEvidence
