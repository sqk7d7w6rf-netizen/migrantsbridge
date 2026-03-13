import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.constants import EmploymentStatus, SavingsTransactionType
from app.core.database import Base
from app.models.base import TimestampMixin


class FinancialProfile(TimestampMixin, Base):
    __tablename__ = "financial_profiles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("clients.id", ondelete="CASCADE"), nullable=False, unique=True, index=True
    )
    financial_literacy_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    employment_status: Mapped[EmploymentStatus | None] = mapped_column(nullable=True)
    employer_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    monthly_income: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    monthly_expenses: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    has_bank_account: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    has_credit_history: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    credit_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    total_debt: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    total_assets: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    client: Mapped["Client"] = relationship(back_populates="financial_profile", lazy="selectin")  # noqa: F821
    goals: Mapped[list["FinancialGoal"]] = relationship(
        back_populates="financial_profile", cascade="all, delete-orphan", lazy="noload"
    )
    assets: Mapped[list["AssetRecord"]] = relationship(
        back_populates="financial_profile", cascade="all, delete-orphan", lazy="noload"
    )
    investments: Mapped[list["InvestmentRecord"]] = relationship(
        back_populates="financial_profile", cascade="all, delete-orphan", lazy="noload"
    )


class FinancialGoal(TimestampMixin, Base):
    __tablename__ = "financial_goals"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    financial_profile_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("financial_profiles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    target_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    current_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"), nullable=False)
    target_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    is_achieved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    achieved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    financial_profile: Mapped["FinancialProfile"] = relationship(back_populates="goals")


class SavingsProgram(TimestampMixin, Base):
    __tablename__ = "savings_programs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    match_percentage: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    max_match_amount: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    min_monthly_deposit: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    duration_months: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    eligibility_criteria: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    enrollments: Mapped[list["SavingsEnrollment"]] = relationship(
        back_populates="program", cascade="all, delete-orphan", lazy="noload"
    )


class SavingsEnrollment(TimestampMixin, Base):
    __tablename__ = "savings_enrollments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    program_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("savings_programs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    client_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("clients.id", ondelete="CASCADE"), nullable=False, index=True
    )
    enrolled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    balance: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"), nullable=False)
    matched_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"), nullable=False)

    program: Mapped["SavingsProgram"] = relationship(back_populates="enrollments", lazy="selectin")
    client: Mapped["Client"] = relationship(lazy="selectin")  # noqa: F821
    transactions: Mapped[list["SavingsTransaction"]] = relationship(
        back_populates="enrollment", cascade="all, delete-orphan", lazy="noload"
    )


class SavingsTransaction(TimestampMixin, Base):
    __tablename__ = "savings_transactions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    enrollment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("savings_enrollments.id", ondelete="CASCADE"), nullable=False, index=True
    )
    transaction_type: Mapped[SavingsTransactionType] = mapped_column(nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    balance_after: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    transaction_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    enrollment: Mapped["SavingsEnrollment"] = relationship(back_populates="transactions")


class InvestmentRecord(TimestampMixin, Base):
    __tablename__ = "investment_records"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    financial_profile_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("financial_profiles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    investment_type: Mapped[str] = mapped_column(String(100), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    amount_invested: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    current_value: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    institution: Mapped[str | None] = mapped_column(String(255), nullable=True)
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    maturity_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    financial_profile: Mapped["FinancialProfile"] = relationship(back_populates="investments")


class EntrepreneurProfile(TimestampMixin, Base):
    __tablename__ = "entrepreneur_profiles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("clients.id", ondelete="CASCADE"), nullable=False, unique=True, index=True
    )
    business_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    business_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    business_stage: Mapped[str | None] = mapped_column(String(100), nullable=True)
    industry: Mapped[str | None] = mapped_column(String(100), nullable=True)
    business_plan_submitted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    has_ein: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    has_business_license: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    annual_revenue: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    employee_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    funding_received: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    funding_sources: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    mentorship_needs: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    client: Mapped["Client"] = relationship(lazy="selectin")  # noqa: F821


class AssetRecord(TimestampMixin, Base):
    __tablename__ = "asset_records"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    financial_profile_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("financial_profiles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    asset_type: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    estimated_value: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    acquisition_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    financial_profile: Mapped["FinancialProfile"] = relationship(back_populates="assets")
