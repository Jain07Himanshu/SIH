from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.repositories.user_repository import UserRepository
from app.auth.security import hash_password, verify_password, create_access_token
from app.schemas.auth import (
    CitizenRegisterRequest,
    AuthorityRegisterRequest,
    LoginRequest,
    TokenResponse,
    UserProfileResponse
)

class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)

    def register_citizen(self, req: CitizenRegisterRequest) -> TokenResponse:
        existing = self.user_repo.get_by_email(req.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"An account with email '{req.email}' already exists."
            )
        
        pwd_hash = hash_password(req.password)
        user = self.user_repo.create(
            name=req.name,
            email=req.email,
            password_hash=pwd_hash,
            role="CITIZEN"
        )
        token = create_access_token({"sub": user.email, "role": user.role, "user_id": user.user_id})
        return TokenResponse(
            access_token=token,
            user=UserProfileResponse.model_validate(user),
            message="Citizen account created successfully."
        )

    def register_authority(self, req: AuthorityRegisterRequest) -> TokenResponse:
        existing = self.user_repo.get_by_email(req.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"An official account with email '{req.email}' already exists."
            )
        
        pwd_hash = hash_password(req.password)
        user = self.user_repo.create(
            name=req.name,
            email=req.email,
            password_hash=pwd_hash,
            role="AUTHORITY",
            designation=req.designation,
            department=req.department,
            employee_id=req.employeeId,
            phone=req.phone
        )
        token = create_access_token({"sub": user.email, "role": user.role, "user_id": user.user_id})
        return TokenResponse(
            access_token=token,
            user=UserProfileResponse.model_validate(user),
            message="Authority account created successfully."
        )

    def login(self, req: LoginRequest) -> TokenResponse:
        user = self.user_repo.get_by_email(req.email)
        if not user or not verify_password(req.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password."
            )
        
        if req.role and req.role.upper() != user.role.upper():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role mismatch: This account is registered as '{user.role}', not '{req.role.upper()}'."
            )
        
        token = create_access_token({"sub": user.email, "role": user.role, "user_id": user.user_id})
        return TokenResponse(
            access_token=token,
            user=UserProfileResponse.model_validate(user),
            message=f"Welcome back, {user.name}!"
        )
