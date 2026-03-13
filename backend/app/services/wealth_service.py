"""Wealth building service: profiles, goals, savings, investments, assets, dashboard."""

from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants import SavingsTransactionType
from app.core.pagination import PaginatedResponse, PaginationParams, paginate
from app.models.wealth import (
    AssetRecord,
    EntrepreneurProfile,
    FinancialGoal,
    FinancialProfile,
    InvestmentRecord,
    SavingsEnrollment,
    SavingsProgram,
    SavingsTransaction,
)
from app.models.client import Client
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
    TransactionType,
    WealthDashboard,
)


# --- Financial Profile ---

def _to_profile_read(profile: FinancialProfile) -> FinancialProfileRead:
    """Map FinancialProfile model to schema."""
    return FinancialProfileRead(
        id=profile.id,
        client_id=profile.client_id,
        annual_income=profile.monthly_income * 12 if profile.monthly_income else None,
        monthly_expenses=profile.monthly_expenses,
        total_debt=profile.total_debt,
        credit_score=profile.credit_score,
        risk_tolerance=None,
        employment_status=profile.employment_status.value if profile.employment_status else None,
        employer_name=profile.employer_name,
        tax_filing_status=None,
        dependents_count=None,
        has_bank_account=profile.has_bank_account,
        has_credit_history=profile.has_credit_history,
        notes=profile.notes,
        updated_at=profile.updated_at,
    )


async def get_financial_profile(session: AsyncSession, client_id: UUID) -> FinancialProfileRead:
    """Get or create a financial profile for a client."""
    result = await session.execute(
        select(FinancialProfile).where(FinancialProfile.client_id == client_id)
    )
    profile = result.scalar_one_or_none()
    if profile is None:
        # Auto-create empty profile
        profile = FinancialProfile(client_id=client_id)
        session.add(profile)
        await session.flush()
        await session.refresh(profile)
    return _to_profile_read(profile)


async def _get_or_create_profile(session: AsyncSession, client_id: UUID) -> FinancialProfile:
    """Get or create the raw FinancialProfile model."""
    result = await session.execute(
        select(FinancialProfile).where(FinancialProfile.client_id == client_id)
    )
    profile = result.scalar_one_or_none()
    if profile is None:
        profile = FinancialProfile(client_id=client_id)
        session.add(profile)
        await session.flush()
        await session.refresh(profile)
    return profile


async def update_financial_profile(
    session: AsyncSession, client_id: UUID, payload: FinancialProfileUpdate
) -> FinancialProfileRead:
    """Update a client's financial profile."""
    profile = await _get_or_create_profile(session, client_id)

    update_data = payload.model_dump(exclude_unset=True)

    # Map annual_income to monthly_income
    if "annual_income" in update_data and update_data["annual_income"] is not None:
        profile.monthly_income = update_data.pop("annual_income") / 12

    # Skip fields that don't exist on model
    skip_fields = {"risk_tolerance", "tax_filing_status", "dependents_count", "annual_income"}
    for field, value in update_data.items():
        if field in skip_fields:
            continue
        if hasattr(profile, field):
            setattr(profile, field, value)

    session.add(profile)
    await session.flush()
    await session.refresh(profile)
    return _to_profile_read(profile)


# --- Goals ---

def _to_goal_read(goal: FinancialGoal) -> GoalRead:
    """Map FinancialGoal model to GoalRead schema."""
    progress = 0.0
    if goal.target_amount and goal.target_amount > 0:
        progress = float(goal.current_amount / goal.target_amount * 100)

    goal_status = "achieved" if goal.is_achieved else "active"

    return GoalRead(
        id=goal.id,
        client_id=goal.financial_profile.client_id if goal.financial_profile else UUID("00000000-0000-0000-0000-000000000000"),
        goal_type="other",
        name=goal.name,
        target_amount=goal.target_amount,
        current_amount=goal.current_amount,
        target_date=goal.target_date,
        monthly_contribution=None,
        status=goal_status,
        progress_percentage=progress,
        notes=goal.description,
        created_at=goal.created_at,
        updated_at=goal.updated_at,
    )


async def create_goal(session: AsyncSession, payload: GoalCreate) -> GoalRead:
    """Create a financial goal."""
    profile = await _get_or_create_profile(session, payload.client_id)

    goal = FinancialGoal(
        financial_profile_id=profile.id,
        name=payload.name,
        description=payload.notes,
        target_amount=payload.target_amount,
        current_amount=payload.current_amount,
        target_date=payload.target_date,
        is_achieved=False,
    )
    session.add(goal)
    await session.flush()
    await session.refresh(goal)

    # Manually build the read since relationship may not be loaded
    progress = 0.0
    if payload.target_amount and payload.target_amount > 0:
        progress = float(payload.current_amount / payload.target_amount * 100)

    return GoalRead(
        id=goal.id,
        client_id=payload.client_id,
        goal_type=payload.goal_type.value,
        name=goal.name,
        target_amount=goal.target_amount,
        current_amount=goal.current_amount,
        target_date=goal.target_date,
        monthly_contribution=payload.monthly_contribution,
        status="active",
        progress_percentage=progress,
        notes=goal.description,
        created_at=goal.created_at,
        updated_at=goal.updated_at,
    )


async def get_goal(session: AsyncSession, goal_id: UUID) -> GoalRead:
    result = await session.execute(select(FinancialGoal).where(FinancialGoal.id == goal_id))
    goal = result.scalar_one_or_none()
    if goal is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")
    return _to_goal_read(goal)


async def list_goals(
    session: AsyncSession, client_id: UUID, pagination: PaginationParams
) -> PaginatedResponse[GoalRead]:
    profile = await _get_or_create_profile(session, client_id)
    query = (
        select(FinancialGoal)
        .where(FinancialGoal.financial_profile_id == profile.id)
        .order_by(FinancialGoal.created_at.desc())
    )
    result = await paginate(session, query, pagination)
    result.items = [_to_goal_read(g) for g in result.items]
    return result


async def update_goal(session: AsyncSession, goal_id: UUID, payload: GoalUpdate) -> GoalRead:
    result = await session.execute(select(FinancialGoal).where(FinancialGoal.id == goal_id))
    goal = result.scalar_one_or_none()
    if goal is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")

    update_data = payload.model_dump(exclude_unset=True)

    if "name" in update_data and update_data["name"]:
        goal.name = update_data["name"]
    if "target_amount" in update_data and update_data["target_amount"] is not None:
        goal.target_amount = update_data["target_amount"]
    if "current_amount" in update_data and update_data["current_amount"] is not None:
        goal.current_amount = update_data["current_amount"]
    if "target_date" in update_data:
        goal.target_date = update_data["target_date"]
    if "notes" in update_data:
        goal.description = update_data["notes"]

    if "status" in update_data and update_data["status"] is not None:
        status_val = update_data["status"].value if hasattr(update_data["status"], "value") else update_data["status"]
        goal.is_achieved = status_val == "achieved"
        if goal.is_achieved and not goal.achieved_at:
            goal.achieved_at = datetime.now(timezone.utc)

    # Auto-mark as achieved
    if goal.current_amount >= goal.target_amount and not goal.is_achieved:
        goal.is_achieved = True
        goal.achieved_at = datetime.now(timezone.utc)

    session.add(goal)
    await session.flush()
    await session.refresh(goal)
    return _to_goal_read(goal)


# --- Savings Programs ---

async def list_savings_programs(
    session: AsyncSession, pagination: PaginationParams, active_only: bool = True
) -> PaginatedResponse[SavingsProgramRead]:
    query = select(SavingsProgram)
    if active_only:
        query = query.where(SavingsProgram.is_active == True)
    query = query.order_by(SavingsProgram.name.asc())
    return await paginate(session, query, pagination, SavingsProgramRead)


def _to_enrollment_read(enrollment: SavingsEnrollment) -> EnrollmentRead:
    """Map SavingsEnrollment model to schema."""
    return EnrollmentRead(
        id=enrollment.id,
        client_id=enrollment.client_id,
        program_id=enrollment.program_id,
        program_name=enrollment.program.name if enrollment.program else None,
        monthly_amount=enrollment.balance,  # Use balance as proxy
        total_deposited=enrollment.balance,
        total_matched=enrollment.matched_amount,
        status="active" if enrollment.is_active else "completed",
        enrolled_at=enrollment.enrolled_at,
        completed_at=enrollment.completed_at,
    )


async def create_enrollment(session: AsyncSession, payload: EnrollmentCreate) -> EnrollmentRead:
    """Enroll a client in a savings program."""
    # Verify program
    prog_result = await session.execute(
        select(SavingsProgram).where(SavingsProgram.id == payload.program_id, SavingsProgram.is_active == True)
    )
    program = prog_result.scalar_one_or_none()
    if program is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Savings program not found or inactive")

    # Validate monthly amount against min deposit
    if program.min_monthly_deposit and payload.monthly_amount < program.min_monthly_deposit:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Monthly amount must be at least {program.min_monthly_deposit}",
        )

    enrollment = SavingsEnrollment(
        client_id=payload.client_id,
        program_id=payload.program_id,
        balance=Decimal("0.00"),
        matched_amount=Decimal("0.00"),
        is_active=True,
        enrolled_at=datetime.now(timezone.utc),
    )
    session.add(enrollment)
    await session.flush()
    await session.refresh(enrollment)

    return EnrollmentRead(
        id=enrollment.id,
        client_id=enrollment.client_id,
        program_id=enrollment.program_id,
        program_name=program.name,
        monthly_amount=payload.monthly_amount,
        total_deposited=Decimal("0.00"),
        total_matched=Decimal("0.00"),
        status="active",
        enrolled_at=enrollment.enrolled_at,
        completed_at=enrollment.completed_at,
    )


async def list_enrollments(
    session: AsyncSession, client_id: UUID, pagination: PaginationParams
) -> PaginatedResponse[EnrollmentRead]:
    query = (
        select(SavingsEnrollment)
        .where(SavingsEnrollment.client_id == client_id)
        .order_by(SavingsEnrollment.enrolled_at.desc())
    )
    result = await paginate(session, query, pagination)
    result.items = [_to_enrollment_read(e) for e in result.items]
    return result


# --- Transactions ---

async def create_transaction(session: AsyncSession, payload: TransactionCreate) -> TransactionRead:
    """Record a savings transaction."""
    enroll_result = await session.execute(
        select(SavingsEnrollment).where(SavingsEnrollment.id == payload.enrollment_id)
    )
    enrollment = enroll_result.scalar_one_or_none()
    if enrollment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Enrollment not found")

    if not enrollment.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Enrollment is not active")

    # Map schema TransactionType to model SavingsTransactionType
    type_map = {
        TransactionType.DEPOSIT: SavingsTransactionType.DEPOSIT,
        TransactionType.WITHDRAWAL: SavingsTransactionType.WITHDRAWAL,
        TransactionType.INTEREST: SavingsTransactionType.INTEREST,
        TransactionType.FEE: SavingsTransactionType.FEE,
        TransactionType.MATCH: SavingsTransactionType.MATCH,
    }
    model_type = type_map.get(payload.transaction_type, SavingsTransactionType.DEPOSIT)

    # Calculate new balance
    if payload.transaction_type in (TransactionType.DEPOSIT, TransactionType.INTEREST, TransactionType.MATCH):
        enrollment.balance += payload.amount
        if payload.transaction_type == TransactionType.MATCH:
            enrollment.matched_amount += payload.amount
    elif payload.transaction_type in (TransactionType.WITHDRAWAL, TransactionType.FEE):
        if payload.amount > enrollment.balance:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient balance")
        enrollment.balance -= payload.amount

    balance_after = enrollment.balance

    txn = SavingsTransaction(
        enrollment_id=payload.enrollment_id,
        transaction_type=model_type,
        amount=payload.amount,
        balance_after=balance_after,
        description=payload.description,
        transaction_date=datetime.now(timezone.utc),
    )
    session.add(txn)
    session.add(enrollment)
    await session.flush()
    await session.refresh(txn)

    return TransactionRead(
        id=txn.id,
        enrollment_id=txn.enrollment_id,
        transaction_type=payload.transaction_type,
        amount=txn.amount,
        balance_after=txn.balance_after,
        description=txn.description,
        reference_number=None,
        created_at=txn.created_at,
    )


async def list_transactions(
    session: AsyncSession, enrollment_id: UUID, pagination: PaginationParams
) -> PaginatedResponse[TransactionRead]:
    query = (
        select(SavingsTransaction)
        .where(SavingsTransaction.enrollment_id == enrollment_id)
        .order_by(SavingsTransaction.created_at.desc())
    )
    return await paginate(session, query, pagination, TransactionRead)


# --- Investments ---

async def create_investment(session: AsyncSession, payload: InvestmentCreate) -> InvestmentRead:
    profile = await _get_or_create_profile(session, payload.client_id)

    inv = InvestmentRecord(
        financial_profile_id=profile.id,
        investment_type=payload.investment_type.value,
        name=payload.name,
        amount_invested=payload.purchase_price * payload.quantity,
        current_value=payload.purchase_price * payload.quantity,
        institution=None,
        start_date=payload.purchase_date,
        notes=payload.notes,
    )
    session.add(inv)
    await session.flush()
    await session.refresh(inv)

    return InvestmentRead(
        id=inv.id,
        client_id=payload.client_id,
        investment_type=payload.investment_type,
        name=inv.name,
        symbol=payload.symbol,
        purchase_price=payload.purchase_price,
        current_price=payload.purchase_price,
        quantity=payload.quantity,
        total_value=inv.current_value,
        gain_loss=Decimal("0.00"),
        gain_loss_percentage=0.0,
        purchase_date=payload.purchase_date,
        notes=inv.notes,
        created_at=inv.created_at,
        updated_at=inv.updated_at,
    )


async def list_investments(
    session: AsyncSession, client_id: UUID, pagination: PaginationParams
) -> PaginatedResponse[InvestmentRead]:
    profile = await _get_or_create_profile(session, client_id)
    query = (
        select(InvestmentRecord)
        .where(InvestmentRecord.financial_profile_id == profile.id)
        .order_by(InvestmentRecord.created_at.desc())
    )
    result = await paginate(session, query, pagination)
    items = []
    for inv in result.items:
        gain_loss = inv.current_value - inv.amount_invested
        gain_pct = float(gain_loss / inv.amount_invested * 100) if inv.amount_invested > 0 else 0.0
        items.append(InvestmentRead(
            id=inv.id,
            client_id=client_id,
            investment_type=inv.investment_type,
            name=inv.name,
            symbol=None,
            purchase_price=inv.amount_invested,
            current_price=inv.current_value,
            quantity=Decimal("1"),
            total_value=inv.current_value,
            gain_loss=gain_loss,
            gain_loss_percentage=gain_pct,
            purchase_date=inv.start_date,
            notes=inv.notes,
            created_at=inv.created_at,
            updated_at=inv.updated_at,
        ))
    result.items = items
    return result


async def update_investment(
    session: AsyncSession, investment_id: UUID, payload: InvestmentUpdate
) -> InvestmentRead:
    result = await session.execute(
        select(InvestmentRecord).where(InvestmentRecord.id == investment_id)
    )
    inv = result.scalar_one_or_none()
    if inv is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Investment not found")

    update_data = payload.model_dump(exclude_unset=True)

    if "current_price" in update_data and update_data["current_price"] is not None:
        # Update current_value based on new price (use amount_invested as basis)
        inv.current_value = update_data["current_price"]

    if "notes" in update_data:
        inv.notes = update_data["notes"]

    session.add(inv)
    await session.flush()
    await session.refresh(inv)

    gain_loss = inv.current_value - inv.amount_invested
    gain_pct = float(gain_loss / inv.amount_invested * 100) if inv.amount_invested > 0 else 0.0

    # Get client_id from profile
    profile = inv.financial_profile
    client_id = profile.client_id if profile else UUID("00000000-0000-0000-0000-000000000000")

    return InvestmentRead(
        id=inv.id,
        client_id=client_id,
        investment_type=inv.investment_type,
        name=inv.name,
        symbol=None,
        purchase_price=inv.amount_invested,
        current_price=inv.current_value,
        quantity=Decimal("1"),
        total_value=inv.current_value,
        gain_loss=gain_loss,
        gain_loss_percentage=gain_pct,
        purchase_date=inv.start_date,
        notes=inv.notes,
        created_at=inv.created_at,
        updated_at=inv.updated_at,
    )


# --- Entrepreneur Profile ---

def _to_entrepreneur_read(ep: EntrepreneurProfile) -> EntrepreneurProfileRead:
    """Map EntrepreneurProfile model to schema."""
    return EntrepreneurProfileRead(
        id=ep.id,
        client_id=ep.client_id,
        business_name=ep.business_name,
        business_type=ep.business_type,
        business_stage=ep.business_stage,
        industry=ep.industry,
        ein=None,
        annual_revenue=ep.annual_revenue,
        employee_count=ep.employee_count,
        has_business_plan=ep.business_plan_submitted,
        has_business_license=ep.has_business_license,
        funding_needed=None,
        funding_secured=ep.funding_received,
        notes=ep.notes,
        created_at=ep.created_at,
        updated_at=ep.updated_at,
    )


async def get_entrepreneur_profile(session: AsyncSession, client_id: UUID) -> EntrepreneurProfileRead:
    result = await session.execute(
        select(EntrepreneurProfile).where(EntrepreneurProfile.client_id == client_id)
    )
    profile = result.scalar_one_or_none()
    if profile is None:
        profile = EntrepreneurProfile(
            client_id=client_id,
            business_plan_submitted=False,
            has_ein=False,
            has_business_license=False,
        )
        session.add(profile)
        await session.flush()
        await session.refresh(profile)
    return _to_entrepreneur_read(profile)


async def update_entrepreneur_profile(
    session: AsyncSession, client_id: UUID, payload: EntrepreneurProfileUpdate
) -> EntrepreneurProfileRead:
    result = await session.execute(
        select(EntrepreneurProfile).where(EntrepreneurProfile.client_id == client_id)
    )
    profile = result.scalar_one_or_none()
    if profile is None:
        profile = EntrepreneurProfile(
            client_id=client_id,
            business_plan_submitted=False,
            has_ein=False,
            has_business_license=False,
        )
        session.add(profile)
        await session.flush()

    update_data = payload.model_dump(exclude_unset=True)

    field_map = {
        "has_business_plan": "business_plan_submitted",
        "funding_secured": "funding_received",
    }
    skip_fields = {"ein", "funding_needed"}

    for field, value in update_data.items():
        if field in skip_fields:
            continue
        model_field = field_map.get(field, field)
        if hasattr(profile, model_field):
            setattr(profile, model_field, value)

    session.add(profile)
    await session.flush()
    await session.refresh(profile)
    return _to_entrepreneur_read(profile)


# --- Assets ---

def _to_asset_read(asset: AssetRecord, client_id: UUID | None = None) -> AssetRead:
    """Map AssetRecord model to schema."""
    return AssetRead(
        id=asset.id,
        client_id=client_id or UUID("00000000-0000-0000-0000-000000000000"),
        asset_type=asset.asset_type,
        name=asset.description[:255] if asset.description else "",
        description=asset.description,
        estimated_value=asset.estimated_value,
        purchase_price=None,
        purchase_date=asset.acquisition_date,
        location=None,
        appreciation=None,
        created_at=asset.created_at,
        updated_at=asset.updated_at,
    )


async def create_asset(session: AsyncSession, payload: AssetCreate) -> AssetRead:
    profile = await _get_or_create_profile(session, payload.client_id)

    asset = AssetRecord(
        financial_profile_id=profile.id,
        asset_type=payload.asset_type.value,
        description=payload.description or payload.name,
        estimated_value=payload.estimated_value,
        acquisition_date=payload.purchase_date,
        notes=None,
    )
    session.add(asset)
    await session.flush()
    await session.refresh(asset)
    return _to_asset_read(asset, payload.client_id)


async def list_assets(
    session: AsyncSession, client_id: UUID, pagination: PaginationParams
) -> PaginatedResponse[AssetRead]:
    profile = await _get_or_create_profile(session, client_id)
    query = (
        select(AssetRecord)
        .where(AssetRecord.financial_profile_id == profile.id)
        .order_by(AssetRecord.created_at.desc())
    )
    result = await paginate(session, query, pagination)
    result.items = [_to_asset_read(a, client_id) for a in result.items]
    return result


async def update_asset(session: AsyncSession, asset_id: UUID, payload: AssetUpdate) -> AssetRead:
    result = await session.execute(
        select(AssetRecord).where(AssetRecord.id == asset_id)
    )
    asset = result.scalar_one_or_none()
    if asset is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")

    update_data = payload.model_dump(exclude_unset=True)

    if "name" in update_data and update_data["name"]:
        asset.description = update_data.get("description") or update_data["name"]
    if "description" in update_data:
        asset.description = update_data["description"]
    if "estimated_value" in update_data and update_data["estimated_value"] is not None:
        asset.estimated_value = update_data["estimated_value"]

    session.add(asset)
    await session.flush()
    await session.refresh(asset)

    # Get client_id from profile
    profile = asset.financial_profile
    client_id = profile.client_id if profile else None

    return _to_asset_read(asset, client_id)


# --- Dashboard ---

async def get_wealth_dashboard(session: AsyncSession, client_id: UUID) -> WealthDashboard:
    """Aggregate wealth data for a client dashboard."""
    # Financial profile
    profile_read = await get_financial_profile(session, client_id)
    profile = await _get_or_create_profile(session, client_id)

    # Total savings
    savings_result = await session.execute(
        select(func.coalesce(func.sum(SavingsEnrollment.balance), Decimal("0.00")))
        .where(SavingsEnrollment.client_id == client_id)
    )
    total_savings = savings_result.scalar_one()

    # Total investments
    inv_result = await session.execute(
        select(func.coalesce(func.sum(InvestmentRecord.current_value), Decimal("0.00")))
        .where(InvestmentRecord.financial_profile_id == profile.id)
    )
    total_investments = inv_result.scalar_one()

    # Investment performance (total gain/loss)
    inv_cost_result = await session.execute(
        select(func.coalesce(func.sum(InvestmentRecord.amount_invested), Decimal("0.00")))
        .where(InvestmentRecord.financial_profile_id == profile.id)
    )
    total_cost = inv_cost_result.scalar_one()
    investment_performance = total_investments - total_cost

    # Total assets
    asset_result = await session.execute(
        select(func.coalesce(func.sum(AssetRecord.estimated_value), Decimal("0.00")))
        .where(AssetRecord.financial_profile_id == profile.id)
    )
    total_assets = asset_result.scalar_one()

    # Goals summary
    goals_result = await session.execute(
        select(FinancialGoal.is_achieved, func.count(FinancialGoal.id))
        .where(FinancialGoal.financial_profile_id == profile.id)
        .group_by(FinancialGoal.is_achieved)
    )
    goals_summary: dict[str, int] = {}
    for row in goals_result.all():
        key = "achieved" if row[0] else "active"
        goals_summary[key] = row[1]

    total_debt = profile_read.total_debt or Decimal("0.00")
    net_worth = total_savings + total_investments + total_assets - total_debt

    savings_rate = None
    monthly_income = profile.monthly_income
    if monthly_income and monthly_income > 0 and profile.monthly_expenses:
        savings_rate = float((monthly_income - profile.monthly_expenses) / monthly_income * 100)

    return WealthDashboard(
        client_id=client_id,
        net_worth=net_worth,
        total_savings=total_savings,
        total_investments_value=total_investments,
        total_assets_value=total_assets,
        total_debt=total_debt,
        monthly_income=monthly_income,
        monthly_expenses=profile.monthly_expenses,
        savings_rate=savings_rate,
        goals_summary=goals_summary,
        investment_performance=investment_performance,
        risk_tolerance=None,
        as_of=datetime.now(timezone.utc),
    )
