from celery import Celery
from celery.schedules import crontab

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

celery_app.conf.beat_schedule = {
    "send-appointment-reminders": {
        "task": "app.workers.reminder_tasks.send_appointment_reminders",
        "schedule": crontab(minute="*/10"),
    },
    "compute-daily-kpis": {
        "task": "app.workers.reporting_tasks.compute_daily_kpis",
        "schedule": crontab(hour=6, minute=0),
    },
    "post-daily-pulse-to-slack": {
        "task": "app.workers.reporting_tasks.post_daily_pulse_to_slack",
        "schedule": crontab(hour=6, minute=15),
    },
}

celery_app.autodiscover_tasks(["app.workers"])
