from celery import Celery
import os
import sys

sys.path.append(os.getcwd())

REDIS_URL = os.getenv("REDIS_URL")

celery_app = Celery(
    "worker",
    broker=REDIS_URL,
    backend=REDIS_URL
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

# autodiscover
celery_app.autodiscover_tasks(["tasks"])

import tasks.character_tasks
import tasks.video_tasks
import tasks.image_tasks