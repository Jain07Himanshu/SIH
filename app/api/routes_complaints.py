from typing import Optional, Any
from fastapi import APIRouter, Depends, status, Body
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import UserModel
from app.auth.dependencies import get_optional_user, get_current_user
from app.schemas.complaint_dto import (
    ComplaintCreateRequest,
    ComplaintDetailResponse,
    ComplaintTrackResponse
)
from app.services.complaint_service import ComplaintService

router = APIRouter(prefix="/api/v1/complaints", tags=["Complaints"])

@router.post("", status_code=status.HTTP_201_CREATED)
def create_complaint(
    req: ComplaintCreateRequest,
    current_user: Optional[UserModel] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    service = ComplaintService(db)
    return service.create_complaint(req, current_user=current_user)

@router.post("/normalize")
def normalize_text(
    payload: dict[str, Any] = Body(...),
    db: Session = Depends(get_db)
):
    text = payload.get("text", "")
    service = ComplaintService(db)
    return service.normalize_text_input(text)

@router.get("/my", response_model=list[ComplaintDetailResponse])
def get_my_complaints(
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = ComplaintService(db)
    return service.get_my_complaints(current_user.email)

@router.get("/track/{complaint_id}", response_model=ComplaintTrackResponse)
def track_complaint(complaint_id: str, db: Session = Depends(get_db)):
    service = ComplaintService(db)
    return service.track(complaint_id)

@router.get("/{complaint_id}", response_model=ComplaintDetailResponse)
def get_complaint_detail(complaint_id: str, db: Session = Depends(get_db)):
    service = ComplaintService(db)
    return service.get_by_id(complaint_id)
