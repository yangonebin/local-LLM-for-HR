from celery import Celery

celery_app = Celery(
    "hr_llm",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/1",
    include=["tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Asia/Seoul",
    enable_utc=True,
    task_track_started=True,
)
