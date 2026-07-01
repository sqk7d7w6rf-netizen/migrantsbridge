"""Reporting service: KPIs, dashboard aggregation, and report generation."""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from typing import Any
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants import (
    AppointmentStatus,
    CaseStatus,
    InvoiceStatus,
    Priority,
    TaskStatus,
)
from app.models.billing import Invoice
from app.models.case import Case
from app.models.client import Client
from app.models.document import Document
from app.models.scheduling import Appointment
from app.models.task import StaffTask
from app.models.user import User
from app.models.wealth import FinancialGoal, InvestmentRecord, SavingsEnrollment


async def compute_kpis(
    session: AsyncSession,
    period_start: date | None = None,
    period_end: date | None = None,
) -> dict[str, Any]:
    """Compute key performance indicators for the organization."""
    now = datetime.now(timezone.utc)
    if period_start is None:
        period_start = (now - timedelta(days=30)).date()
    if period_end is None:
        period_end = now.date()

    start_dt = datetime.combine(period_start, datetime.min.time())
    end_dt = datetime.combine(period_end, datetime.max.time())

    # Client KPIs
    total_clients = (await session.execute(
        select(func.count(Client.id)).where(Client.is_deleted == False)
    )).scalar_one()

    new_clients = (await session.execute(
        select(func.count(Client.id)).where(
            Client.is_deleted == False,
            Client.created_at >= start_dt,
            Client.created_at <= end_dt,
        )
    )).scalar_one()

    # Case KPIs - use model CaseStatus enum values
    closed_statuses = [
        CaseStatus.CLOSED_SUCCESSFUL,
        CaseStatus.CLOSED_UNSUCCESSFUL,
        CaseStatus.CLOSED_WITHDRAWN,
    ]

    total_open_cases = (await session.execute(
        select(func.count(Case.id)).where(
            Case.is_deleted == False,
            Case.status.notin_(closed_statuses),
        )
    )).scalar_one()

    cases_opened = (await session.execute(
        select(func.count(Case.id)).where(
            Case.is_deleted == False,
            Case.created_at >= start_dt,
            Case.created_at <= end_dt,
        )
    )).scalar_one()

    cases_closed = (await session.execute(
        select(func.count(Case.id)).where(
            Case.is_deleted == False,
            Case.status.in_(closed_statuses),
            Case.closed_date.isnot(None),
        )
    )).scalar_one()

    # Financial KPIs
    revenue = (await session.execute(
        select(func.coalesce(func.sum(Invoice.amount_paid), Decimal("0.00"))).where(
            Invoice.is_deleted == False,
            Invoice.created_at >= start_dt,
            Invoice.created_at <= end_dt,
        )
    )).scalar_one()

    outstanding_statuses = [InvoiceStatus.PAID, InvoiceStatus.CANCELLED, InvoiceStatus.REFUNDED]
    outstanding = (await session.execute(
        select(func.coalesce(
            func.sum(Invoice.total_amount - Invoice.amount_paid),
            Decimal("0.00"),
        )).where(
            Invoice.is_deleted == False,
            Invoice.status.notin_(outstanding_statuses),
        )
    )).scalar_one()

    # Task KPIs
    tasks_completed = (await session.execute(
        select(func.count(StaffTask.id)).where(
            StaffTask.is_deleted == False,
            StaffTask.status == TaskStatus.COMPLETED,
            StaffTask.completed_at >= start_dt,
            StaffTask.completed_at <= end_dt,
        )
    )).scalar_one()

    today = date.today()
    overdue_tasks = (await session.execute(
        select(func.count(StaffTask.id)).where(
            StaffTask.is_deleted == False,
            StaffTask.status.notin_([TaskStatus.COMPLETED, TaskStatus.CANCELLED]),
            StaffTask.due_date < today,
        )
    )).scalar_one()

    # Appointment KPIs
    appointments_held = (await session.execute(
        select(func.count(Appointment.id)).where(
            Appointment.is_deleted == False,
            Appointment.status == AppointmentStatus.COMPLETED,
            Appointment.start_time >= start_dt,
            Appointment.start_time <= end_dt,
        )
    )).scalar_one()

    no_shows = (await session.execute(
        select(func.count(Appointment.id)).where(
            Appointment.is_deleted == False,
            Appointment.status == AppointmentStatus.NO_SHOW,
            Appointment.start_time >= start_dt,
            Appointment.start_time <= end_dt,
        )
    )).scalar_one()

    return {
        "period": {"start": period_start.isoformat(), "end": period_end.isoformat()},
        "clients": {
            "total": total_clients,
            "new_in_period": new_clients,
        },
        "cases": {
            "total_open": total_open_cases,
            "opened_in_period": cases_opened,
            "closed_in_period": cases_closed,
            "closure_rate": round(cases_closed / cases_opened * 100, 1) if cases_opened > 0 else 0,
        },
        "financial": {
            "revenue_in_period": str(revenue),
            "total_outstanding": str(outstanding),
        },
        "tasks": {
            "completed_in_period": tasks_completed,
            "overdue": overdue_tasks,
        },
        "appointments": {
            "held_in_period": appointments_held,
            "no_shows": no_shows,
            "no_show_rate": round(no_shows / (appointments_held + no_shows) * 100, 1) if (appointments_held + no_shows) > 0 else 0,
        },
    }


def format_kpi_digest(kpis: dict, period_label: str) -> str:
    """Format the output of compute_kpis into a Slack mrkdwn digest message.

    Pure string-formatting function (no I/O) so it can be unit tested.
    """
    clients = kpis.get("clients", {})
    cases = kpis.get("cases", {})
    financial = kpis.get("financial", {})
    tasks = kpis.get("tasks", {})
    appointments = kpis.get("appointments", {})

    new_clients = clients.get("new_in_period", 0)
    total_open_cases = cases.get("total_open", 0)
    cases_opened = cases.get("opened_in_period", 0)
    cases_closed = cases.get("closed_in_period", 0)
    revenue = financial.get("revenue_in_period", "0.00")
    overdue_tasks = tasks.get("overdue", 0)
    no_show_rate = appointments.get("no_show_rate", 0)

    lines = [
        f"*MigrantsBridge KPI Digest — {period_label}*",
        "",
        f"• *New clients:* {new_clients}",
        f"• *Open cases:* {total_open_cases} _(opened {cases_opened} / closed {cases_closed} this period)_",
        f"• *Revenue this period:* ${revenue}",
        f"• *Overdue tasks:* {overdue_tasks}",
        f"• *Appointment no-show rate:* {no_show_rate}%",
    ]
    return "\n".join(lines)


async def get_plate_summary(session: AsyncSession) -> dict[str, Any]:
    """Org-wide (not per-user) snapshot of what needs attention this week.

    Includes overdue staff tasks, unassigned open cases, upcoming
    appointments in the next 7 days, and other "pending decision" signals.
    """
    now = datetime.now(timezone.utc)
    today = date.today()
    week_from_now = now + timedelta(days=7)

    closed_statuses = [
        CaseStatus.CLOSED_SUCCESSFUL,
        CaseStatus.CLOSED_UNSUCCESSFUL,
        CaseStatus.CLOSED_WITHDRAWN,
    ]

    # Overdue staff tasks (due_date in the past, not completed)
    overdue_tasks_query = (
        select(StaffTask)
        .where(
            StaffTask.is_deleted == False,
            StaffTask.status.notin_([TaskStatus.COMPLETED, TaskStatus.CANCELLED]),
            StaffTask.due_date.isnot(None),
            StaffTask.due_date < today,
        )
        .order_by(StaffTask.due_date.asc())
    )
    overdue_tasks_result = await session.execute(overdue_tasks_query)
    overdue_tasks = overdue_tasks_result.scalars().all()

    overdue_task_examples = [
        {
            "title": task.title,
            "assigned_to_id": str(task.assigned_to_id) if task.assigned_to_id else None,
            "due_date": task.due_date.isoformat() if task.due_date else None,
        }
        for task in overdue_tasks[:5]
    ]

    # Open cases with no assigned staff
    unassigned_cases_query = (
        select(Case)
        .where(
            Case.is_deleted == False,
            Case.assigned_to_id.is_(None),
            Case.status.notin_(closed_statuses),
        )
        .order_by(Case.opened_date.asc())
    )
    unassigned_cases_result = await session.execute(unassigned_cases_query)
    unassigned_cases = unassigned_cases_result.scalars().all()

    unassigned_case_examples = [
        {
            "case_number": case.case_number,
            "case_type": case.case_type.value if hasattr(case.case_type, "value") else str(case.case_type),
            "opened_date": case.opened_date.isoformat() if case.opened_date else None,
        }
        for case in unassigned_cases[:5]
    ]

    # Upcoming appointments in the next 7 days
    upcoming_appointments_count = (await session.execute(
        select(func.count(Appointment.id)).where(
            Appointment.is_deleted == False,
            Appointment.status.in_([AppointmentStatus.SCHEDULED, AppointmentStatus.CONFIRMED]),
            Appointment.start_time >= now,
            Appointment.start_time <= week_from_now,
        )
    )).scalar_one()

    # High-priority tasks with no due date set (at risk of being forgotten)
    high_priority_no_due_date = (await session.execute(
        select(func.count(StaffTask.id)).where(
            StaffTask.is_deleted == False,
            StaffTask.status.notin_([TaskStatus.COMPLETED, TaskStatus.CANCELLED]),
            StaffTask.priority.in_([Priority.HIGH, Priority.URGENT]),
            StaffTask.due_date.is_(None),
        )
    )).scalar_one()

    return {
        "overdue_tasks": {
            "count": len(overdue_tasks),
            "examples": overdue_task_examples,
        },
        "unassigned_open_cases": {
            "count": len(unassigned_cases),
            "examples": unassigned_case_examples,
        },
        "upcoming_appointments_next_7_days": upcoming_appointments_count,
        "high_priority_tasks_missing_due_date": high_priority_no_due_date,
    }


def format_plate_digest(summary: dict) -> str:
    """Format get_plate_summary's output into a Slack mrkdwn digest message.

    Pure string-formatting function (no I/O) so it can be unit tested.
    """
    overdue = summary.get("overdue_tasks", {})
    unassigned = summary.get("unassigned_open_cases", {})
    upcoming_appointments = summary.get("upcoming_appointments_next_7_days", 0)
    high_priority_no_due_date = summary.get("high_priority_tasks_missing_due_date", 0)

    lines = [
        "*What's on your plate this week*",
        "",
        f"• *Overdue tasks:* {overdue.get('count', 0)}",
    ]
    for example in overdue.get("examples", []):
        assignee = example.get("assigned_to_id") or "unassigned"
        lines.append(f"    - {example.get('title')} (assignee: {assignee}, due {example.get('due_date')})")

    lines.append(f"• *Unassigned open cases:* {unassigned.get('count', 0)}")
    for example in unassigned.get("examples", []):
        lines.append(
            f"    - Case #{example.get('case_number')} ({example.get('case_type')}, opened {example.get('opened_date')})"
        )

    lines.append(f"• *Upcoming appointments (next 7 days):* {upcoming_appointments}")
    lines.append(f"• *High-priority tasks with no due date:* {high_priority_no_due_date}")

    return "\n".join(lines)


async def get_overview_dashboard(session: AsyncSession) -> dict[str, Any]:
    """Get organization overview dashboard data."""
    kpis = await compute_kpis(session)

    # Cases by type
    cases_by_type = (await session.execute(
        select(Case.case_type, func.count(Case.id))
        .where(Case.is_deleted == False)
        .group_by(Case.case_type)
    )).all()

    # Cases by status
    cases_by_status = (await session.execute(
        select(Case.status, func.count(Case.id))
        .where(Case.is_deleted == False)
        .group_by(Case.status)
    )).all()

    return {
        "kpis": kpis,
        "cases_by_type": {row[0].value if hasattr(row[0], "value") else str(row[0]): row[1] for row in cases_by_type},
        "cases_by_status": {row[0].value if hasattr(row[0], "value") else str(row[0]): row[1] for row in cases_by_status},
    }


async def get_cases_dashboard(session: AsyncSession) -> dict[str, Any]:
    """Get case-focused dashboard data."""
    closed_statuses = [
        CaseStatus.CLOSED_SUCCESSFUL,
        CaseStatus.CLOSED_UNSUCCESSFUL,
        CaseStatus.CLOSED_WITHDRAWN,
    ]

    # Cases by priority
    by_priority = (await session.execute(
        select(Case.priority, func.count(Case.id))
        .where(Case.is_deleted == False, Case.status.notin_(closed_statuses))
        .group_by(Case.priority)
    )).all()

    # Cases by assigned staff
    by_staff = (await session.execute(
        select(Case.assigned_to_id, func.count(Case.id))
        .where(Case.is_deleted == False, Case.assigned_to_id.isnot(None))
        .group_by(Case.assigned_to_id)
    )).all()

    # Average case duration for closed cases (using closed_date and opened_date)
    avg_duration = (await session.execute(
        select(func.avg(func.extract("epoch", Case.closed_date) - func.extract("epoch", Case.opened_date)) / 86400)
        .where(
            Case.is_deleted == False,
            Case.closed_date.isnot(None),
            Case.opened_date.isnot(None),
        )
    )).scalar_one()

    # Unassigned cases
    unassigned = (await session.execute(
        select(func.count(Case.id)).where(
            Case.is_deleted == False,
            Case.assigned_to_id.is_(None),
            Case.status.notin_(closed_statuses),
        )
    )).scalar_one()

    return {
        "by_priority": {row[0].value if hasattr(row[0], "value") else str(row[0]): row[1] for row in by_priority},
        "by_staff": {str(row[0]): row[1] for row in by_staff if row[0]},
        "average_duration_days": round(float(avg_duration), 1) if avg_duration else None,
        "unassigned_count": unassigned,
    }


async def get_financial_dashboard(session: AsyncSession) -> dict[str, Any]:
    """Get financial dashboard data."""
    from app.services.billing_service import compute_billing_summary

    # Current month summary
    now = datetime.now(timezone.utc)
    month_start = now.replace(day=1).date()
    summary = await compute_billing_summary(session, period_start=month_start)

    # Revenue trend (last 6 months)
    revenue_trend = []
    for i in range(5, -1, -1):
        m_start = (now - timedelta(days=30 * i)).replace(day=1).date()
        m_end = (m_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        month_result = await session.execute(
            select(func.coalesce(func.sum(Invoice.amount_paid), Decimal("0.00"))).where(
                Invoice.is_deleted == False,
                Invoice.paid_date >= m_start,
                Invoice.paid_date <= m_end,
            )
        )
        revenue_trend.append({
            "month": m_start.strftime("%Y-%m"),
            "revenue": str(month_result.scalar_one()),
        })

    return {
        "current_month_summary": {
            "total_invoiced": str(summary.total_invoiced),
            "total_collected": str(summary.total_collected),
            "total_outstanding": str(summary.total_outstanding),
            "overdue_amount": str(summary.overdue_amount),
        },
        "revenue_trend": revenue_trend,
    }


async def get_wealth_dashboard(session: AsyncSession) -> dict[str, Any]:
    """Get wealth building dashboard data."""
    # Total savings across all clients
    total_savings = (await session.execute(
        select(func.coalesce(func.sum(SavingsEnrollment.balance), Decimal("0.00")))
    )).scalar_one()

    total_matched = (await session.execute(
        select(func.coalesce(func.sum(SavingsEnrollment.matched_amount), Decimal("0.00")))
    )).scalar_one()

    active_enrollments = (await session.execute(
        select(func.count(SavingsEnrollment.id)).where(SavingsEnrollment.is_active == True)
    )).scalar_one()

    # Goals summary
    goals_by_status = (await session.execute(
        select(FinancialGoal.is_achieved, func.count(FinancialGoal.id))
        .group_by(FinancialGoal.is_achieved)
    )).all()

    goals_map: dict[str, int] = {}
    for row in goals_by_status:
        key = "achieved" if row[0] else "active"
        goals_map[key] = row[1]

    # Investment totals
    total_inv_value = (await session.execute(
        select(func.coalesce(func.sum(InvestmentRecord.current_value), Decimal("0.00")))
    )).scalar_one()

    return {
        "total_savings": str(total_savings),
        "total_matched": str(total_matched),
        "active_enrollments": active_enrollments,
        "goals_by_status": goals_map,
        "total_investment_value": str(total_inv_value),
    }


async def get_staff_dashboard(session: AsyncSession) -> dict[str, Any]:
    """Get staff performance dashboard data."""
    now = datetime.now(timezone.utc)
    week_start = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)

    closed_statuses = [
        CaseStatus.CLOSED_SUCCESSFUL,
        CaseStatus.CLOSED_UNSUCCESSFUL,
        CaseStatus.CLOSED_WITHDRAWN,
    ]

    # Staff with most open cases
    staff_cases = (await session.execute(
        select(Case.assigned_to_id, func.count(Case.id))
        .where(
            Case.is_deleted == False,
            Case.assigned_to_id.isnot(None),
            Case.status.notin_(closed_statuses),
        )
        .group_by(Case.assigned_to_id)
        .order_by(func.count(Case.id).desc())
        .limit(10)
    )).all()

    # Hours worked this week (from actual_hours on tasks completed this week)
    hours_by_staff = (await session.execute(
        select(StaffTask.assigned_to_id, func.sum(StaffTask.actual_hours))
        .where(
            StaffTask.is_deleted == False,
            StaffTask.completed_at >= week_start,
            StaffTask.actual_hours.isnot(None),
        )
        .group_by(StaffTask.assigned_to_id)
    )).all()

    # Tasks completed this week
    tasks_by_staff = (await session.execute(
        select(StaffTask.assigned_to_id, func.count(StaffTask.id))
        .where(
            StaffTask.is_deleted == False,
            StaffTask.status == TaskStatus.COMPLETED,
            StaffTask.completed_at >= week_start,
        )
        .group_by(StaffTask.assigned_to_id)
    )).all()

    return {
        "case_load": {str(row[0]): row[1] for row in staff_cases if row[0]},
        "hours_this_week": {str(row[0]): float(row[1]) for row in hours_by_staff if row[0] and row[1]},
        "tasks_completed_this_week": {str(row[0]): row[1] for row in tasks_by_staff if row[0]},
    }
