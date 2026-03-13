"""Authentication API routes."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.core.security import get_current_user
from app.schemas.auth import (
    ChangePasswordRequest,
    LoginRequest,
    RefreshTokenRequest,
    TokenResponse,
    UserCreate,
    UserRead,
    UserUpdate,
)
from app.schemas.common import SuccessResponse
from app.services import auth_service

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
async def login(
    payload: LoginRequest,
    session: AsyncSession = Depends(get_async_session),
):
    """Authenticate user and return JWT tokens."""
    return await auth_service.authenticate(session, payload)


@router.post("/register", response_model=UserRead, status_code=201)
async def register(
    payload: UserCreate,
    session: AsyncSession = Depends(get_async_session),
):
    """Register a new user account."""
    return await auth_service.create_user(session, payload)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    payload: RefreshTokenRequest,
    session: AsyncSession = Depends(get_async_session),
):
    """Refresh an access token using a valid refresh token."""
    return await auth_service.refresh_token(session, payload.refresh_token)


@router.get("/me", response_model=UserRead)
async def get_me(
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Get the current authenticated user's profile."""
    return await auth_service.get_user_by_id(session, current_user.id)


@router.put("/me", response_model=UserRead)
async def update_me(
    payload: UserUpdate,
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Update the current user's profile."""
    return await auth_service.update_user(session, current_user.id, payload)


@router.post("/change-password", response_model=SuccessResponse)
async def change_password(
    payload: ChangePasswordRequest,
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Change the current user's password."""
    await auth_service.change_password(session, current_user.id, payload)
    return SuccessResponse(message="Password changed successfully")
