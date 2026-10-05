import math
from datetime import datetime
from collections import Counter
import numpy as np

from app.schemas.complaint import ComplaintRecord, NormalizedComplaint
from app.schemas.category import CategoryPrediction, DepartmentRecord
from app.schemas.issue import (
    IssueRecord,
    LocationSummary,
    PrioritySummary,
    TimeSummary
)
from app.classification.taxonomy import TaxonomyManager
from app.similarity.geographic import GeographicSimilarityCalculator

class IssueBuilder:
    def __init__(self, taxonomy_manager: TaxonomyManager | None = None):
        self.taxonomy = taxonomy_manager or TaxonomyManager()

    def generate_title(self, complaints: list[ComplaintRecord], top_keywords: list[str]) -> str:
        if not complaints:
            return "Civic Issue"

        # 1. Look for strong location keywords
        location_part = ""
        for kw in top_keywords:
            for c in complaints:
                if kw in c.text.lower():
                    # check if kw looks like a location
                    if any(place in kw for place in ["station", "road", "ward", "sector", "hospital", "school", "market", "nagar", "colony", "street"]):
                        location_part = kw.title()
                        break
            if location_part:
                break

        # 2. Strong issue core
        issue_part = ""
        for kw in top_keywords:
            if kw.title() != location_part:
                issue_part = kw.title()
                break

        if not issue_part and complaints:
            issue_part = complaints[0].text[:40].strip()

        if issue_part and location_part:
            return f"{issue_part} near {location_part}"
        elif issue_part:
            return f"{issue_part} Issue"
        else:
            return complaints[0].text[:50].strip()

    def build_location_summary(self, complaints: list[ComplaintRecord]) -> LocationSummary | None:
        coords = [(c.latitude, c.longitude) for c in complaints if c.latitude is not None and c.longitude is not None]
        if not coords:
            return None

        avg_lat = float(np.mean([p[0] for p in coords]))
        avg_lng = float(np.mean([p[1] for p in coords]))

        # Calculate max radius
        max_dist = 0.0
        for lat, lng in coords:
            d = GeographicSimilarityCalculator.haversine_distance(avg_lat, avg_lng, lat, lng)
            if d > max_dist:
                max_dist = d

        min_lat = float(min(p[0] for p in coords))
        max_lat = float(max(p[0] for p in coords))
        min_lng = float(min(p[1] for p in coords))
        max_lng = float(max(p[1] for p in coords))

        concentration = "High" if max_dist < 500.0 else ("Medium" if max_dist < 1500.0 else "Dispersed")

        return LocationSummary(
            latitude=round(avg_lat, 6),
            longitude=round(avg_lng, 6),
            radius_meters=round(max_dist, 1),
            bounding_box={"min_lat": min_lat, "max_lat": max_lat, "min_lng": min_lng, "max_lng": max_lng},
            geographic_concentration=concentration
        )

    def build_priority_summary(self, complaints: list[ComplaintRecord]) -> PrioritySummary:
        high = 0
        med = 0
        low = 0
        unspec = 0
        score_sum = 0.0

        for c in complaints:
            p = (c.priority or "").upper()
            if p == "HIGH":
                high += 1
                score_sum += 3.0
            elif p == "LOW":
                low += 1
                score_sum += 1.0
            elif p == "MEDIUM":
                med += 1
                score_sum += 2.0
            else:
                unspec += 1
                score_sum += 2.0 # default medium

        total = max(1, len(complaints))
        avg_score = score_sum / total

        dominant = "HIGH" if high >= max(med, low, 1) else ("LOW" if low > max(high, med) else "MEDIUM")

        return PrioritySummary(
            high_count=high,
            medium_count=med,
            low_count=low,
            unspecified_count=unspec,
            dominant_priority=dominant,
            average_priority_score=round(avg_score, 2)
        )

    def build_time_summary(self, complaints: list[ComplaintRecord]) -> TimeSummary | None:
        timestamps = [c.timestamp for c in complaints if c.timestamp is not None]
        if not timestamps:
            return None
        earliest = min(timestamps)
        latest = max(timestamps)
        span_days = (latest - earliest).total_seconds() / 86400.0

        return TimeSummary(
            earliest_timestamp=earliest,
            latest_timestamp=latest,
            span_days=round(span_days, 1)
        )

    def build_issue(self,
                    issue_id: str,
                    normalized_complaints: list[NormalizedComplaint],
                    category_pred: CategoryPrediction | None = None,
                    similarity_score: float = 1.0) -> IssueRecord:
        
        raw_complaints = [nc.raw_record for nc in normalized_complaints]
        complaint_ids = [c.complaint_id for c in raw_complaints]

        # Collect & rank keywords
        all_kws = []
        for nc in normalized_complaints:
            all_kws.extend([k.term for k in nc.keywords])
        top_kws = [term for term, _ in Counter(all_kws).most_common(6)]

        title = self.generate_title(raw_complaints, top_kws)
        loc_summary = self.build_location_summary(raw_complaints)
        priority_summary = self.build_priority_summary(raw_complaints)
        time_summary = self.build_time_summary(raw_complaints)

        # Department
        dept_record = None
        if category_pred and category_pred.department_id:
            dept_record = self.taxonomy.get_department(category_pred.department_id)

        rep_id = raw_complaints[0].complaint_id
        duplicate_count = max(0, len(complaint_ids) - 1)

        return IssueRecord(
            issue_id=issue_id,
            title=title,
            category=category_pred,
            department=dept_record,
            keywords=top_kws,
            representative_complaint_id=rep_id,
            complaint_ids=complaint_ids,
            complaint_count=len(complaint_ids),
            duplicate_count=duplicate_count,
            similarity_score=round(similarity_score, 4),
            location=loc_summary,
            priority_summary=priority_summary,
            status_summary={"OPEN": len(complaint_ids)},
            time_summary=time_summary,
            needs_review=False
        )
