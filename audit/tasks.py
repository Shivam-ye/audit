from celery import shared_task
from .interactors.activity_interactor import ActivityInteractor


@shared_task(bind=True, max_retries=2,queue="audit_log_queue")
def process_activity_task(self, payloads):
    try:
        return ActivityInteractor.process_payloads(payloads)
    except Exception as exc:
        raise self.retry(exc=exc, countdown=20)

