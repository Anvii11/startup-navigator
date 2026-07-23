from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)
from app.models.user import User, UserRole
from app.schemas.auth import TokenResponse, UserCreate


class AuthService:
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> User | None:
        return db.scalar(select(User).where(User.email == email.lower()))

    @staticmethod
    def register_user(db: Session, payload: UserCreate) -> User:
        existing = AuthService.get_user_by_email(db, payload.email)
        if existing:
            raise ValueError("Email already registered")

        user = User(
            email=payload.email.lower(),
            password_hash=hash_password(payload.password),
            full_name=payload.full_name.strip(),
            role=UserRole.user,
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def authenticate(db: Session, email: str, password: str) -> User | None:
        user = AuthService.get_user_by_email(db, email)
        if user is None or not verify_password(password, user.password_hash):
            return None
        if not user.is_active:
            return None
        return user

    @staticmethod
    def issue_tokens(user: User) -> TokenResponse:
        subject = str(user.id)
        role = user.role.value
        return TokenResponse(
            access_token=create_access_token(subject, role),
            refresh_token=create_refresh_token(subject, role),
            token_type="bearer",
        )

    @staticmethod
    def ensure_admin_user(db: Session, email: str, password: str, full_name: str = "Admin") -> User:
        user = AuthService.get_user_by_email(db, email)
        if user:
            if user.role != UserRole.admin:
                user.role = UserRole.admin
                db.commit()
                db.refresh(user)
            return user

        user = User(
            email=email.lower(),
            password_hash=hash_password(password),
            full_name=full_name,
            role=UserRole.admin,
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
