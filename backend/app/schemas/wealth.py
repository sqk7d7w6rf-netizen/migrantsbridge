from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field


class RiskTolerance(str, Enum):
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"


class GoalStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    ACHIEVED = "achieved"
    CANCELLED = "cancelled"


class GoalType(str, Enum):
    EMERGENCY_FUND = "emergency_fund"
    HOME_PURCHASE = "home_purchase"
    EDUCATION = "education"
    RETIREMENT = "retirement"
    BUSINESS = "business"
    DEBT_PAYOFF = "debt_payoff"
    TRAVEL = "travel"
    OTHER = "other"


class EnrollmentStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    WITHDRAWN = "withdrawn"


class TransactionType(str, Enum):
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    INTEREST = "interest"
    FEE = "fee"
    MATCH = "match"


class InvestmentType(str, Enum):
    STOCKS = "stocks"
    BONDS = "bonds"
    MUTUAL_FUND = "mutual_fund"
    ETF = "etf"
    REAL_ESTATE = "real_estate"
    CRYPTO = "crypto"
    SAVINGS = "savings"
    OTHER = "other"


class AssetType(str, Enum):
    REAL_ESTATE = "real_estate"
    VEHICLE = "vehicle"
    BUSINESS = "business"
    JEWELRY = "jewelry"
    EQUIPMENT = "equipment"
    OTHER = "other"


class BusinessStage(str, Enum):
    IDEA = "idea"
    PLANNING = "planning"
    STARTUP = "startup"
    GROWTH = "growth"
    ESTABLISHED = "established"


# --- Financial Profile ---

class FinancialProfileRead(BaseModel):
    id: UUID
    client_id: UUID
    annual_income: Decimal | None = None
    monthly_expenses: Decimal | None = None
    total_debt: Decimal | None = None
    credit_score: int | None = None
    risk_tolerance: RiskTolerance | None = None
    employment_status: str | None = None
    employer_name: str | None = None
    tax_filing_status: str | None = None
    dependents_count: int | None = None
    has_bank_account: bool | None = None
    has_credit_history: bool | None = None
    notes: str | None = None
    updated_at: datetime

    model_config = {"from_attributes": True}


class FinancialProfileUpdate(BaseModel):
    annual_income: Decimal | None = None
    monthly_expenses: Decimal | None = None
    total_debt: Decimal | None = None
    credit_score: int | None = Field(default=None, ge=300, le=850)
    risk_tolerance: RiskTolerance | None = None
    employment_status: str | None = Field(default=None, max_length=100)
    employer_name: str | None = Field(default=None, max_length=255)
    tax_filing_status: str | None = Field(default=None, max_length=50)
    dependents_count: int | None = Field(default=None, ge=0)
    has_bank_account: bool | None = None
    has_credit_history: bool | None = None
    notes: str | None = None


# --- Goals ---

class GoalCreate(BaseModel):
    client_id: UUID
    goal_type: GoalType
    name: str = Field(min_length=1, max_length=255)
    target_amount: Decimal = Field(gt=0, decimal_places=2)
    current_amount: Decimal = Field(default=Decimal("0.00"), ge=0, decimal_places=2)
    target_date: date | None = None
    monthly_contribution: Decimal | None = Field(default=None, ge=0, decimal_places=2)
    notes: str | None = None


class GoalRead(BaseModel):
    id: UUID
    client_id: UUID
    goal_type: GoalType
    name: str
    target_amount: Decimal
    current_amount: Decimal
    target_date: date | None = None
    monthly_contribution: Decimal | None = None
    status: GoalStatus
    progress_percentage: float
    notes: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class GoalUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    target_amount: Decimal | None = Field(default=None, gt=0, decimal_places=2)
    current_amount: Decimal | None = Field(default=None, ge=0, decimal_places=2)
    target_date: date | None = None
    monthly_contribution: Decimal | None = None
    status: GoalStatus | None = None
    notes: str | None = None


# --- Savings Programs ---

class SavingsProgramRead(BaseModel):
    id: UUID
    name: str
    description: str | None = None
    interest_rate: Decimal | None = None
    match_percentage: Decimal | None = None
    min_monthly_deposit: Decimal | None = None
    max_monthly_deposit: Decimal | None = None
    duration_months: int | None = None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class EnrollmentCreate(BaseModel):
    client_id: UUID
    program_id: UUID
    monthly_amount: Decimal = Field(gt=0, decimal_places=2)


class EnrollmentRead(BaseModel):
    id: UUID
    client_id: UUID
    program_id: UUID
    program_name: str | None = None
    monthly_amount: Decimal
    total_deposited: Decimal
    total_matched: Decimal
    status: EnrollmentStatus
    enrolled_at: datetime
    completed_at: datetime | None = None

    model_config = {"from_attributes": True}


# --- Transactions ---

class TransactionCreate(BaseModel):
    enrollment_id: UUID
    transaction_type: TransactionType
    amount: Decimal = Field(gt=0, decimal_places=2)
    description: str | None = None
    reference_number: str | None = Field(default=None, max_length=100)


class TransactionRead(BaseModel):
    id: UUID
    enrollment_id: UUID
    transaction_type: TransactionType
    amount: Decimal
    balance_after: Decimal
    description: str | None = None
    reference_number: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Investments ---

class InvestmentCreate(BaseModel):
    client_id: UUID
    investment_type: InvestmentType
    name: str = Field(min_length=1, max_length=255)
    symbol: str | None = Field(default=None, max_length=20)
    purchase_price: Decimal = Field(gt=0, decimal_places=2)
    quantity: Decimal = Field(gt=0, decimal_places=4)
    purchase_date: date | None = None
    notes: str | None = None


class InvestmentRead(BaseModel):
    id: UUID
    client_id: UUID
    investment_type: InvestmentType
    name: str
    symbol: str | None = None
    purchase_price: Decimal
    current_price: Decimal | None = None
    quantity: Decimal
    total_value: Decimal | None = None
    gain_loss: Decimal | None = None
    gain_loss_percentage: float | None = None
    purchase_date: date | None = None
    notes: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class InvestmentUpdate(BaseModel):
    current_price: Decimal | None = Field(default=None, ge=0, decimal_places=2)
    quantity: Decimal | None = Field(default=None, gt=0, decimal_places=4)
    notes: str | None = None


# --- Entrepreneur Profile ---

class EntrepreneurProfileRead(BaseModel):
    id: UUID
    client_id: UUID
    business_name: str | None = None
    business_type: str | None = None
    business_stage: BusinessStage | None = None
    industry: str | None = None
    ein: str | None = None
    annual_revenue: Decimal | None = None
    employee_count: int | None = None
    has_business_plan: bool
    has_business_license: bool
    funding_needed: Decimal | None = None
    funding_secured: Decimal | None = None
    notes: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class EntrepreneurProfileUpdate(BaseModel):
    business_name: str | None = Field(default=None, max_length=255)
    business_type: str | None = Field(default=None, max_length=100)
    business_stage: BusinessStage | None = None
    industry: str | None = Field(default=None, max_length=100)
    ein: str | None = Field(default=None, max_length=20)
    annual_revenue: Decimal | None = None
    employee_count: int | None = Field(default=None, ge=0)
    has_business_plan: bool | None = None
    has_business_license: bool | None = None
    funding_needed: Decimal | None = None
    funding_secured: Decimal | None = None
    notes: str | None = None


# --- Assets ---

class AssetCreate(BaseModel):
    client_id: UUID
    asset_type: AssetType
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    estimated_value: Decimal = Field(ge=0, decimal_places=2)
    purchase_price: Decimal | None = Field(default=None, ge=0, decimal_places=2)
    purchase_date: date | None = None
    location: str | None = Field(default=None, max_length=255)


class AssetRead(BaseModel):
    id: UUID
    client_id: UUID
    asset_type: AssetType
    name: str
    description: str | None = None
    estimated_value: Decimal
    purchase_price: Decimal | None = None
    purchase_date: date | None = None
    location: str | None = None
    appreciation: Decimal | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AssetUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    estimated_value: Decimal | None = Field(default=None, ge=0, decimal_places=2)
    location: str | None = None


# --- Dashboard ---

class WealthDashboard(BaseModel):
    """Aggregated wealth dashboard for a client."""

    client_id: UUID
    net_worth: Decimal
    total_savings: Decimal
    total_investments_value: Decimal
    total_assets_value: Decimal
    total_debt: Decimal
    monthly_income: Decimal | None = None
    monthly_expenses: Decimal | None = None
    savings_rate: float | None = None
    goals_summary: dict[str, int] = Field(
        default_factory=dict,
        description="Count of goals by status: {active: N, achieved: N, ...}",
    )
    investment_performance: Decimal | None = None
    risk_tolerance: RiskTolerance | None = None
    as_of: datetime
