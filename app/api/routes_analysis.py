from fastapi import APIRouter, HTTPException, Depends
from app.schemas.complaint import ComplaintInput, ComplaintRecord, BatchProcessingReport
from app.schemas.similarity import SimilarityMatchResult
from app.schemas.issue import IssueRecord
from app.schemas.cluster import ClusterSummary
from app.services.pipeline import GrievanceIntelligencePipeline

router = APIRouter(prefix="/api/v1/analyze", tags=["Analysis & Ingestion"])

# Singleton pipeline instance for in-memory serving
_pipeline: GrievanceIntelligencePipeline | None = None

def get_pipeline() -> GrievanceIntelligencePipeline:
    global _pipeline
    if _pipeline is None:
        _pipeline = GrievanceIntelligencePipeline()
    return _pipeline

@router.post("", response_model=dict)
def analyze_single_complaint(input_data: ComplaintInput, pipeline: GrievanceIntelligencePipeline = Depends(get_pipeline)):
    try:
        raw_record = input_data.to_record()
        norm_complaint, match_res, issue_rec = pipeline.process_single(raw_record)
        return {
            "complaint": norm_complaint,
            "match": match_res,
            "assigned_issue": issue_rec
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/batch", response_model=dict)
def analyze_batch_complaints(inputs: list[ComplaintInput], pipeline: GrievanceIntelligencePipeline = Depends(get_pipeline)):
    try:
        raw_records = [inp.to_record() for inp in inputs]
        issues, cluster_summary, report = pipeline.process_batch(raw_records)
        return {
            "total_complaints": len(inputs),
            "unique_issues": len(issues),
            "issues": issues,
            "clusters": cluster_summary,
            "report": report
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
