from fastapi import APIRouter, Depends
from app.schemas.analytics import (
    OverviewAnalytics,
    CategoryAnalyticsItem,
    DepartmentAnalyticsItem,
    TrendAnalytics,
    HotspotListResponse
)
from app.analytics.aggregations import AnalyticsAggregator
from app.analytics.trends import TrendAnalyzer
from app.analytics.hotspots import HotspotAnalyzer
from app.services.pipeline import GrievanceIntelligencePipeline
from app.api.routes_analysis import get_pipeline

router = APIRouter(prefix="/api/v1/analytics", tags=["Analytics & Authority Dashboard"])

@router.get("/overview", response_model=OverviewAnalytics)
def get_overview(pipeline: GrievanceIntelligencePipeline = Depends(get_pipeline)):
    complaints = [nc.raw_record for nc in pipeline.normalized_cache.values()]
    issues = list(pipeline.issues.values())
    agg = AnalyticsAggregator(taxonomy_manager=pipeline.taxonomy)
    return agg.compute_overview(complaints, issues)

@router.get("/categories", response_model=list[CategoryAnalyticsItem])
def get_category_analytics(pipeline: GrievanceIntelligencePipeline = Depends(get_pipeline)):
    issues = list(pipeline.issues.values())
    agg = AnalyticsAggregator(taxonomy_manager=pipeline.taxonomy)
    return agg.compute_category_analytics(issues)

@router.get("/departments", response_model=list[DepartmentAnalyticsItem])
def get_department_analytics(pipeline: GrievanceIntelligencePipeline = Depends(get_pipeline)):
    issues = list(pipeline.issues.values())
    agg = AnalyticsAggregator(taxonomy_manager=pipeline.taxonomy)
    return agg.compute_department_analytics(issues)

@router.get("/trends", response_model=TrendAnalytics)
def get_trends(interval: str = "daily", pipeline: GrievanceIntelligencePipeline = Depends(get_pipeline)):
    complaints = [nc.raw_record for nc in pipeline.normalized_cache.values()]
    issues = list(pipeline.issues.values())
    return TrendAnalyzer.analyze_trends(complaints, issues, interval=interval)

@router.get("/hotspots", response_model=HotspotListResponse)
def get_hotspots(radius_km: float = 0.8, pipeline: GrievanceIntelligencePipeline = Depends(get_pipeline)):
    complaints = [nc.raw_record for nc in pipeline.normalized_cache.values()]
    issues = list(pipeline.issues.values())
    return HotspotAnalyzer.identify_hotspots(complaints, issues, radius_km=radius_km)
