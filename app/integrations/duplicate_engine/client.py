import os
import httpx
from typing import Optional, Any
from app.core.logging import get_logger
from app.schemas.complaint import ComplaintRecord
from app.services.pipeline import GrievanceIntelligencePipeline

logger = get_logger("duplicate_engine_client")

class DuplicateEngineClient:
    def __init__(self):
        self.engine_url = os.environ.get("DUPLICATE_ENGINE_URL", "").strip()
        self.timeout = float(os.environ.get("DUPLICATE_ENGINE_TIMEOUT", "5.0"))
        self._local_pipeline: Optional[GrievanceIntelligencePipeline] = None

    def _get_local_pipeline(self) -> GrievanceIntelligencePipeline:
        if self._local_pipeline is None:
            self._local_pipeline = GrievanceIntelligencePipeline()
        return self._local_pipeline

    def analyze_complaint(self,
                          complaint_id: str,
                          text: str,
                          category: Optional[str] = None,
                          priority: Optional[str] = None,
                          latitude: Optional[float] = None,
                          longitude: Optional[float] = None,
                          timestamp: Optional[str] = None) -> dict[str, Any]:
        if self.engine_url:
            try:
                payload = {
                    "complaint_id": complaint_id,
                    "text": text,
                    "category": category,
                    "priority": priority,
                    "latitude": latitude,
                    "longitude": longitude,
                    "timestamp": timestamp
                }
                with httpx.Client(timeout=self.timeout) as client:
                    resp = client.post(f"{self.engine_url}/api/v1/analyze", json=payload)
                    if resp.status_code == 200:
                        return resp.json()
                    logger.warning(f"Duplicate engine returned status {resp.status_code}, falling back to local engine")
            except Exception as e:
                logger.error(f"Duplicate engine HTTP error: {e}, falling back to local pipeline")

        # In-process direct AI pipeline execution (zero network overhead, 100% reliable)
        try:
            pipeline = self._get_local_pipeline()
            record = ComplaintRecord(
                complaint_id=complaint_id,
                text=text,
                category=category,
                priority=priority or "MEDIUM",
                latitude=latitude,
                longitude=longitude
            )
            norm_complaint, best_match, target_issue = pipeline.process_single(record)

            is_duplicate = False
            if best_match and best_match.match_type in ("DUPLICATE", "POSSIBLY_SIMILAR"):
                is_duplicate = True
            
            assigned_issue_dict = None
            if target_issue:
                assigned_issue_dict = {
                    "issue_id": target_issue.issue_id,
                    "title": target_issue.title,
                    "category_id": target_issue.category.category_id if target_issue.category else None,
                    "department_id": target_issue.department.id if target_issue.department else None,
                    "complaint_count": target_issue.complaint_count,
                    "duplicate_count": target_issue.duplicate_count,
                    "similarity_score": target_issue.similarity_score,
                    "dominant_priority": target_issue.priority_summary.dominant_priority
                }

            best_match_dict = None
            if best_match:
                explanation_data = None
                if hasattr(best_match.evidence.explanation, "model_dump"):
                    explanation_data = best_match.evidence.explanation.model_dump()
                elif hasattr(best_match.evidence.explanation, "dict"):
                    explanation_data = best_match.evidence.explanation.dict()
                else:
                    explanation_data = str(best_match.evidence.explanation)

                best_match_dict = {
                    "matched_complaint_id": best_match.matched_complaint_id,
                    "similarity_score": best_match.similarity_score,
                    "match_type": best_match.match_type,
                    "confidence": best_match.evidence.confidence,
                    "explanation": explanation_data
                }

            return {
                "complaint_id": complaint_id,
                "is_duplicate": is_duplicate,
                "best_match": best_match_dict,
                "assigned_issue": assigned_issue_dict,
                "predicted_category": norm_complaint.raw_record.category,
                "status": "PROCESSED"
            }
        except Exception as ex:
            logger.error(f"In-process duplicate engine error: {ex}")
            return {
                "complaint_id": complaint_id,
                "is_duplicate": False,
                "best_match": None,
                "assigned_issue": None,
                "status": "PENDING_AI",
                "error": str(ex)
            }
