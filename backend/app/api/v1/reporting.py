"""Reporting API routes: KPIs, dashboards, report generation."""

from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.core.security import get_current_user
from app.services import ai_service, reporting_service

router = APIRouter()


@router.get("/dashboard")
async def get_dashboard(
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """Get full dashboard data (KPIs + trends)."""
    return await reporting_service.get_overview_dashboard(session)


@router.get("/kpis")
async def get_kpis(
    period_start: date | None = None,
    period_end: date | None = None,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """Get key performance indicators."""
    return await reporting_service.compute_kpis(session, period_start, period_end)


@router.get("/my-plate")
async def get_my_plate(
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """Get an org-wide snapshot of what's on the plate this week."""
    return await reporting_service.get_plate_summary(session)


@router.get("/blindspots")
async def get_blindspots(
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """Get AI-generated blindspot insights from recent KPIs and the plate summary."""
    kpis = await reporting_service.compute_kpis(session)
    plate_summary = await reporting_service.get_plate_summary(session)
    return await ai_service.generate_blindspots(kpis, plate_summary)


@router.get("/dashboards/overview")
async def get_overview_dashboard(
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """Get organization overview dashboard."""
    return await reporting_service.get_overview_dashboard(session)


@router.get("/dashboards/cases")
async def get_cases_dashboard(
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """Get case-focused dashboard."""
    return await reporting_service.get_cases_dashboard(session)


@router.get("/dashboards/financial")
async def get_financial_dashboard(
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """Get financial dashboard."""
    return await reporting_service.get_financial_dashboard(session)


@router.get("/dashboards/wealth")
async def get_wealth_dashboard(
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """Get wealth building dashboard."""
    return await reporting_service.get_wealth_dashboard(session)


@router.get("/dashboards/staff")
async def get_staff_dashboard(
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """Get staff performance dashboard."""
    return await reporting_service.get_staff_dashboard(session)


@router.get("/generate")
async def generate_report(
    report_type: str = Query(..., description="Type: kpis, cases, financial, wealth, staff"),
    period_start: date | None = None,
    period_end: date | None = None,
    format: str = Query(default="json", description="Output format: json or csv"),
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """Generate a report by type and period."""
    data = {}
    if report_type == "kpis":
        data = await reporting_service.compute_kpis(session, period_start, period_end)
    elif report_type == "cases":
        data = await reporting_service.get_cases_dashboard(session)
    elif report_type == "financial":
        data = await reporting_service.get_financial_dashboard(session)
    elif report_type == "wealth":
        data = await reporting_service.get_wealth_dashboard(session)
    elif report_type == "staff":
        data = await reporting_service.get_staff_dashboard(session)
    else:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown report type: {report_type}. Valid: kpis, cases, financial, wealth, staff",
        )

    if format == "csv":
        from app.utils.export import export_to_csv_bytes, generate_csv_response_headers
        import json

        # Flatten dict to list of rows for CSV
        rows = []
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, dict):
                    for sub_key, sub_value in value.items():
                        rows.append({"category": key, "metric": sub_key, "value": str(sub_value)})
                else:
                    rows.append({"category": "summary", "metric": key, "value": str(value)})

        csv_bytes = export_to_csv_bytes(rows)
        headers = generate_csv_response_headers(f"report_{report_type}.csv")
        return Response(content=csv_bytes, media_type="text/csv", headers=headers)

    return data


@router.get("/snapshots")
async def get_snapshots(
    period_start: date | None = None,
    period_end: date | None = None,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """Get historical snapshots / trend data for key metrics."""
    from datetime import timedelta, datetime
    from decimal import Decimal
    from sqlalchemy import func, select
    from app.models.case import Case
    from app.models.client import Client
    from app.models.billing import Invoice

    now = datetime.utcnow()
    if period_start is None:
        period_start = (now - timedelta(days=90)).date()
    if period_end is None:
        period_end = now.date()

    snapshots = []
    current = period_start
    while current <= period_end:
        week_end = current + timedelta(days=6)

        start_dt = datetime.combine(current, datetime.min.time())
        end_dt = datetime.combine(week_end, datetime.max.time())

        new_clients = (await session.execute(
            select(func.count(Client.id)).where(
                Client.is_deleted == False,
                Client.created_at >= start_dt,
                Client.created_at <= end_dt,
            )
        )).scalar_one()

        new_cases = (await session.execute(
            select(func.count(Case.id)).where(
                Case.is_deleted == False,
                Case.created_at >= start_dt,
                Case.created_at <= end_dt,
            )
        )).scalar_one()

        revenue = (await session.execute(
            select(func.coalesce(func.sum(Invoice.amount_paid), Decimal("0.00"))).where(
                Invoice.is_deleted == False,
                Invoice.paid_date >= current,
                Invoice.paid_date <= week_end,
            )
        )).scalar_one()

        snapshots.append({
            "week_start": current.isoformat(),
            "week_end": week_end.isoformat(),
            "new_clients": new_clients,
            "new_cases": new_cases,
            "revenue": str(revenue),
        })

        current = week_end + timedelta(days=1)

    return {"period": {"start": period_start.isoformat(), "end": period_end.isoformat()}, "snapshots": snapshots}


# --------------------------------------------------------------------------- #
# Granular report endpoints expected by the frontend                          #
# --------------------------------------------------------------------------- #

@router.get("/clients/growth")
async def get_client_growth(
    date_from: date | None = None,
    date_to: date | None = None,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """Monthly client growth trend."""
    from app.models.client import Client
    now = datetime.now(timezone.utc)
    start = date_from or (now - timedelta(days=180)).date()
    end = date_to or now.date()

    rows = []
    current = date(start.year, start.month, 1)
    while current <= end:
        if current.month == 12:
            next_month = date(current.year + 1, 1, 1)
        else:
            next_month = date(current.year, current.month + 1, 1)
        month_end = next_month - timedelta(days=1)

        new_count = (await session.execute(
            select(func.count(Client.id)).where(
                Client.is_deleted == False,
                Client.created_at >= datetime.combine(current, datetime.min.time()),
                Client.created_at <= datetime.combine(month_end, datetime.max.time()),
            )
        )).scalar_one()
        total = (await session.execute(
            select(func.count(Client.id)).where(
                Client.is_deleted == False,
                Client.created_at <= datetime.combine(month_end, datetime.max.time()),
            )
        )).scalar_one()
        rows.append({"month": current.strftime("%b %Y"), "new_clients": new_count, "total_clients": total})
        current = next_month
    return rows


@router.get("/clients/demographics")
async def get_client_demographics(
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """Client counts by immigration status."""
    from app.models.client import Client
    result = await session.execute(
        select(Client.immigration_status, func.count(Client.id))
        .where(Client.is_deleted == False)
        .group_by(Client.immigration_status)
    )
    return [{"status": row[0].value if hasattr(row[0], "value") else str(row[0]), "count": row[1]} for row in result.all()]


@router.get("/clients/languages")
async def get_language_distribution(
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """Client counts by preferred language."""
    from app.models.client import Client
    result = await session.execute(
        select(Client.preferred_language, func.count(Client.id))
        .where(Client.is_deleted == False, Client.preferred_language.isnot(None))
        .group_by(Client.preferred_language)
        .order_by(func.count(Client.id).desc())
    )
    return [{"language": row[0] or "Unknown", "count": row[1]} for row in result.all()]


@router.get("/financial/revenue")
async def get_revenue_trend(
    date_from: date | None = None,
    date_to: date | None = None,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """Monthly revenue trend."""
    from app.models.billing import Invoice
    from app.constants import InvoiceStatus
    now = datetime.now(timezone.utc)
    start = date_from or (now - timedelta(days=180)).date()
    end = date_to or now.date()

    rows = []
    current = date(start.year, start.month, 1)
    while current <= end:
        if current.month == 12:
            next_month = date(current.year + 1, 1, 1)
        else:
            next_month = date(current.year, current.month + 1, 1)
        month_end = next_month - timedelta(days=1)

        result = await session.execute(
            select(
                func.coalesce(func.sum(Invoice.total_amount), Decimal("0")),
                func.coalesce(func.sum(Invoice.amount_paid), Decimal("0")),
            ).where(
                Invoice.is_deleted == False,
                Invoice.created_at >= datetime.combine(current, datetime.min.time()),
                Invoice.created_at <= datetime.combine(month_end, datetime.max.time()),
            )
        )
        row = result.one()
        rows.append({
            "month": current.strftime("%b %Y"),
            "revenue": float(row[0]),
            "collected": float(row[1]),
            "outstanding": float(row[0] - row[1]),
        })
        current = next_month
    return rows


@router.get("/financial/billing-status")
async def get_billing_status_breakdown(
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """Invoice counts and totals by status."""
    from app.models.billing import Invoice
    result = await session.execute(
        select(Invoice.status, func.count(Invoice.id), func.coalesce(func.sum(Invoice.total_amount), Decimal("0")))
        .where(Invoice.is_deleted == False)
        .group_by(Invoice.status)
    )
    return [{"status": row[0].value if hasattr(row[0], "value") else str(row[0]), "count": row[1], "total_amount": float(row[2])} for row in result.all()]


@router.get("/financial/top-services")
async def get_top_services(
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """Top service fees by revenue."""
    from app.models.billing import InvoiceLineItem, Invoice
    result = await session.execute(
        select(InvoiceLineItem.description, func.count(InvoiceLineItem.id), func.coalesce(func.sum(InvoiceLineItem.amount), Decimal("0")))
        .join(Invoice, InvoiceLineItem.invoice_id == Invoice.id)
        .where(Invoice.is_deleted == False)
        .group_by(InvoiceLineItem.description)
        .order_by(func.sum(InvoiceLineItem.amount).desc())
        .limit(10)
    )
    return [{"service_name": row[0], "count": row[1], "revenue": float(row[2])} for row in result.all()]


@router.get("/cases/outcomes")
async def get_case_outcomes(
    date_from: date | None = None,
    date_to: date | None = None,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """Case outcomes by type."""
    from app.models.case import Case
    from app.constants import CaseStatus, CaseType
    result = await session.execute(
        select(Case.case_type, Case.status, func.count(Case.id))
        .where(Case.is_deleted == False)
        .group_by(Case.case_type, Case.status)
    )
    aggregated: dict = {}
    for row in result.all():
        case_type = row[0].value if hasattr(row[0], "value") else str(row[0])
        case_status = row[1].value if hasattr(row[1], "value") else str(row[1])
        count = row[2]
        if case_type not in aggregated:
            aggregated[case_type] = {"case_type": case_type, "approved": 0, "denied": 0, "pending": 0}
        if "successful" in case_status:
            aggregated[case_type]["approved"] += count
        elif "unsuccessful" in case_status or "withdrawn" in case_status:
            aggregated[case_type]["denied"] += count
        else:
            aggregated[case_type]["pending"] += count
    return list(aggregated.values())


@router.get("/cases/resolution-times")
async def get_case_resolution_times(
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """Average case resolution times by type."""
    from app.models.case import Case
    from app.constants import CaseStatus
    closed_statuses = [CaseStatus.CLOSED_SUCCESSFUL, CaseStatus.CLOSED_UNSUCCESSFUL, CaseStatus.CLOSED_WITHDRAWN]
    result = await session.execute(
        select(Case.case_type, Case.created_at, Case.updated_at)
        .where(Case.is_deleted == False, Case.status.in_(closed_statuses))
    )
    by_type: dict = {}
    for row in result.all():
        case_type = row[0].value if hasattr(row[0], "value") else str(row[0])
        if row[1] and row[2]:
            days = (row[2] - row[1]).days
            by_type.setdefault(case_type, []).append(days)
    output = []
    for case_type, days_list in by_type.items():
        avg = sum(days_list) / len(days_list)
        sorted_days = sorted(days_list)
        n = len(sorted_days)
        median = sorted_days[n // 2] if n % 2 == 1 else (sorted_days[n // 2 - 1] + sorted_days[n // 2]) / 2
        output.append({"case_type": case_type, "avg_days": round(avg, 1), "median_days": round(median, 1)})
    return output


@router.get("/cases/status-distribution")
async def get_case_status_distribution(
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """Case counts by status."""
    from app.models.case import Case
    result = await session.execute(
        select(Case.status, func.count(Case.id))
        .where(Case.is_deleted == False)
        .group_by(Case.status)
    )
    return [{"status": row[0].value if hasattr(row[0], "value") else str(row[0]), "count": row[1]} for row in result.all()]


@router.get("/export/{report_type}")
async def export_report(
    report_type: str,
    date_from: date | None = None,
    date_to: date | None = None,
    format: str = Query(default="csv"),
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """Export a report as CSV or JSON."""
    from fastapi import HTTPException
    valid_types = {"kpis", "cases", "financial", "wealth", "staff"}
    if report_type not in valid_types:
        raise HTTPException(status_code=400, detail=f"Unknown report type: {report_type}. Valid: {', '.join(valid_types)}")
    data = {}
    if report_type == "kpis":
        data = await reporting_service.compute_kpis(session, date_from, date_to)
    elif report_type == "cases":
        data = await reporting_service.get_cases_dashboard(session)
    elif report_type == "financial":
        data = await reporting_service.get_financial_dashboard(session)
    elif report_type == "wealth":
        data = await reporting_service.get_wealth_dashboard(session)
    elif report_type == "staff":
        data = await reporting_service.get_staff_dashboard(session)
    if format == "csv":
        from app.utils.export import export_to_csv_bytes, generate_csv_response_headers
        rows = []
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, dict):
                    for sub_key, sub_value in value.items():
                        rows.append({"category": key, "metric": sub_key, "value": str(sub_value)})
                else:
                    rows.append({"category": "summary", "metric": key, "value": str(value)})
        csv_bytes = export_to_csv_bytes(rows)
        headers = generate_csv_response_headers(f"report_{report_type}.csv")
        return Response(content=csv_bytes, media_type="text/csv", headers=headers)
    return data
