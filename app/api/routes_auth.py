from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import UserModel
from app.auth.dependencies import get_current_user
from app.schemas.auth import (
    CitizenRegisterRequest,
    AuthorityRegisterRequest,
    LoginRequest,
    TokenResponse,
    UserProfileResponse
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])

@router.post("/register/citizen", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register_citizen(req: CitizenRegisterRequest, db: Session = Depends(get_db)):
    service = AuthService(db)
    return service.register_citizen(req)

@router.post("/register/authority", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register_authority(req: AuthorityRegisterRequest, db: Session = Depends(get_db)):
    service = AuthService(db)
    return service.register_authority(req)

@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    service = AuthService(db)
    return service.login(req)

@router.get("/me", response_model=UserProfileResponse)
def get_me(current_user: UserModel = Depends(get_current_user)):
    return UserProfileResponse.from_orm(current_user)
