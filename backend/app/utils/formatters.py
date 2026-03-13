"""Formatting utilities for dates, currency, phone numbers, etc."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal


def format_date(d: date | datetime | None, fmt: str = "%B %d, %Y") -> str:
    """Format a date for display. Returns empty string for None."""
    if d is None:
        return ""
    return d.strftime(fmt)


def format_date_short(d: date | datetime | None) -> str:
    """Format a date as MM/DD/YYYY."""
    return format_date(d, "%m/%d/%Y")


def format_date_iso(d: date | datetime | None) -> str:
    """Format a date as YYYY-MM-DD."""
    return format_date(d, "%Y-%m-%d")


def format_datetime(dt: datetime | None, fmt: str = "%B %d, %Y at %I:%M %p") -> str:
    """Format a datetime for display."""
    if dt is None:
        return ""
    return dt.strftime(fmt)


def format_datetime_short(dt: datetime | None) -> str:
    """Format a datetime as MM/DD/YY HH:MM."""
    return format_datetime(dt, "%m/%d/%y %H:%M")


def format_currency(
    amount: Decimal | float | int | None,
    currency: str = "USD",
    show_symbol: bool = True,
) -> str:
    """Format a monetary amount for display."""
    if amount is None:
        return "$0.00" if show_symbol else "0.00"

    decimal_amount = Decimal(str(amount))
    formatted = f"{decimal_amount:,.2f}"

    symbols = {
        "USD": "$",
        "EUR": "\u20ac",
        "GBP": "\u00a3",
        "MXN": "MX$",
        "BRL": "R$",
    }

    if show_symbol:
        symbol = symbols.get(currency, f"{currency} ")
        if decimal_amount < 0:
            return f"-{symbol}{formatted.lstrip('-')}"
        return f"{symbol}{formatted}"

    return formatted


def format_phone(phone: str | None) -> str:
    """Format a phone number for display as (XXX) XXX-XXXX for US numbers."""
    if not phone:
        return ""

    import re
    digits = re.sub(r"[^\d]", "", phone)

    if len(digits) == 11 and digits.startswith("1"):
        digits = digits[1:]

    if len(digits) == 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"

    # Return as-is for international or unrecognized formats
    return phone


def format_ssn_masked(ssn: str | None) -> str:
    """Mask an SSN showing only last 4 digits: ***-**-XXXX."""
    if not ssn:
        return ""
    import re
    digits = re.sub(r"[^\d]", "", ssn)
    if len(digits) < 4:
        return "***-**-****"
    return f"***-**-{digits[-4:]}"


def format_percentage(value: float | Decimal | None, decimals: int = 1) -> str:
    """Format a decimal value as a percentage string."""
    if value is None:
        return "0.0%"
    return f"{float(value):.{decimals}f}%"


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable form."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"


def truncate(text: str | None, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to max_length, adding suffix if truncated."""
    if not text:
        return ""
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)] + suffix


def format_name(first_name: str, last_name: str) -> str:
    """Format a full name."""
    return f"{first_name} {last_name}".strip()


def format_case_number(number: int, prefix: str = "MB") -> str:
    """Format a case number with prefix and zero-padding."""
    return f"{prefix}-{number:06d}"


def format_invoice_number(number: int, prefix: str = "INV") -> str:
    """Format an invoice number with prefix and zero-padding."""
    return f"{prefix}-{number:06d}"
