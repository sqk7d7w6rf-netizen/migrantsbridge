"""Authentication and user management service."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.config import settings
from app.models.user import Role, User
from app.schemas.auth import (
    ChangePasswordRequest,
    LoginRequest,
    TokenResponse,
    UserCreate,
    UserRead,
    UserUpdate,
)


async def authenticate(session: AsyncSession, payload: LoginRequest) -> TokenResponse:
    """Authenticate user and return JWT tokens."""
    result = await session.execute(
        select(User).where(User.email == payload.email, User.is_deleted == False)
    )
    user = result.scalar_one_or_none()

    if user is None or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated",
        )

    # Update last login
    user.last_login_at = datetime.now(timezone.utc)
    session.add(user)

    extra_claims = {}
    if user.role:
        extra_claims["role"] = user.role.name

    access_token = create_access_token(user.id, extra_claims)
    refresh_token = create_refresh_token(user.id)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


async def create_user(session: AsyncSession, payload: UserCreate) -> UserRead:
    """Register a new user."""
    existing = await session.execute(
        select(User).where(User.email == payload.email, User.is_deleted == False)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists",
        )

    user = User(
        email=payload.email,
        hashed_password=hash_password(payload.password),
        first_name=payload.first_name,
        last_name=payload.last_name,
        phone=payload.phone,
        role_id=payload.role_id,
        is_active=True,
    )
    session.add(user)
    await session.flush()
    await session.refresh(user)

    role_name = user.role.name if user.role else None

    return UserRead(
        id=user.id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        phone=user.phone,
        role_id=user.role_id,
        role_name=role_name,
        is_active=user.is_active,
        last_login=user.last_login_at,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


async def create_tokens(user_id: UUID, role_name: str | None = None) -> TokenResponse:
    """Create fresh token pair for a user."""
    extra_claims = {}
    if role_name:
        extra_claims["role"] = role_name

    access_token = create_access_token(user_id, extra_claims)
    refresh_token = create_refresh_token(user_id)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


async def refresh_token(session: AsyncSession, token: str) -> TokenResponse:
    """Validate a refresh token and issue new token pair."""
    payload = decode_token(token)

    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type; expected refresh token",
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    result = await session.execute(
        select(User).where(User.id == user_id, User.is_active == True, User.is_deleted == False)
    )
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    role_name = user.role.name if user.role else None
    return await create_tokens(user.id, role_name)


async def change_password(
    session: AsyncSession,
    user_id: UUID,
    payload: ChangePasswordRequest,
) -> None:
    """Change a user's password after verifying the current one."""
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if not verify_password(payload.current_password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )

    user.hashed_password = hash_password(payload.new_password)
    session.add(user)


async def get_user_by_id(session: AsyncSession, user_id: UUID) -> User:
    """Fetch a user by ID. Raises 404 if not found."""
    result = await session.execute(
        select(User).where(User.id == user_id, User.is_deleted == False)
    )
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


async def update_user(session: AsyncSession, user_id: UUID, payload: UserUpdate) -> UserRead:
    """Update user profile fields."""
    user = await get_user_by_id(session, user_id)

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)

    session.add(user)
    await session.flush()
    await session.refresh(user)

    role_name = user.role.name if user.role else None

    return UserRead(
        id=user.id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        phone=user.phone,
        role_id=user.role_id,
        role_name=role_name,
        is_active=user.is_active,
        last_login=user.last_login_at,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )
