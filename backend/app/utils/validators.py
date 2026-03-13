"""Input validation utilities for phone, email, SSN, and other formats."""

from __future__ import annotations

import re


# Compiled patterns for performance
_EMAIL_PATTERN = re.compile(
    r"^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}"
    r"[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$"
)

# US phone: optional +1, then 10 digits
_US_PHONE_PATTERN = re.compile(r"^\+?1?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}$")

# International phone: + followed by 7-15 digits
_INTL_PHONE_PATTERN = re.compile(r"^\+\d{7,15}$")

# SSN: XXX-XX-XXXX
_SSN_PATTERN = re.compile(r"^\d{3}-?\d{2}-?\d{4}$")

# ITIN: 9XX-XX-XXXX where X is 7 or 8
_ITIN_PATTERN = re.compile(r"^9\d{2}-?\d{2}-?\d{4}$")

# ZIP code: 5 digits or 5+4
_ZIP_PATTERN = re.compile(r"^\d{5}(-\d{4})?$")

# EIN: XX-XXXXXXX
_EIN_PATTERN = re.compile(r"^\d{2}-?\d{7}$")


def is_valid_email(email: str) -> bool:
    """Validate email format."""
    if not email or len(email) > 254:
        return False
    return bool(_EMAIL_PATTERN.match(email))


def is_valid_us_phone(phone: str) -> bool:
    """Validate US phone number format."""
    if not phone:
        return False
    cleaned = phone.strip()
    return bool(_US_PHONE_PATTERN.match(cleaned))


def is_valid_international_phone(phone: str) -> bool:
    """Validate international phone number format (E.164-like)."""
    if not phone:
        return False
    cleaned = re.sub(r"[-.\s()]", "", phone.strip())
    if not cleaned.startswith("+"):
        cleaned = "+" + cleaned
    return bool(_INTL_PHONE_PATTERN.match(cleaned))


def is_valid_phone(phone: str) -> bool:
    """Validate phone number (US or international)."""
    return is_valid_us_phone(phone) or is_valid_international_phone(phone)


def is_valid_ssn(ssn: str) -> bool:
    """Validate SSN format (XXX-XX-XXXX). Does not validate against IRS rules."""
    if not ssn:
        return False
    cleaned = ssn.strip()
    if not _SSN_PATTERN.match(cleaned):
        return False
    # Basic IRS rules: no group of all zeros
    digits = cleaned.replace("-", "")
    area, group, serial = digits[:3], digits[3:5], digits[5:]
    if area == "000" or group == "00" or serial == "0000":
        return False
    # 666 and 900-999 are invalid area numbers
    area_int = int(area)
    if area_int == 666 or area_int >= 900:
        return False
    return True


def is_valid_itin(itin: str) -> bool:
    """Validate ITIN format (9XX-XX-XXXX)."""
    if not itin:
        return False
    return bool(_ITIN_PATTERN.match(itin.strip()))


def is_valid_zip_code(zip_code: str) -> bool:
    """Validate US ZIP code format."""
    if not zip_code:
        return False
    return bool(_ZIP_PATTERN.match(zip_code.strip()))


def is_valid_ein(ein: str) -> bool:
    """Validate EIN format (XX-XXXXXXX)."""
    if not ein:
        return False
    return bool(_EIN_PATTERN.match(ein.strip()))


def normalize_phone(phone: str) -> str:
    """Normalize a phone number to E.164-like format (+1XXXXXXXXXX for US)."""
    if not phone:
        return phone
    digits = re.sub(r"[^\d+]", "", phone.strip())
    if digits.startswith("+"):
        return digits
    if len(digits) == 10:
        return f"+1{digits}"
    if len(digits) == 11 and digits.startswith("1"):
        return f"+{digits}"
    return f"+{digits}"


def normalize_ssn(ssn: str) -> str:
    """Normalize SSN to XXX-XX-XXXX format."""
    digits = re.sub(r"[^\d]", "", ssn.strip())
    if len(digits) != 9:
        raise ValueError("SSN must contain exactly 9 digits")
    return f"{digits[:3]}-{digits[3:5]}-{digits[5:]}"
