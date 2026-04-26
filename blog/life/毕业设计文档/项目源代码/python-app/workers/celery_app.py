from celery import Celery
from app.core.config import settings
from app.services.layout_service import celery_generate_layout, celery_generate_model

celery_app = Celery(
    "city_platform",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)
