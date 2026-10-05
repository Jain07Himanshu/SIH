from fastapi import APIRouter, Depends
from app.schemas.similarity import SimilarityCompareRequest, SimilarityCompareResponse, SimilarityMatchResult
from app.schemas.complaint import ComplaintRecord
from app.services.pipeline import GrievanceIntelligencePipeline
from app.api.routes_analysis import get_pipeline

router = APIRouter(prefix="/api/v1/similarity", tags=["Similarity & Matching"])

@router.post("/compare", response_model=SimilarityCompareResponse)
def compare_pair(req: SimilarityCompareRequest, pipeline: GrievanceIntelligencePipeline = Depends(get_pipeline)):
    rec_a = ComplaintRecord(
        complaint_id="A",
        text=req.complaint_a.text,
        category=req.complaint_a.category,
        priority=req.complaint_a.priority,
        latitude=req.complaint_a.latitude,
        longitude=req.complaint_a.longitude,
        timestamp=req.complaint_a.timestamp
    )
    rec_b = ComplaintRecord(
        complaint_id="B",
        text=req.complaint_b.text,
        category=req.complaint_b.category,
        priority=req.complaint_b.priority,
        latitude=req.complaint_b.latitude,
        longitude=req.complaint_b.longitude,
        timestamp=req.complaint_b.timestamp
    )

    norm_a = pipeline.normalizer.normalize_record(rec_a)
    norm_b = pipeline.normalizer.normalize_record(rec_b)

    kws_a = pipeline.keyword_extractor.extract_keywords(norm_a.text.clean)
    kws_b = pipeline.keyword_extractor.extract_keywords(norm_b.text.clean)

    emb_a = pipeline.encoder.encode_one(norm_a.text.semantic)
    emb_b = pipeline.encoder.encode_one(norm_b.text.semantic)

    match_res = pipeline.scorer.score_pair(
        rec_a, rec_b,
        emb_a=emb_a, emb_b=emb_b,
        kw_a=kws_a, kw_b=kws_b
    )

    return SimilarityCompareResponse(
        similarity_score=match_res.similarity_score,
        match_type=match_res.match_type,
        components=match_res.components,
        evidence=match_res.evidence
    )
