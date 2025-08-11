from __future__ import annotations

try:
    from .celery import app as celery_app  # noqa: F401
except Exception:
    # Celery not configured yet; safe import guard
    celery_app = None  # type: ignore