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
    "friday-kpi-digest": {
        "task": "app.workers.reporting_tasks.send_friday_kpi_digest",
        "schedule": crontab(hour=16, minute=0, day_of_week="fri"),
    },
    "monday-plate-digest": {
        "task": "app.workers.reporting_tasks.send_monday_plate_digest",
        "schedule": crontab(hour=8, minute=0, day_of_week="mon"),
    },
}

celery_app.autodiscover_tasks(["app.workers"])
