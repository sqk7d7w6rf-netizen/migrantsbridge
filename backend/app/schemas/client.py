from datetime import date, datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    NON_BINARY = "non_binary"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"


class ImmigrationStatus(str, Enum):
    CITIZEN = "citizen"
    PERMANENT_RESIDENT = "permanent_resident"
    REFUGEE = "refugee"
    ASYLUM_SEEKER = "asylum_seeker"
    WORK_VISA = "work_visa"
    STUDENT_VISA = "student_visa"
    UNDOCUMENTED = "undocumented"
    TPS = "tps"
    DACA = "daca"
    OTHER = "other"


class ClientLanguageCreate(BaseModel):
    """Add a language to a client."""

    language_code: str = Field(min_length=2, max_length=10)
    proficiency: str = Field(default="conversational", max_length=50)
    is_primary: bool = False


class ClientLanguageRead(BaseModel):
    """Language association read."""

    id: UUID
    language_code: str
    proficiency: str
    is_primary: bool

    model_config = {"from_attributes": True}


class ClientCreate(BaseModel):
    """Client registration payload."""

    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=20)
    date_of_birth: date | None = None
    gender: Gender | None = None
    country_of_origin: str | None = Field(default=None, max_length=100)
    immigration_status: ImmigrationStatus | None = None
    address_line1: str | None = Field(default=None, max_length=255)
    address_line2: str | None = Field(default=None, max_length=255)
    city: str | None = Field(default=None, max_length=100)
    state: str | None = Field(default=None, max_length=100)
    zip_code: str | None = Field(default=None, max_length=20)
    preferred_language: str = Field(default="en", max_length=10)
    emergency_contact_name: str | None = Field(default=None, max_length=200)
    emergency_contact_phone: str | None = Field(default=None, max_length=20)
    notes: str | None = None
    languages: list[ClientLanguageCreate] = Field(default_factory=list)


class ClientRead(BaseModel):
    """Client read response."""

    id: UUID
    client_number: str
    first_name: str
    last_name: str
    email: str | None = None
    phone: str | None = None
    date_of_birth: date | None = None
    gender: Gender | None = None
    country_of_origin: str | None = None
    immigration_status: ImmigrationStatus | None = None
    address_line1: str | None = None
    address_line2: str | None = None
    city: str | None = None
    state: str | None = None
    zip_code: str | None = None
    preferred_language: str
    emergency_contact_name: str | None = None
    emergency_contact_phone: str | None = None
    notes: str | None = None
    is_active: bool
    languages: list[ClientLanguageRead] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @property
    def full_address(self) -> str | None:
        parts = [self.address_line1, self.address_line2, self.city, self.state, self.zip_code]
        filtered = [p for p in parts if p]
        return ", ".join(filtered) if filtered else None


class ClientUpdate(BaseModel):
    """Client update payload."""

    first_name: str | None = Field(default=None, min_length=1, max_length=100)
    last_name: str | None = Field(default=None, min_length=1, max_length=100)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=20)
    date_of_birth: date | None = None
    gender: Gender | None = None
    country_of_origin: str | None = Field(default=None, max_length=100)
    immigration_status: ImmigrationStatus | None = None
    address_line1: str | None = Field(default=None, max_length=255)
    address_line2: str | None = Field(default=None, max_length=255)
    city: str | None = Field(default=None, max_length=100)
    state: str | None = Field(default=None, max_length=100)
    zip_code: str | None = Field(default=None, max_length=20)
    preferred_language: str | None = Field(default=None, max_length=10)
    emergency_contact_name: str | None = Field(default=None, max_length=200)
    emergency_contact_phone: str | None = Field(default=None, max_length=20)
    notes: str | None = None
    is_active: bool | None = None


class ClientSearch(BaseModel):
    """Client search filter parameters."""

    query: str | None = Field(default=None, description="Search name, email, phone, client_number")
    immigration_status: ImmigrationStatus | None = None
    country_of_origin: str | None = None
    city: str | None = None
    state: str | None = None
    is_active: bool | None = None
    preferred_language: str | None = None
    created_after: datetime | None = None
    created_before: datetime | None = None
