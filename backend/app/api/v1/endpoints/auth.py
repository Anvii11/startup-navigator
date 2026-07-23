from fastapi import APIRouter, HTTPException, status
import jwt

from app.core.deps import CurrentUser, DbSession
from app.core.security import decode_token
from app.models.user import User
from app.schemas.auth import (
    TokenRefreshRequest,
    TokenResponse,
    UserCreate,
    UserLogin,
    UserRead,
)
from app.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
)
def register(payload: UserCreate, db: DbSession) -> User:
    try:
        return AuthService.register_user(db, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/login", response_model=TokenResponse)
def login(payload: UserLogin, db: DbSession) -> TokenResponse:
    user = AuthService.authenticate(db, payload.email, payload.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    return AuthService.issue_tokens(user)


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(payload: TokenRefreshRequest, db: DbSession) -> TokenResponse:
    try:
        data = decode_token(payload.refresh_token)
    except jwt.PyJWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        ) from exc

    if data.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    user = db.get(User, int(data["sub"]))
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )
    return AuthService.issue_tokens(user)


@router.get("/me", response_model=UserRead)
def read_me(current_user: CurrentUser) -> User:
    return current_user
