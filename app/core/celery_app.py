import os
from celery import Celery

# Default to local redis if not set
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

celery_app = Celery("ghosthire", broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_soft_time_limit=300, # 5 min limit per task for free tier safety
    worker_concurrency=2, # Limit concurrency
)

# Auto-discover tasks in packages
celery_app.autodiscover_tasks(["app.services.orchestrator.tasks"])
