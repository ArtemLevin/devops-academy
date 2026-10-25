"""Pure and idempotent Celery fixture; no real services or student data."""
import os
from celery import Celery

app = Celery(
    "academy",
    broker=os.environ.get("CELERY_BROKER_URL", "redis://redis:6379/0"),
    backend=os.environ.get("CELERY_RESULT_BACKEND", "redis://redis:6379/1"),
)
app.conf.update(
    task_serializer="json", result_serializer="json", accept_content=["json"],
    task_acks_late=True, worker_prefetch_multiplier=1,
)


@app.task(name="academy.square")
def square(number: int) -> int:
    """Result is deterministic; retrying does not create duplicate side effects."""
    return number * number
