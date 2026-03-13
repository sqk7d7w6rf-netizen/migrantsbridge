"""Celery tasks for report generation and periodic KPI computation."""

from __future__ import annotations

import asyncio
import json
import logging
from datetime import date, datetime, timedelta, timezone

from app.core.celery_app import celery_app

logger = logging.getLogger(__name__)


def _run_async(coro):
    """Helper to run async code in a sync Celery task."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery_app.task(bind=True, max_retries=2, default_retry_delay=120)
def generate_report(self, report_type: str, period_start: str | None = None, period_end: str | None = None) -> dict:
    """Generate a report and cache the results in Redis."""
    logger.info("Generating report: type=%s, period=%s to %s", report_type, period_start, period_end)

    async def _generate():
        from app.core.database import async_session_factory
        from app.core.redis import redis_client
        from app.services import reporting_service

        p_start = date.fromisoformat(period_start) if period_start else None
        p_end = date.fromisoformat(period_end) if period_end else None

        async with async_session_factory() as session:
            if report_type == "kpis":
                data = await reporting_service.compute_kpis(session, p_start, p_end)
            elif report_type == "overview":
                data = await reporting_service.get_overview_dashboard(session)
            elif report_type == "cases":
                data = await reporting_service.get_cases_dashboard(session)
            elif report_type == "financial":
                data = await reporting_service.get_financial_dashboard(session)
            elif report_type == "wealth":
                data = await reporting_service.get_wealth_dashboard(session)
            elif report_type == "staff":
                data = await reporting_service.get_staff_dashboard(session)
            else:
                logger.error("Unknown report type: %s", report_type)
                return {"status": "error", "message": f"Unknown report type: {report_type}"}

        # Cache in Redis with 1-hour TTL
        cache_key = f"report:{report_type}:{period_start}:{period_end}"
        await redis_client.setex(
            cache_key,
            3600,
            json.dumps(data, default=str),
        )

        logger.info("Report generated and cached: %s", cache_key)
        return {"status": "success", "report_type": report_type, "cache_key": cache_key}

    try:
        return _run_async(_generate())
    except Exception as exc:
        logger.exception("Report generation failed: type=%s", report_type)
        raise self.retry(exc=exc)


@celery_app.task
def compute_daily_kpis() -> dict:
    """Periodic task to compute and cache daily KPIs.

    Should be scheduled via Celery Beat to run once daily.
    """
    logger.info("Computing daily KPIs")

    async def _compute():
        from app.core.database import async_session_factory
        from app.core.redis import redis_client
        from app.services import reporting_service

        now = datetime.now(timezone.utc)
        today = now.date()
        month_start = today.replace(day=1)
        week_start = today - timedelta(days=today.weekday())

        async with async_session_factory() as session:
            # Daily KPIs
            daily = await reporting_service.compute_kpis(session, today, today)
            await redis_client.setex(
                f"kpis:daily:{today.isoformat()}",
                86400,
                json.dumps(daily, default=str),
            )

            # Weekly KPIs
            weekly = await reporting_service.compute_kpis(session, week_start, today)
            await redis_client.setex(
                f"kpis:weekly:{week_start.isoformat()}",
                86400,
                json.dumps(weekly, default=str),
            )

            # Monthly KPIs
            monthly = await reporting_service.compute_kpis(session, month_start, today)
            await redis_client.setex(
                f"kpis:monthly:{month_start.isoformat()}",
                86400,
                json.dumps(monthly, default=str),
            )

        logger.info("Daily KPIs computed and cached for %s", today.isoformat())
        return {
            "status": "success",
            "date": today.isoformat(),
            "daily": daily,
        }

    return _run_async(_compute())
