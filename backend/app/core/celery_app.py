from celery import Celery
from celery.schedules import crontab as _crontab

from app.config import settings

celery_app = Celery(
    "migrantsbridge",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    result_expires=3600,
    broker_connection_retry_on_startup=True,
)

celery_app.autodiscover_tasks(["app.workers"])

# Learning Center agent schedules (Asia/Bangkok = UTC+7)
celery_app.conf.beat_schedule = {
    # Agent 1: Lesson plan review — Sunday 8:05pm Bangkok (13:05 UTC)
    # Runs 5 minutes after submission deadline to collect all plans
    "lesson-plan-review-sunday": {
        "task": "app.workers.learning_center_tasks.review_lesson_plans",
        "schedule": _crontab(hour=13, minute=5, day_of_week=0),  # 0=Sunday
        "args": ([],),  # plans injected via API trigger; fallback = empty
    },
    # Agent 4: Weekly KPI compiler — Monday 9am Bangkok (02:00 UTC)
    "weekly-kpi-compiler-monday": {
        "task": "app.workers.learning_center_tasks.compile_weekly_kpis",
        "schedule": _crontab(hour=2, minute=0, day_of_week=1),  # 1=Monday
        "args": ({},),  # data injected by Google Sheets sync; fallback = empty
    },
    # Agent 6: Buddy program tracker — Friday 3pm Bangkok (08:00 UTC)
    "buddy-program-tracker-friday": {
        "task": "app.workers.learning_center_tasks.track_buddy_program",
        "schedule": _crontab(hour=8, minute=0, day_of_week=5),  # 5=Friday
        "args": (1, [], [], ""),  # week_number updated each week
    },
    # Appointment reminders — every 10 minutes
    "send-appointment-reminders": {
        "task": "app.workers.reminder_tasks.send_appointment_reminders",
        "schedule": 600,  # every 10 minutes
    },

    # ── Talart Thai Vegetable Business agents (Asia/Bangkok = UTC+7) ──────────

    # Morning Buy Advisor — 5:30am Bangkok daily (22:30 UTC previous day)
    "vegbiz-morning-buy-advisor": {
        "task": "app.workers.vegetable_biz_tasks.morning_buy_advisor",
        "schedule": _crontab(hour=22, minute=30),
        "args": ({}, {}, []),  # data loaded from Google Sheets at runtime
    },
    # 3pm Waste Reducer — 3pm Bangkok daily (8:00 UTC)
    "vegbiz-afternoon-waste-reducer": {
        "task": "app.workers.vegetable_biz_tasks.afternoon_waste_reducer",
        "schedule": _crontab(hour=8, minute=0),
        "args": ({}, {}),
    },
    # Weekly Commission Report — Sunday 8pm Bangkok (13:00 UTC Sunday)
    "vegbiz-weekly-commission": {
        "task": "app.workers.vegetable_biz_tasks.weekly_commission_report",
        "schedule": _crontab(hour=13, minute=0, day_of_week=0),  # 0=Sunday
        "args": ([],),  # sales_data loaded from Google Sheets at runtime
    },
}
