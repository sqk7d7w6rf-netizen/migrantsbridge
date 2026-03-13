"""Wealth building API routes: profiles, goals, savings, investments, assets, dashboard."""

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.core.pagination import PaginatedResponse, PaginationParams
from app.core.security import get_current_user
from app.schemas.wealth import (
    AssetCreate,
    AssetRead,
    AssetUpdate,
    EnrollmentCreate,
    EnrollmentRead,
    EntrepreneurProfileRead,
    EntrepreneurProfileUpdate,
    FinancialProfileRead,
    FinancialProfileUpdate,
    GoalCreate,
    GoalRead,
    GoalUpdate,
    InvestmentCreate,
    InvestmentRead,
    InvestmentUpdate,
    SavingsProgramRead,
    TransactionCreate,
    TransactionRead,
    WealthDashboard,
)
from app.services import wealth_service

router = APIRouter()


# --- Financial Profile ---

@router.get("/profile/{client_id}", response_model=FinancialProfileRead)
async def get_financial_profile(
    client_id: UUID,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """Get a client's financial profile."""
    return await wealth_service.get_financial_profile(session, client_id)


@router.put("/profile/{client_id}", response_model=FinancialProfileRead)
async def update_financial_profile(
    client_id: UUID,
    payload: FinancialProfileUpdate,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """Update a client's financial profile."""
    return await wealth_service.update_financial_profile(session, client_id, payload)


# --- Goals ---

@router.post("/goals", response_model=GoalRead, status_code=201)
async def create_goal(
    payload: GoalCreate,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """Create a financial goal for a client."""
    return await wealth_service.create_goal(session, payload)


@router.get("/goals/{client_id}", response_model=PaginatedResponse[GoalRead])
async def list_goals(
    client_id: UUID,
    pagination: PaginationParams = Depends(),
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """List financial goals for a client."""
    return await wealth_service.list_goals(session, client_id, pagination)


@router.put("/goals/{goal_id}/update", response_model=GoalRead)
async def update_goal(
    goal_id: UUID,
    payload: GoalUpdate,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """Update a financial goal."""
    return await wealth_service.update_goal(session, goal_id, payload)


# --- Savings Programs ---

@router.get("/savings/programs", response_model=PaginatedResponse[SavingsProgramRead])
async def list_savings_programs(
    pagination: PaginationParams = Depends(),
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """List available savings programs."""
    return await wealth_service.list_savings_programs(session, pagination)


@router.post("/savings/enrollments", response_model=EnrollmentRead, status_code=201)
async def create_enrollment(
    payload: EnrollmentCreate,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """Enroll a client in a savings program."""
    return await wealth_service.create_enrollment(session, payload)


@router.get("/savings/enrollments/{client_id}", response_model=PaginatedResponse[EnrollmentRead])
async def list_enrollments(
    client_id: UUID,
    pagination: PaginationParams = Depends(),
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """List savings enrollments for a client."""
    return await wealth_service.list_enrollments(session, client_id, pagination)


@router.post("/savings/transactions", response_model=TransactionRead, status_code=201)
async def create_transaction(
    payload: TransactionCreate,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """Record a savings transaction."""
    return await wealth_service.create_transaction(session, payload)


@router.get(
    "/savings/transactions/{enrollment_id}",
    response_model=PaginatedResponse[TransactionRead],
)
async def list_transactions(
    enrollment_id: UUID,
    pagination: PaginationParams = Depends(),
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """List transactions for a savings enrollment."""
    return await wealth_service.list_transactions(session, enrollment_id, pagination)


# --- Investments ---

@router.post("/investments", response_model=InvestmentRead, status_code=201)
async def create_investment(
    payload: InvestmentCreate,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """Add an investment for a client."""
    return await wealth_service.create_investment(session, payload)


@router.get("/investments/{client_id}", response_model=PaginatedResponse[InvestmentRead])
async def list_investments(
    client_id: UUID,
    pagination: PaginationParams = Depends(),
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """List investments for a client."""
    return await wealth_service.list_investments(session, client_id, pagination)


@router.put("/investments/{investment_id}/update", response_model=InvestmentRead)
async def update_investment(
    investment_id: UUID,
    payload: InvestmentUpdate,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """Update an investment."""
    return await wealth_service.update_investment(session, investment_id, payload)


# --- Entrepreneur Profile ---

@router.get("/entrepreneur/{client_id}", response_model=EntrepreneurProfileRead)
async def get_entrepreneur_profile(
    client_id: UUID,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """Get a client's entrepreneur profile."""
    return await wealth_service.get_entrepreneur_profile(session, client_id)


@router.put("/entrepreneur/{client_id}", response_model=EntrepreneurProfileRead)
async def update_entrepreneur_profile(
    client_id: UUID,
    payload: EntrepreneurProfileUpdate,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """Update a client's entrepreneur profile."""
    return await wealth_service.update_entrepreneur_profile(session, client_id, payload)


# --- Assets ---

@router.post("/assets", response_model=AssetRead, status_code=201)
async def create_asset(
    payload: AssetCreate,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """Add an asset for a client."""
    return await wealth_service.create_asset(session, payload)


@router.get("/assets/{client_id}", response_model=PaginatedResponse[AssetRead])
async def list_assets(
    client_id: UUID,
    pagination: PaginationParams = Depends(),
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """List assets for a client."""
    return await wealth_service.list_assets(session, client_id, pagination)


@router.put("/assets/{asset_id}/update", response_model=AssetRead)
async def update_asset(
    asset_id: UUID,
    payload: AssetUpdate,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """Update an asset."""
    return await wealth_service.update_asset(session, asset_id, payload)


# --- Dashboard ---

@router.get("/dashboard/{client_id}", response_model=WealthDashboard)
async def get_wealth_dashboard(
    client_id: UUID,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """Get aggregated wealth dashboard for a client."""
    return await wealth_service.get_wealth_dashboard(session, client_id)
