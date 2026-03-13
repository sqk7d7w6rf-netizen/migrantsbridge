import uuid
from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.constants import Gender, ImmigrationStatus
from app.core.database import Base
from app.models.base import SoftDeleteMixin, TimestampMixin


class Client(TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "clients"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    last_name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    middle_name: Mapped[str | None] = mapped_column(String(150), nullable=True)
    date_of_birth: Mapped[date | None] = mapped_column(Date, nullable=True)
    gender: Mapped[Gender | None] = mapped_column(nullable=True)
    email: Mapped[str | None] = mapped_column(String(320), nullable=True, index=True)
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    preferred_language: Mapped[str] = mapped_column(String(10), default="en", nullable=False)
    nationality: Mapped[str | None] = mapped_column(String(100), nullable=True)
    country_of_origin: Mapped[str | None] = mapped_column(String(100), nullable=True)
    immigration_status: Mapped[ImmigrationStatus | None] = mapped_column(nullable=True, index=True)
    alien_number: Mapped[str | None] = mapped_column(String(50), nullable=True, unique=True)
    address_line_1: Mapped[str | None] = mapped_column(String(255), nullable=True)
    address_line_2: Mapped[str | None] = mapped_column(String(255), nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    state: Mapped[str | None] = mapped_column(String(100), nullable=True)
    zip_code: Mapped[str | None] = mapped_column(String(20), nullable=True)
    country: Mapped[str] = mapped_column(String(100), default="US", nullable=False)
    emergency_contact_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    emergency_contact_phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    emergency_contact_relationship: Mapped[str | None] = mapped_column(String(100), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    intake_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    languages: Mapped[list["ClientLanguage"]] = relationship(
        back_populates="client", cascade="all, delete-orphan", lazy="selectin"
    )
    cases: Mapped[list["Case"]] = relationship(back_populates="client", lazy="noload")  # noqa: F821
    documents: Mapped[list["Document"]] = relationship(back_populates="client", lazy="noload")  # noqa: F821
    appointments: Mapped[list["Appointment"]] = relationship(back_populates="client", lazy="noload")  # noqa: F821
    invoices: Mapped[list["Invoice"]] = relationship(back_populates="client", lazy="noload")  # noqa: F821
    financial_profile: Mapped["FinancialProfile | None"] = relationship(  # noqa: F821
        back_populates="client", uselist=False, lazy="noload"
    )

    @property
    def full_name(self) -> str:
        parts = [self.first_name]
        if self.middle_name:
            parts.append(self.middle_name)
        parts.append(self.last_name)
        return " ".join(parts)


class ClientLanguage(TimestampMixin, Base):
    __tablename__ = "client_languages"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("clients.id", ondelete="CASCADE"), nullable=False, index=True
    )
    language: Mapped[str] = mapped_column(String(50), nullable=False)
    proficiency: Mapped[str | None] = mapped_column(String(50), nullable=True)
    is_primary: Mapped[bool] = mapped_column(default=False, nullable=False)

    client: Mapped["Client"] = relationship(back_populates="languages")
