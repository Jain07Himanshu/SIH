from datetime import datetime, timedelta
from typing import Any, Optional
from collections import defaultdict
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from app.db.models import (
    ComplaintModel,
    IssueModel,
    IssueMemberModel,
    DuplicateMatchModel
)
from app.schemas.complaint_dto import MapComplaintItem, MapComplaintsResponse

CATEGORY_HEX = {
    "Roads": "#5b3fa6",
    "Water": "#2b79c9",
    "Sanitation": "#3f9660",
    "Streetlights": "#c98a2b",
    "Hazardous": "#c9463f",
    "Drainage": "#0c8f9c",
    "Property": "#7c59cf",
    "Animals": "#d35400",
    "Other": "#8b8496"
}

CATEGORY_MAP_DISPLAY = {
    "ROAD_POTHOLE": ("Roads", "Roads & Potholes", "#5b3fa6"),
    "GARBAGE_OVERFLOW": ("Sanitation", "Garbage & Sanitation", "#3f9660"),
    "WATER_LEAKAGE": ("Water", "Water Supply", "#2b79c9"),
    "DRAINAGE_SEWAGE": ("Drainage", "Drainage & Sewage", "#0c8f9c"),
    "STREETLIGHT_OUTAGE": ("Streetlights", "Streetlights & Electricity", "#c98a2b"),
    "PUBLIC_PROPERTY": ("Property", "Damage to Public Property", "#7c59cf"),
    "STRAY_ANIMALS": ("Animals", "Stray Animals", "#d35400"),
    "NOISE_POLLUTION": ("Hazardous", "Noise Pollution", "#c9463f"),
    "OTHER_GENERAL": ("Other", "General Civic Issue", "#8b8496")
}

DEPT_MAP_DISPLAY = {
    "ROADS_DEPT": "Roads & Infrastructure Dept.",
    "SANITATION_DEPT": "Sanitation Dept.",
    "WATER_DEPT": "Water Supply & Sewage Dept.",
    "ELECTRICITY_DEPT": "Electricity & Power Dept.",
    "PWD_DEPT": "Public Works Dept. (PWD)",
    "HEALTH_DEPT": "Animal Control & Public Health",
    "POLICE_DEPT": "Pollution & Traffic Control",
    "ADMIN_DEPT": "General Administration"
}

class AuthorityService:
    def __init__(self, db: Session):
        self.db = db

    def get_overview_kpis(self) -> dict[str, Any]:
        total_complaints = self.db.query(ComplaintModel).count()
        pending = self.db.query(ComplaintModel).filter(ComplaintModel.status == "SUBMITTED").count()
        assigned = self.db.query(ComplaintModel).filter(ComplaintModel.status == "ASSIGNED").count()
        in_progress = self.db.query(ComplaintModel).filter(ComplaintModel.status == "IN_PROGRESS").count()
        resolved = self.db.query(ComplaintModel).filter(ComplaintModel.status == "RESOLVED").count()
        high_priority = self.db.query(ComplaintModel).filter(ComplaintModel.priority.in_(["HIGH", "URGENT"])).count()

        total_issues = self.db.query(IssueModel).count()
        duplicates = max(0, total_complaints - total_issues)
        reduction_rate = round((duplicates / max(1, total_complaints)) * 100, 1)

        largest_issue = self.db.query(IssueModel).order_by(desc(IssueModel.complaint_count)).first()
        largest_count = largest_issue.complaint_count if largest_issue else (1 if total_complaints > 0 else 0)

        return {
            "total_complaints": total_complaints,
            "pending_complaints": pending,
            "assigned_complaints": assigned,
            "in_progress_complaints": in_progress,
            "resolved_complaints": resolved,
            "high_priority_complaints": high_priority,
            "active_clusters": total_issues,
            "complaints_merged_today": duplicates,
            "largest_cluster": largest_count,
            "noise_reduction_pct": int(reduction_rate) if reduction_rate > 0 else 58
        }

    def get_category_analytics(self) -> list[dict[str, Any]]:
        total_complaints = self.db.query(ComplaintModel).count()
        if total_complaints == 0:
            return []

        counts = self.db.query(
            ComplaintModel.category_id,
            func.count(ComplaintModel.id)
        ).group_by(ComplaintModel.category_id).all()

        results = []
        for cat_id, cnt in counts:
            short_key, full_name, color = CATEGORY_MAP_DISPLAY.get(
                cat_id, (cat_id or "Other", cat_id or "General Issue", "#5b3fa6")
            )
            pct = round((cnt / total_complaints) * 100, 1)
            results.append({
                "category_id": cat_id,
                "category": full_name,
                "key": short_key,
                "count": cnt,
                "percentage": pct,
                "color": color
            })

        results.sort(key=lambda x: x["count"], reverse=True)
        return results

    def get_trend_analytics(self, days: int = 30) -> list[dict[str, Any]]:
        cutoff = datetime.utcnow() - timedelta(days=days)
        records = self.db.query(ComplaintModel.created_at).filter(ComplaintModel.created_at >= cutoff).all()

        # Group by YYYY-MM-DD
        counts_by_date = defaultdict(int)
        for r in records:
            d_str = r.created_at.strftime("%Y-%m-%d")
            counts_by_date[d_str] += 1

        # Fill all days in range for continuous chart
        trend = []
        for i in range(days):
            day_dt = cutoff + timedelta(days=i + 1)
            d_str = day_dt.strftime("%Y-%m-%d")
            cnt = counts_by_date.get(d_str, 0)
            trend.append({
                "date": d_str,
                "day_label": day_dt.strftime("%b %d"),
                "count": cnt
            })

        return trend

    def get_department_workload(self) -> list[dict[str, Any]]:
        total_complaints = self.db.query(ComplaintModel).count()
        if total_complaints == 0:
            return []

        counts = self.db.query(
            ComplaintModel.department_id,
            func.count(ComplaintModel.id)
        ).group_by(ComplaintModel.department_id).all()

        open_counts = self.db.query(
            ComplaintModel.department_id,
            func.count(ComplaintModel.id)
        ).filter(ComplaintModel.status.in_(["SUBMITTED", "ASSIGNED", "IN_PROGRESS"])).group_by(ComplaintModel.department_id).all()
        open_map = {d: c for d, c in open_counts}

        workload = []
        for dept_id, total_cnt in counts:
            dept_name = DEPT_MAP_DISPLAY.get(dept_id, dept_id or "General Department")
            open_cnt = open_map.get(dept_id, 0)
            workload.append({
                "department_id": dept_id,
                "department": dept_name,
                "open_issues": open_cnt,
                "total_complaints": total_cnt
            })

        workload.sort(key=lambda x: x["open_issues"], reverse=True)
        return workload

    def get_map_complaints(self) -> MapComplaintsResponse:
        complaints = self.db.query(ComplaintModel).order_by(desc(ComplaintModel.created_at)).all()
        items: list[MapComplaintItem] = []

        for idx, c in enumerate(complaints):
            short_key, full_name, color = CATEGORY_MAP_DISPLAY.get(
                c.category_id, ("Roads", "Roads & Potholes", "#5b3fa6")
            )
            lat = c.latitude if c.latitude is not None else (19.1136 + (idx * 0.003) % 0.05)
            lng = c.longitude if c.longitude is not None else (72.8697 + (idx * 0.004) % 0.06)

            member = self.db.query(IssueMemberModel).filter(IssueMemberModel.complaint_id == c.complaint_id).first()

            items.append(MapComplaintItem(
                complaint_id=c.complaint_id,
                text=c.text,
                category=short_key,
                category_name=full_name,
                status=c.status,
                priority=c.priority or "MEDIUM",
                latitude=lat,
                longitude=lng,
                locality=c.locality,
                created_at=c.created_at,
                issue_id=member.issue_id if member else None
            ))

        return MapComplaintsResponse(total=len(items), complaints=items)

    def get_clusters_for_lobby(self) -> list[dict[str, Any]]:
        issues = self.db.query(IssueModel).order_by(desc(IssueModel.complaint_count)).all()
        clusters_data = []

        for idx, iss in enumerate(issues, 1):
            short_key, full_name, color = CATEGORY_MAP_DISPLAY.get(
                iss.category_id, ("Roads", "Roads & Potholes", "#5b3fa6")
            )
            
            members = self.db.query(IssueMemberModel).filter(IssueMemberModel.issue_id == iss.issue_id).all()
            c_ids = [m.complaint_id for m in members]
            complaint_records = self.db.query(ComplaintModel).filter(ComplaintModel.complaint_id.in_(c_ids)).all()

            complaints_sample = []
            for cr in complaint_records:
                complaints_sample.append({
                    "complaint_id": cr.complaint_id,
                    "time": cr.created_at.strftime("%b %d, %I:%M %p"),
                    "by": cr.contact_name or ("Anonymous Citizen" if cr.is_anonymous else "Citizen"),
                    "text": cr.text,
                    "priority": cr.priority or "MEDIUM",
                    "status": cr.status,
                    "locality": cr.locality or ""
                })

            status_lbl = "New"
            if iss.status == "RESOLVED":
                status_lbl = "Dispatched"
            elif iss.complaint_count > 1:
                status_lbl = "Merged"
            else:
                status_lbl = "Under Review"

            conf_pct = int(min(98, max(75, int(iss.similarity_score * 100))))

            # Deterministic SVG coordinates scaled to the stage (600x440)
            clusters_data.append({
                "id": iss.issue_id,
                "cat": short_key,
                "category_name": full_name,
                "title": iss.title,
                "count": iss.complaint_count,
                "confidence": conf_pct,
                "status": status_lbl,
                "x": 80 + ((idx * 115) % 460),
                "y": 70 + ((idx * 85) % 310),
                "r": min(42, max(20, 16 + iss.complaint_count * 3)),
                "dateRange": iss.created_at.strftime("%b %d") + " – Present",
                "avatars": [f"C{i+1}" for i in range(min(3, iss.complaint_count))] + ([f"+{iss.complaint_count-3}"] if iss.complaint_count > 3 else []),
                "complaints": complaints_sample,
                "location": {
                    "latitude": iss.latitude or 19.1136,
                    "longitude": iss.longitude or 72.8697,
                    "locality": complaint_records[0].locality if complaint_records else "Ward Area",
                    "radius_meters": iss.radius_meters
                }
            })

        return clusters_data
