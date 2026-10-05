import uuid
from typing import Optional
from sqlalchemy.orm import Session
from app.db.models import UserModel

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: int) -> Optional[UserModel]:
        return self.db.query(UserModel).filter(UserModel.id == user_id).first()

    def get_by_email(self, email: str) -> Optional[UserModel]:
        return self.db.query(UserModel).filter(UserModel.email == email.strip().lower()).first()

    def create(self, name: str, email: str, password_hash: str, role: str,
               designation: Optional[str] = None, department: Optional[str] = None,
               employee_id: Optional[str] = None, phone: Optional[str] = None) -> UserModel:
        uid = f"USR-{uuid.uuid4().hex[:8].upper()}"
        user = UserModel(
            user_id=uid,
            name=name.strip(),
            email=email.strip().lower(),
            password_hash=password_hash,
            role=role.upper(),
            designation=designation,
            department=department,
            employee_id=employee_id,
            phone=phone
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
