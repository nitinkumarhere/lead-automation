import os
from celery import Celery

# Explicitly pass the 'include' argument containing the module string path
celery_app = Celery(
    "tasks",
    broker=os.getenv("REDIS_URL", "redis://redis:6379/0"),
    backend=os.getenv("REDIS_URL", "redis://redis:6379/0"),
    include=["app.tasks"]  # <--- CRITICAL: Tells the worker to eagerly register all tasks!
)

# Configuration tweaks for production-level stability
celery_app.conf.update(
    task_track_started=True,
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC"
)
