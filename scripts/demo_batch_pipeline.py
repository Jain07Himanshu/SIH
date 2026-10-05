import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.schemas.complaint import ComplaintRecord
from app.services.pipeline import GrievanceIntelligencePipeline
from app.analytics.aggregations import AnalyticsAggregator
from app.analytics.hotspots import HotspotAnalyzer

def run_demo():
    print("=" * 75)
    print("CIVIC GRIEVANCE PLATFORM -- END-TO-END INTELLIGENCE DEMO")
    print("=" * 75)

    complaints = [
        ComplaintRecord(complaint_id="CMP-101", text="Huge pothole near railway station flyover causing major traffic and bike skidding", category="ROAD_POTHOLE", priority="HIGH", latitude=28.6139, longitude=77.2090),
        ComplaintRecord(complaint_id="CMP-102", text="Dangerous deep pothole outside railway station flyover, two wheelers skidding", category="ROAD_POTHOLE", priority="HIGH", latitude=28.6141, longitude=77.2092),
        ComplaintRecord(complaint_id="CMP-103", text="Vehicle damaged due to big pothole near railway station", category="ROAD_POTHOLE", priority="HIGH", latitude=28.6140, longitude=77.2088),
        
        ComplaintRecord(complaint_id="CMP-201", text="Garbage dump overflowing near sector 15 market, foul smell spread everywhere", category="GARBAGE_OVERFLOW", priority="MEDIUM", latitude=28.6250, longitude=77.2180),
        ComplaintRecord(complaint_id="CMP-202", text="Uncollected trash and waste pile at sector 15 market gate", category="GARBAGE_OVERFLOW", priority="MEDIUM", latitude=28.6252, longitude=77.2182),
        
        ComplaintRecord(complaint_id="CMP-301", text="Water pipeline burst in block B, clean water flowing on street since 2 days", category="WATER_LEAKAGE", priority="HIGH", latitude=28.6310, longitude=77.2250),
        ComplaintRecord(complaint_id="CMP-302", text="Severe drinking water leak from broken pipe in Block B road", category="WATER_LEAKAGE", priority="HIGH", latitude=28.6312, longitude=77.2251),
        
        ComplaintRecord(complaint_id="CMP-401", text="All street lights dark in ward 9 lane 4, safety risk for pedestrians", category="STREETLIGHT_OUTAGE", priority="LOW", latitude=28.6400, longitude=77.2350),
        ComplaintRecord(complaint_id="CMP-501", text="Illegal commercial banners blocking road traffic signals", category="OTHER_GENERAL", priority="LOW", latitude=28.6500, longitude=77.2450)
    ]

    pipeline = GrievanceIntelligencePipeline()
    issues, cluster_summary, report = pipeline.process_batch(complaints)

    print(f"\n[OK] Successfully ingested and processed {len(complaints)} complaints.")
    print(f"[OK] Formed {len(issues)} distinct canonical issues with explainable evidence.\n")

    for idx, iss in enumerate(issues, 1):
        print(f"ISSUE #{idx}: [{iss.issue_id}] {iss.title}")
        print(f"  - Category:        {iss.category.category_name if iss.category else 'N/A'}")
        print(f"  - Department:      {iss.department.name if iss.department else 'N/A'}")
        print(f"  - Complaints ({iss.complaint_count}): {', '.join(iss.complaint_ids)}")
        print(f"  - Representative:  {iss.representative_complaint_id}")
        print(f"  - Key Keywords:    {', '.join(iss.keywords)}")
        if iss.location:
            print(f"  - GIS Centroid:    ({iss.location.latitude}, {iss.location.longitude}) [Radius: {iss.location.radius_meters}m]")
        print(f"  - Dominant Prio:   {iss.priority_summary.dominant_priority}")
        print()

    aggregator = AnalyticsAggregator(taxonomy_manager=pipeline.taxonomy)
    overview = aggregator.compute_overview(complaints, issues)
    print("=" * 75)
    print("EXECUTIVE OVERVIEW ANALYTICS:")
    print(f"  - Total Complaints Ingested:     {overview.total_complaints}")
    print(f"  - Unique Issues Created:         {overview.unique_issues}")
    print(f"  - Duplicate Complaints Filtered: {overview.duplicate_complaints} ({overview.duplicate_rate}% reduction)")
    print(f"  - Average Complaints per Issue:  {overview.average_cluster_size}")
    print(f"  - High Priority Civic Issues:    {overview.high_priority_issues}")
    print("=" * 75)

    hotspots = HotspotAnalyzer.identify_hotspots(complaints, issues)
    print(f"\nGIS HOTSPOTS IDENTIFIED ({hotspots.total_hotspots}):")
    for h in hotspots.hotspots:
        print(f"  - [{h.hotspot_id}] Category: {h.category} | Complaints: {h.complaint_count} | Radius: {h.radius_meters}m | Centroid: ({h.center['lat']}, {h.center['lng']})")
    print("=" * 75)

if __name__ == "__main__":
    run_demo()
