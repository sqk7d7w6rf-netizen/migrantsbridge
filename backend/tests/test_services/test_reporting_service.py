"""Unit tests for pure-function formatting helpers in reporting_service."""

from app.services.reporting_service import format_kpi_digest, format_plate_digest


def _sample_kpis() -> dict:
    return {
        "period": {"start": "2026-06-01", "end": "2026-06-30"},
        "clients": {"total": 120, "new_in_period": 8},
        "cases": {
            "total_open": 45,
            "opened_in_period": 10,
            "closed_in_period": 6,
            "closure_rate": 60.0,
        },
        "financial": {"revenue_in_period": "12500.00", "total_outstanding": "3200.00"},
        "tasks": {"completed_in_period": 30, "overdue": 5},
        "appointments": {"held_in_period": 40, "no_shows": 4, "no_show_rate": 9.1},
    }


def test_format_kpi_digest_includes_headline_numbers():
    text = format_kpi_digest(_sample_kpis(), "June 2026")

    assert "June 2026" in text
    assert "*New clients:* 8" in text
    assert "*Open cases:* 45" in text
    assert "opened 10 / closed 6" in text
    assert "*Revenue this period:* $12500.00" in text
    assert "*Overdue tasks:* 5" in text
    assert "*Appointment no-show rate:* 9.1%" in text


def test_format_kpi_digest_is_pure_string_output():
    text = format_kpi_digest(_sample_kpis(), "Week of June 1")
    assert isinstance(text, str)
    assert text.startswith("*MigrantsBridge KPI Digest")


def _sample_plate_summary() -> dict:
    return {
        "overdue_tasks": {
            "count": 2,
            "examples": [
                {"title": "Follow up with client", "assigned_to_id": "abc-123", "due_date": "2026-06-25"},
                {"title": "Review documents", "assigned_to_id": None, "due_date": "2026-06-20"},
            ],
        },
        "unassigned_open_cases": {
            "count": 1,
            "examples": [
                {"case_number": 10123, "case_type": "immigration", "opened_date": "2026-06-10"},
            ],
        },
        "upcoming_appointments_next_7_days": 12,
        "high_priority_tasks_missing_due_date": 3,
    }


def test_format_plate_digest_includes_all_sections():
    text = format_plate_digest(_sample_plate_summary())

    assert "What's on your plate this week" in text
    assert "*Overdue tasks:* 2" in text
    assert "Follow up with client" in text
    assert "*Unassigned open cases:* 1" in text
    assert "Case #10123" in text
    assert "*Upcoming appointments (next 7 days):* 12" in text
    assert "*High-priority tasks with no due date:* 3" in text


def test_format_plate_digest_handles_empty_summary():
    empty_summary = {
        "overdue_tasks": {"count": 0, "examples": []},
        "unassigned_open_cases": {"count": 0, "examples": []},
        "upcoming_appointments_next_7_days": 0,
        "high_priority_tasks_missing_due_date": 0,
    }
    text = format_plate_digest(empty_summary)
    assert "*Overdue tasks:* 0" in text
    assert "*Unassigned open cases:* 0" in text
