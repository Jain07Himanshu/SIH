from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime

class CitizenRegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=200)
    email: str = Field(..., min_length=5, max_length=200)
    password: str = Field(..., min_length=6)

class AuthorityRegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=200)
    designation: str = Field(..., min_length=2, max_length=200)
    department: str = Field(..., min_length=2, max_length=200)
    employeeId: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., min_length=5, max_length=200)
    phone: str = Field(..., min_length=10, max_length=20)
    password: str = Field(..., min_length=6)

class LoginRequest(BaseModel):
    email: str
    password: str
    role: Optional[str] = "citizen"

class UserProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: str
    name: str
    email: str
    role: str
    designation: Optional[str] = None
    department: Optional[str] = None
    employee_id: Optional[str] = None
    phone: Optional[str] = None
    created_at: datetime

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserProfileResponse
    message: str = "Authentication successful"
