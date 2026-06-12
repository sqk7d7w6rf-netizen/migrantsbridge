import logging
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from app.config import settings

logger = logging.getLogger("migrantsbridge")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# Sentinel value shipped in config defaults / .env.example. Running with this in
# production would let anyone forge JWTs, so we refuse to start outside DEBUG.
INSECURE_SECRET_KEY = "change-me-in-production"


def validate_production_security() -> None:
    """Fail fast if the app is configured insecurely for a non-debug deployment.

    Called at application startup. In DEBUG mode we only warn, so local dev and
    tests keep working with the placeholder secret.
    """
    if settings.SECRET_KEY == INSECURE_SECRET_KEY:
        message = (
            "SECRET_KEY is set to the insecure default. Set a strong, random "
            "SECRET_KEY before running outside DEBUG mode."
        )
        if settings.DEBUG:
            logger.warning("%s (allowed because DEBUG=True)", message)
        else:
            raise RuntimeError(message)


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


def create_access_token(subject: str | UUID, extra_claims: dict[str, Any] | None = None) -> str:
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    claims: dict[str, Any] = {
        "sub": str(subject),
        "iat": now,
        "exp": expire,
        "type": "access",
    }
    if extra_claims:
        claims.update(extra_claims)
    return jwt.encode(claims, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(subject: str | UUID) -> str:
    now = datetime.now(timezone.utc)
    expire = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    claims: dict[str, Any] = {
        "sub": str(subject),
        "iat": now,
        "exp": expire,
        "type": "refresh",
    }
    return jwt.encode(claims, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict[str, Any]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Decode token and return user from DB. Imported in dependencies.py for full implementation."""
    from app.dependencies import resolve_current_user

    return await resolve_current_user(token)


def require_permission(*permissions: str):
    """Dependency factory that checks if current user has all the specified permissions."""

    async def _check_permissions(
        token: str = Depends(oauth2_scheme),
    ):
        from app.dependencies import resolve_current_user_with_permissions

        user, user_permissions = await resolve_current_user_with_permissions(token)
        missing = set(permissions) - set(user_permissions)
        if missing:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing permissions: {', '.join(sorted(missing))}",
            )
        return user

    return _check_permissions
