import uuid
import json
from datetime import datetime
from typing import Optional, Any
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.db.models import (
    ComplaintModel,
    ComplaintStatusHistoryModel,
    DuplicateMatchModel,
    IssueModel,
    IssueMemberModel,
    UserModel
)
from app.schemas.complaint_dto import (
    ComplaintCreateRequest,
    ComplaintDetailResponse,
    ComplaintTrackResponse,
    StatusHistoryItem
)
from app.services.duplicate_engine_service import DuplicateEngineService
from app.preprocessing.normalizer import ComplaintNormalizer
from app.schemas.complaint import ComplaintRecord

CATEGORY_MAP = {
    "roads": ("ROAD_POTHOLE", "Roads & Potholes", "ROADS_DEPT", "Roads & Infrastructure Dept."),
    "garbage": ("GARBAGE_OVERFLOW", "Garbage & Sanitation", "SANITATION_DEPT", "Sanitation Dept."),
    "water": ("WATER_LEAKAGE", "Water Supply", "WATER_DEPT", "Water Supply Dept."),
    "drainage": ("DRAINAGE_SEWAGE", "Drainage & Sewage", "WATER_DEPT", "Drainage & Sewage Dept."),
    "electricity": ("STREETLIGHT_OUTAGE", "Streetlights & Electricity", "ELECTRICITY_DEPT", "Electricity Dept."),
    "property": ("PUBLIC_PROPERTY", "Damage to Public Property", "PWD_DEPT", "Public Works Dept."),
    "animals": ("STRAY_ANIMALS", "Stray Animals", "HEALTH_DEPT", "Animal Control Dept."),
    "noise": ("NOISE_POLLUTION", "Noise Pollution", "POLICE_DEPT", "Pollution Control Dept."),
    "other": ("OTHER_GENERAL", "General Civic Issue", "ADMIN_DEPT", "General Administration")
}

STAGE_DEFS = [
    ("SUBMITTED", "Submitted", "Your complaint has been logged and is awaiting verification."),
    ("ASSIGNED", "Verified & Assigned", "This has been verified and assigned to the concerned department."),
    ("IN_PROGRESS", "In Progress", "The concerned team has been notified and is actively working on it."),
    ("RESOLVED", "Resolved", "This complaint has been marked resolved. Please confirm if the issue persists.")
]

class ComplaintService:
    def __init__(self, db: Session):
        self.db = db
        self.ai_service = DuplicateEngineService()
        self.normalizer = ComplaintNormalizer()

    def generate_complaint_id(self) -> str:
        count = self.db.query(ComplaintModel).count() + 100001
        return f"SS-{count}"

    def normalize_text_input(self, text: str) -> dict[str, Any]:
        rec = ComplaintRecord(complaint_id="TEMP", text=text)
        norm = self.normalizer.normalize_record(rec)
        canon_tokens = [self.normalizer.synonym_manager.canonicalize(t) for t in norm.tokens]
        return {
            "original": norm.text.original,
            "clean": norm.text.clean,
            "canonical_text": norm.text.keyword,
            "keyword": norm.text.keyword,
            "tokens": canon_tokens,
            "language": norm.language,
            "language_confidence": norm.language_confidence
        }

    def create_complaint(self, req: ComplaintCreateRequest, current_user: Optional[UserModel] = None) -> dict[str, Any]:
        cid = self.generate_complaint_id()
        cat_key = req.category.lower().strip()
        cat_id, cat_name, dept_id, dept_name = CATEGORY_MAP.get(
            cat_key, ("OTHER_GENERAL", "General Civic Issue", "ADMIN_DEPT", "General Administration")
        )

        norm_info = self.normalize_text_input(req.description)

        # 1. Persist complaint
        complaint = ComplaintModel(
            complaint_id=cid,
            citizen_id=current_user.email if current_user else None,
            text=req.description.strip(),
            clean_text=norm_info["clean"],
            category_id=cat_id,
            department_id=dept_id,
            locality=req.locality,
            ward=req.ward,
            landmark=req.landmark,
            priority=req.priority.upper() if req.priority else "MEDIUM",
            status="SUBMITTED",
            latitude=req.latitude,
            longitude=req.longitude,
            image_url=req.image_url,
            is_anonymous=req.is_anonymous,
            contact_name=req.full_name or (current_user.name if current_user else None),
            contact_phone=req.phone or (current_user.phone if current_user else None)
        )
        self.db.add(complaint)
        self.db.commit()
        self.db.refresh(complaint)

        # 2. Add initial status history
        history = ComplaintStatusHistoryModel(
            complaint_id=cid,
            old_status="NONE",
            new_status="SUBMITTED",
            changed_by=current_user.name if current_user else "Citizen",
            comment="Grievance submitted by citizen"
        )
        self.db.add(history)
        self.db.commit()

        # 3. AI Duplicate Clustering
        ai_result = self.ai_service.process_new_complaint(
            complaint_id=cid,
            text=complaint.text,
            category=complaint.category_id,
            latitude=complaint.latitude,
            longitude=complaint.longitude,
            locality=complaint.locality,
            ward=complaint.ward,
            timestamp=complaint.created_at
        )

        best_match = ai_result.get("best_match") or {}
        assigned_issue = ai_result.get("assigned_issue") or {}
        matched_id = best_match.get("matched_complaint_id") or ai_result.get("matched_complaint_id")
        matched_issue_id = assigned_issue.get("issue_id") or ai_result.get("matched_issue_id")
        similarity_score = best_match.get("similarity_score") or ai_result.get("similarity_score", 0.0)
        match_type = best_match.get("match_type") or ai_result.get("match_type", "NEW_ISSUE")
        confidence = best_match.get("confidence") or ai_result.get("confidence", 0.8)
        explanation = best_match.get("explanation") or ai_result.get("explanation", {})
        is_dup = ai_result.get("is_duplicate", False) or (match_type in ("DUPLICATE", "POSSIBLY_SIMILAR"))

        if matched_id or matched_issue_id:
            dup_match = DuplicateMatchModel(
                complaint_id=cid,
                matched_complaint_id=matched_id,
                matched_issue_id=matched_issue_id,
                semantic_score=similarity_score,
                final_similarity_score=similarity_score,
                match_type=match_type,
                confidence=confidence,
                explanation_json=json.dumps(explanation)
            )
            self.db.add(dup_match)

            if matched_issue_id:
                member = IssueMemberModel(
                    issue_id=matched_issue_id,
                    complaint_id=cid,
                    similarity_score=similarity_score,
                    is_representative=False
                )
                self.db.add(member)
                issue = self.db.query(IssueModel).filter(IssueModel.issue_id == matched_issue_id).first()
                if issue:
                    issue.complaint_count += 1
                    issue.duplicate_count += 1
            self.db.commit()

        return {
            "success": True,
            "complaint_id": cid,
            "status": complaint.status,
            "category_name": cat_name,
            "department_name": dept_name,
            "is_duplicate": is_dup,
            "match_type": match_type,
            "similarity_score": similarity_score,
            "matched_issue_id": matched_issue_id,
            "matched_complaint_id": matched_id,
            "normalization": {
                "clean_text": norm_info["clean"],
                "keywords": norm_info["tokens"][:5],
                "language": norm_info["language"]
            }
        }

    def track(self, complaint_id: str) -> ComplaintTrackResponse:
        cid = complaint_id.strip().upper()
        c = self.db.query(ComplaintModel).filter(ComplaintModel.complaint_id == cid).first()
        if not c:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Complaint '{cid}' not found")

        cat_name = "General Civic Issue"
        dept_name = "General Administration"
        for k, v in CATEGORY_MAP.items():
            if v[0] == c.category_id:
                cat_name = v[1]
                dept_name = v[3]
                break

        stage_idx = 0
        stage_lbl = "Submitted"
        status_note = "Your complaint has been logged and is awaiting verification."
        for idx, (code, lbl, note) in enumerate(STAGE_DEFS):
            if c.status == code:
                stage_idx = idx
                stage_lbl = lbl
                status_note = note
                break

        hist_records = self.db.query(ComplaintStatusHistoryModel).filter(
            ComplaintStatusHistoryModel.complaint_id == cid
        ).order_by(desc(ComplaintStatusHistoryModel.timestamp)).all()

        history_items = [
            StatusHistoryItem(
                old_status=h.old_status,
                new_status=h.new_status,
                changed_by=h.changed_by or "System",
                comment=h.comment or "",
                timestamp=h.timestamp
            ) for h in hist_records
        ]

        return ComplaintTrackResponse(
            complaint_id=c.complaint_id,
            category_name=cat_name,
            department_name=dept_name,
            locality=c.locality or "Ward Area",
            landmark=c.landmark,
            status=c.status,
            stage_index=stage_idx,
            stage_label=stage_lbl,
            status_note=status_note,
            filed_date=c.created_at.strftime("%b %d, %Y, %I:%M %p"),
            history=history_items
        )

    def get_by_id(self, complaint_id: str) -> ComplaintDetailResponse:
        cid = complaint_id.strip().upper()
        c = self.db.query(ComplaintModel).filter(ComplaintModel.complaint_id == cid).first()
        if not c:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Complaint '{cid}' not found")

        cat_name = "General Civic Issue"
        dept_name = "General Administration"
        for k, v in CATEGORY_MAP.items():
            if v[0] == c.category_id:
                cat_name = v[1]
                dept_name = v[3]
                break

        dup_match = self.db.query(DuplicateMatchModel).filter(DuplicateMatchModel.complaint_id == cid).first()
        history = self.db.query(ComplaintStatusHistoryModel).filter(
            ComplaintStatusHistoryModel.complaint_id == cid
        ).order_by(desc(ComplaintStatusHistoryModel.timestamp)).all()

        return ComplaintDetailResponse(
            complaint_id=c.complaint_id,
            citizen_id=c.citizen_id,
            text=c.text,
            clean_text=c.clean_text,
            category_id=c.category_id,
            category_name=cat_name,
            department_id=c.department_id,
            department_name=dept_name,
            locality=c.locality,
            ward=c.ward,
            landmark=c.landmark,
            priority=c.priority,
            status=c.status,
            latitude=c.latitude,
            longitude=c.longitude,
            image_url=c.image_url,
            is_anonymous=c.is_anonymous,
            contact_name=c.contact_name,
            contact_phone=c.contact_phone,
            created_at=c.created_at,
            matched_issue_id=dup_match.matched_issue_id if dup_match else None,
            matched_complaint_id=dup_match.matched_complaint_id if dup_match else None,
            similarity_score=dup_match.final_similarity_score if dup_match else None,
            match_type=dup_match.match_type if dup_match else None,
            confidence=dup_match.confidence if dup_match else None,
            history=[StatusHistoryItem(
                old_status=h.old_status,
                new_status=h.new_status,
                changed_by=h.changed_by or "System",
                comment=h.comment or "",
                timestamp=h.timestamp
            ) for h in history]
        )

    def get_my_complaints(self, user_email: str) -> list[ComplaintDetailResponse]:
        records = self.db.query(ComplaintModel).filter(
            ComplaintModel.citizen_id == user_email
        ).order_by(desc(ComplaintModel.created_at)).all()

        return [self.get_by_id(r.complaint_id) for r in records]

    def update_status(self, complaint_id: str, new_status: str, changed_by: str = "Authority Officer", comment: str = "") -> ComplaintDetailResponse:
        cid = complaint_id.strip().upper()
        c = self.db.query(ComplaintModel).filter(ComplaintModel.complaint_id == cid).first()
        if not c:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Complaint '{cid}' not found")

        old_status = c.status
        c.status = new_status.upper()

        hist = ComplaintStatusHistoryModel(
            complaint_id=cid,
            old_status=old_status,
            new_status=c.status,
            changed_by=changed_by,
            comment=comment or f"Status changed from {old_status} to {c.status}"
        )
        self.db.add(hist)
        self.db.commit()
        self.db.refresh(c)

        return self.get_by_id(cid)
