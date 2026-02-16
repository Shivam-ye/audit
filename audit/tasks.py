import logging
from celery import shared_task
from .interactors.activity_interactor import ActivityInteractor

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=2, queue="audit_log_queue")
def process_activity_task(self, payloads):
    try:
        result = ActivityInteractor.process_payloads(payloads)
        logger.info(f"Activity processing completed successfully. Result: {result}")
        return result
    except Exception as exc:
        logger.error(f"Activity processing failed: {exc}")
        raise self.retry(exc=exc, countdown=20)

