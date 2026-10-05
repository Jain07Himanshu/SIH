import sys
import os
import time
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.schemas.complaint import ComplaintRecord
from app.services.pipeline import GrievanceIntelligencePipeline

def run_evaluation():
    print("=" * 70)
    print("GRIEVANCE INTELLIGENCE ENGINE — BENCHMARK EVALUATION")
    print("=" * 70)

    dataset = [
        ComplaintRecord(complaint_id="C01", text="Deep dangerous pothole near central station pillar 12", category="ROAD_POTHOLE", priority="HIGH", latitude=28.6139, longitude=77.2090),
        ComplaintRecord(complaint_id="C02", text="Big pothole right outside central station pillar 12, cars getting damaged", category="ROAD_POTHOLE", priority="HIGH", latitude=28.6140, longitude=77.2091),
        ComplaintRecord(complaint_id="C03", text="Vehicle axle broke due to massive pothole near central station", category="ROAD_POTHOLE", priority="HIGH", latitude=28.6142, longitude=77.2089),
        
        ComplaintRecord(complaint_id="C04", text="Garbage bin overflowing near market entrance, terrible stench", category="GARBAGE_OVERFLOW", priority="MEDIUM", latitude=28.6200, longitude=77.2150),
        ComplaintRecord(complaint_id="C05", text="Uncollected trash and waste rotting at market entrance", category="GARBAGE_OVERFLOW", priority="MEDIUM", latitude=28.6201, longitude=77.2152),
        
        ComplaintRecord(complaint_id="C06", text="Drinking water pipeline burst in Sector 5, water wasted on street", category="WATER_LEAKAGE", priority="HIGH", latitude=28.6300, longitude=77.2200),
        ComplaintRecord(complaint_id="C07", text="Main water supply line leaking heavily in Sector 5 road", category="WATER_LEAKAGE", priority="HIGH", latitude=28.6302, longitude=77.2201),
        
        ComplaintRecord(complaint_id="C08", text="Streetlights not turning on in Ward 4 residential colony", category="STREETLIGHT_OUTAGE", priority="LOW", latitude=28.6400, longitude=77.2300),
        ComplaintRecord(complaint_id="C09", text="Severe noise pollution from factory generator late at night", category="OTHER_GENERAL", priority="LOW", latitude=28.6500, longitude=77.2400)
    ]

    pipeline = GrievanceIntelligencePipeline()
    t0 = time.perf_counter()
    issues, cluster_summary, report = pipeline.process_batch(dataset)
    total_time = time.perf_counter() - t0

    print(f"\nProcessed {len(dataset)} complaints into {len(issues)} canonical civic issues in {total_time*1000:.2f}ms.")
    print(f"Average throughput: {len(dataset) / total_time:.1f} complaints/sec\n")

    print(f"{'Issue ID':<10} | {'Complaints':<10} | {'Duplicates':<10} | {'Category':<22} | {'Issue Title'}")
    print("-" * 80)
    for iss in issues:
        cat_name = iss.category.category_name if iss.category else "Unclassified"
        print(f"{iss.issue_id:<10} | {iss.complaint_count:<10} | {iss.duplicate_count:<10} | {cat_name[:20]:<22} | {iss.title[:30]}")

    print("-" * 80)
    dup_total = sum(i.duplicate_count for i in issues)
    print(f"Total Complaints: {len(dataset)} | Unique Issues: {len(issues)} | Consolidated Duplicates: {dup_total} ({dup_total/len(dataset)*100:.1f}%)")
    print("=" * 70)

if __name__ == "__main__":
    run_evaluation()
