from fastapi import APIRouter, Depends
from app.schemas.complaint import ComplaintInput
from app.schemas.cluster import ClusterSummary
from app.services.pipeline import GrievanceIntelligencePipeline
from app.api.routes_analysis import get_pipeline

router = APIRouter(prefix="/api/v1/clusters", tags=["Clustering"])

@router.post("/build", response_model=ClusterSummary)
def build_clusters(inputs: list[ComplaintInput], pipeline: GrievanceIntelligencePipeline = Depends(get_pipeline)):
    raw_records = [inp.to_record() for inp in inputs]
    _, cluster_summary, _ = pipeline.process_batch(raw_records)
    return cluster_summary
