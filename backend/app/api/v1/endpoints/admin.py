from fastapi import APIRouter

from app.core.deps import AdminUser
from app.models.user import User
from app.schemas.auth import UserRead

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/ping", response_model=UserRead)
def admin_ping(current_admin: AdminUser) -> User:
    """Smoke-test endpoint for admin role middleware (Phase 1)."""
    return current_admin
