from app.analytics.aggregations import AnalyticsAggregator
from app.analytics.trends import TrendAnalyzer
from app.analytics.hotspots import HotspotAnalyzer

def test_analytics_and_hotspots(pipeline, sample_complaints):
    issues, _, _ = pipeline.process_batch(sample_complaints)
    agg = AnalyticsAggregator(taxonomy_manager=pipeline.taxonomy)

    overview = agg.compute_overview(sample_complaints, issues)
    assert overview.total_complaints == 6
    assert overview.unique_issues == len(issues)
    assert overview.duplicate_rate > 0

    cats = agg.compute_category_analytics(issues)
    assert len(cats) >= 2

    trends = TrendAnalyzer.analyze_trends(sample_complaints, issues, interval="daily")
    assert len(trends.trends) >= 1

    hotspots = HotspotAnalyzer.identify_hotspots(sample_complaints, issues)
    assert hotspots.total_hotspots >= 1
