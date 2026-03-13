"""Reporting API routes: KPIs, dashboards, report generation."""

from datetime import date

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.core.security import get_current_user
from app.services import reporting_service

router = APIRouter()


@router.get("/kpis")
async def get_kpis(
    period_start: date | None = None,
    period_end: date | None = None,
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user),
):
    """Get key performance indicators."""
    return await reporting_service.compute_kpis(session, period_start, period_end)


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
