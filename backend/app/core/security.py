from datetime import datetime, timedelta, timezone
from typing import Any, Optional

import jwt
from passlib.context import CryptContext

from app.core.config import get_settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_token(
    subject: str,
    *,
    expires_delta: timedelta,
    token_type: str,
    extra_claims: Optional[dict[str, Any]] = None,
) -> str:
    settings = get_settings()
    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "sub": subject,
        "type": token_type,
        "iat": now,
        "exp": now + expires_delta,
    }
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def create_access_token(subject: str, role: str) -> str:
    settings = get_settings()
    return create_token(
        subject,
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
        token_type="access",
        extra_claims={"role": role},
    )


def create_refresh_token(subject: str, role: str) -> str:
    settings = get_settings()
    return create_token(
        subject,
        expires_delta=timedelta(days=settings.refresh_token_expire_days),
        token_type="refresh",
        extra_claims={"role": role},
    )


def decode_token(token: str) -> dict[str, Any]:
    settings = get_settings()
    return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
