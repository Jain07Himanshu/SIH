import numpy as np
from app.schemas.complaint import ComplaintRecord
from app.schemas.issue import IssueRecord
from app.schemas.analytics import HotspotRecord, HotspotListResponse
from app.clustering.geographic_clusterer import GeographicClusterer
from app.similarity.geographic import GeographicSimilarityCalculator

class HotspotAnalyzer:
    @staticmethod
    def identify_hotspots(complaints: list[ComplaintRecord], issues: list[IssueRecord], radius_km: float = 0.8) -> HotspotListResponse:
        spatial_clusters = GeographicClusterer.cluster_hotspots(complaints, eps_km=radius_km, min_samples=2)

        records: list[HotspotRecord] = []
        for idx, cluster_complaints in enumerate(spatial_clusters):
            lats = [c.latitude for c in cluster_complaints if c.latitude is not None]
            lngs = [c.longitude for c in cluster_complaints if c.longitude is not None]
            if not lats or not lngs:
                continue

            center_lat = float(np.mean(lats))
            center_lng = float(np.mean(lngs))

            # Max radius from centroid
            max_r = 0.0
            for lat, lng in zip(lats, lngs):
                d = GeographicSimilarityCalculator.haversine_distance(center_lat, center_lng, lat, lng)
                if d > max_r:
                    max_r = d

            # Categories & keywords
            cats = [c.category for c in cluster_complaints if c.category]
            from collections import Counter
            dominant_cat = Counter(cats).most_common(1)[0][0] if cats else "CIVIC_HOTSPOT"

            # Check matching issues
            cid_set = set(c.complaint_id for c in cluster_complaints)
            matched_issues = [i for i in issues if any(cid in cid_set for cid in i.complaint_ids)]

            prios = [i.priority_summary.dominant_priority for i in matched_issues]
            dominant_p = max(set(prios), key=prios.count) if prios else "HIGH"

            # Keywords
            all_kws = []
            for i in matched_issues:
                all_kws.extend(i.keywords)
            top_kws = [k for k, _ in Counter(all_kws).most_common(5)]

            records.append(HotspotRecord(
                hotspot_id=f"HOTSPOT-{idx+1:03d}",
                category=dominant_cat,
                issue_count=len(matched_issues),
                complaint_count=len(cluster_complaints),
                center={"lat": round(center_lat, 6), "lng": round(center_lng, 6)},
                radius_meters=round(max(max_r, 100.0), 1),
                priority=dominant_p,
                dominant_keywords=top_kws
            ))

        records.sort(key=lambda x: x.complaint_count, reverse=True)
        return HotspotListResponse(total_hotspots=len(records), hotspots=records)
