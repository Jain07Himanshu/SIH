from typing import Any, Optional
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import UserModel, IssueMemberModel, IssueModel
from app.auth.dependencies import get_optional_user
from app.schemas.complaint_dto import (
    MapComplaintsResponse,
    ComplaintDetailResponse,
    StatusUpdateRequest
)
from app.services.authority_service import AuthorityService
from app.services.complaint_service import ComplaintService

router = APIRouter(prefix="/api/v1/authority", tags=["Authority"])

@router.get("/analytics/overview", response_model=dict[str, Any])
def get_overview_kpis(db: Session = Depends(get_db)):
    service = AuthorityService(db)
    return service.get_overview_kpis()

@router.get("/analytics/categories", response_model=list[dict[str, Any]])
def get_category_analytics(db: Session = Depends(get_db)):
    service = AuthorityService(db)
    return service.get_category_analytics()

@router.get("/analytics/trends", response_model=list[dict[str, Any]])
def get_trend_analytics(days: int = Query(30, ge=1, le=180), db: Session = Depends(get_db)):
    service = AuthorityService(db)
    return service.get_trend_analytics(days=days)

@router.get("/analytics/departments", response_model=list[dict[str, Any]])
def get_department_workload(db: Session = Depends(get_db)):
    service = AuthorityService(db)
    return service.get_department_workload()

@router.get("/complaints/map", response_model=MapComplaintsResponse)
def get_map_complaints(db: Session = Depends(get_db)):
    service = AuthorityService(db)
    return service.get_map_complaints()

@router.get("/clusters", response_model=list[dict[str, Any]])
def get_clusters(db: Session = Depends(get_db)):
    service = AuthorityService(db)
    return service.get_clusters_for_lobby()

@router.get("/complaints/{complaint_id}", response_model=ComplaintDetailResponse)
def get_authority_complaint_detail(complaint_id: str, db: Session = Depends(get_db)):
    service = ComplaintService(db)
    return service.get_by_id(complaint_id)

@router.patch("/complaints/{complaint_id}/status", response_model=ComplaintDetailResponse)
def update_complaint_status(
    complaint_id: str,
    req: StatusUpdateRequest,
    current_user: Optional[UserModel] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    service = ComplaintService(db)
    changed_by = current_user.name if current_user else "Authority Officer"
    return service.update_status(complaint_id, req.status, changed_by=changed_by, comment=req.comment)

@router.post("/clusters/{issue_id}/merge")
def merge_and_assign_cluster(
    issue_id: str,
    current_user: Optional[UserModel] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    service = ComplaintService(db)
    members = db.query(IssueMemberModel).filter(IssueMemberModel.issue_id == issue_id).all()
    changed_by = current_user.name if current_user else "Authority Officer"
    for m in members:
        service.update_status(m.complaint_id, "ASSIGNED", changed_by=changed_by, comment=f"Assigned under unified issue {issue_id}")
    
    issue = db.query(IssueModel).filter(IssueModel.issue_id == issue_id).first()
    if issue:
        issue.status = "ASSIGNED"
        db.commit()

    return {"success": True, "issue_id": issue_id, "message": f"Cluster {issue_id} merged and dispatched to department."}
