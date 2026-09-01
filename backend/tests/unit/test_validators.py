"""Tests for app/utils/validators.py — all pure-function, no DB required."""

import pytest

from app.utils.validators import (
    is_valid_ein,
    is_valid_email,
    is_valid_international_phone,
    is_valid_itin,
    is_valid_phone,
    is_valid_ssn,
    is_valid_us_phone,
    is_valid_zip_code,
    normalize_phone,
    normalize_ssn,
)


# ── Email ─────────────────────────────────────────────────────────────────────

class TestIsValidEmail:
    def test_standard_email(self):
        assert is_valid_email("user@example.com") is True

    def test_subdomain(self):
        assert is_valid_email("user@mail.example.co.uk") is True

    def test_plus_addressing(self):
        assert is_valid_email("user+tag@example.com") is True

    def test_missing_at(self):
        assert is_valid_email("userexample.com") is False

    def test_missing_domain(self):
        assert is_valid_email("user@") is False

    def test_empty_string(self):
        assert is_valid_email("") is False

    def test_too_long(self):
        # Exceeds 254-character limit
        long_local = "a" * 250
        assert is_valid_email(f"{long_local}@example.com") is False

    def test_double_at(self):
        assert is_valid_email("user@@example.com") is False


# ── US phone ─────────────────────────────────────────────────────────────────

class TestIsValidUsPhone:
    def test_plain_ten_digits(self):
        assert is_valid_us_phone("5558675309") is True

    def test_dashes(self):
        assert is_valid_us_phone("555-867-5309") is True

    def test_parentheses(self):
        assert is_valid_us_phone("(555) 867-5309") is True

    def test_country_code_plus_one(self):
        assert is_valid_us_phone("+15558675309") is True

    def test_dots(self):
        assert is_valid_us_phone("555.867.5309") is True

    def test_too_short(self):
        assert is_valid_us_phone("55512345") is False

    def test_empty_string(self):
        assert is_valid_us_phone("") is False

    def test_letters(self):
        assert is_valid_us_phone("555-ABC-5309") is False


# ── International phone ───────────────────────────────────────────────────────

class TestIsValidInternationalPhone:
    def test_uk_number(self):
        assert is_valid_international_phone("+447911123456") is True

    def test_mexico(self):
        assert is_valid_international_phone("+525512345678") is True

    def test_too_short(self):
        assert is_valid_international_phone("+12345") is False

    def test_empty(self):
        assert is_valid_international_phone("") is False


# ── Combined phone ────────────────────────────────────────────────────────────

class TestIsValidPhone:
    def test_us_number_accepted(self):
        assert is_valid_phone("(555) 123-4567") is True

    def test_international_accepted(self):
        assert is_valid_phone("+447911123456") is True

    def test_garbage_rejected(self):
        assert is_valid_phone("not-a-phone") is False


# ── SSN ───────────────────────────────────────────────────────────────────────

class TestIsValidSsn:
    def test_valid_ssn(self):
        assert is_valid_ssn("123-45-6789") is True

    def test_valid_no_dashes(self):
        assert is_valid_ssn("123456789") is True

    def test_all_zero_area(self):
        assert is_valid_ssn("000-45-6789") is False

    def test_all_zero_group(self):
        assert is_valid_ssn("123-00-6789") is False

    def test_all_zero_serial(self):
        assert is_valid_ssn("123-45-0000") is False

    def test_area_666(self):
        assert is_valid_ssn("666-45-6789") is False

    def test_area_900_plus(self):
        assert is_valid_ssn("900-45-6789") is False

    def test_area_999(self):
        assert is_valid_ssn("999-45-6789") is False

    def test_empty(self):
        assert is_valid_ssn("") is False

    def test_wrong_format(self):
        assert is_valid_ssn("12-345-6789") is False


# ── ITIN ──────────────────────────────────────────────────────────────────────

class TestIsValidItin:
    def test_valid_itin(self):
        assert is_valid_itin("912-70-1234") is True

    def test_valid_no_dashes(self):
        assert is_valid_itin("912701234") is True

    def test_not_starting_with_9(self):
        assert is_valid_itin("112-70-1234") is False

    def test_empty(self):
        assert is_valid_itin("") is False


# ── ZIP code ──────────────────────────────────────────────────────────────────

class TestIsValidZipCode:
    def test_five_digits(self):
        assert is_valid_zip_code("12345") is True

    def test_zip_plus_four(self):
        assert is_valid_zip_code("12345-6789") is True

    def test_four_digits(self):
        assert is_valid_zip_code("1234") is False

    def test_six_digits(self):
        assert is_valid_zip_code("123456") is False

    def test_letters(self):
        assert is_valid_zip_code("1234A") is False

    def test_empty(self):
        assert is_valid_zip_code("") is False


# ── EIN ───────────────────────────────────────────────────────────────────────

class TestIsValidEin:
    def test_valid_with_dash(self):
        assert is_valid_ein("12-3456789") is True

    def test_valid_no_dash(self):
        assert is_valid_ein("123456789") is True

    def test_too_short(self):
        assert is_valid_ein("12-34567") is False

    def test_empty(self):
        assert is_valid_ein("") is False


# ── normalize_phone ───────────────────────────────────────────────────────────

class TestNormalizePhone:
    def test_ten_digits(self):
        assert normalize_phone("5558675309") == "+15558675309"

    def test_one_prefix(self):
        assert normalize_phone("15558675309") == "+15558675309"

    def test_already_e164(self):
        assert normalize_phone("+15558675309") == "+15558675309"

    def test_dashes_stripped(self):
        assert normalize_phone("555-867-5309") == "+15558675309"

    def test_parentheses_stripped(self):
        assert normalize_phone("(555) 867-5309") == "+15558675309"

    def test_empty_returns_empty(self):
        assert normalize_phone("") == ""


# ── normalize_ssn ─────────────────────────────────────────────────────────────

class TestNormalizeSsn:
    def test_plain_nine_digits(self):
        assert normalize_ssn("123456789") == "123-45-6789"

    def test_already_formatted(self):
        assert normalize_ssn("123-45-6789") == "123-45-6789"

    def test_wrong_digit_count_raises(self):
        with pytest.raises(ValueError, match="9 digits"):
            normalize_ssn("12345678")
