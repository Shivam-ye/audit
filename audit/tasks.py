from __future__ import annotations
import logging
from typing import Optional

from .config import app as celery_app
from .enums import CeleryTaskName, CeleryTaskQueue
from .interactors.activity_interactor import ActivityInteractor
from .models import Message

logger = logging.getLogger(__name__)


@celery_app.task(
    bind=True,
    name=CeleryTaskName.AUDIT_LOGS,
    queue=CeleryTaskQueue.AUDIT_LOG_QUEUE,
    max_retries=2,
)
def process_audit_log(
    self,
    payload: dict,
    *,
    db_message: Optional[Message] = None,
    **kwargs
):
    """
    Celery task to process audit log payloads.
    
    Args:
        payload: The payload dict containing audit log data
        db_message: Optional Message model instance for async processing
        **kwargs: Additional keyword arguments
    """
    try:
        logger.info(f"Processing audit log payload")
        logger.info(f"Payload Received: {payload}")
        
        # Extract the actual payload data
        # Handle both new wrapped format and legacy format
        if isinstance(payload, dict) and payload.get("type") == "audit_logs" and "payload" in payload:
            # New wrapped format: {"id": "uuid", "type": "audit_logs", "payload": {...}}
            payloads = payload.get("payload", {})
            original_payload = payload
        else:
            # Legacy format
            payloads = payload
            original_payload = None
        
        logger.info(f"Extracted payloads: {payloads}")
        
        # Process the payload through the activity interactor
        result = ActivityInteractor.process_payloads(payloads, original_payload=original_payload)
        
        logger.info(f"Audit log processing completed successfully. Result: {result}")
        
        # Update message status if db_message is provided
        if db_message:
            db_message.status = "completed"
            db_message.save()
        
        return result
        
    except Exception as exc:
        logger.error(f"Audit log processing failed: {exc}")
        
        # Update message status if db_message is provided
        if db_message:
            db_message.status = "failed"
            db_message.error_message = str(exc)
            db_message.save()
        
        raise self.retry(exc=exc, countdown=20)


@celery_app.task(
    bind=True,
    name=CeleryTaskName.AUDIT_LOG_PROCESS,
    queue=CeleryTaskQueue.AUDIT_LOG_QUEUE,
    max_retries=2,
)
def process_activity_task(self, payload):
    """
    Celery task to process activity payloads.
    
    Args:
        payload: The payload dict containing activity data (can be wrapped or legacy format)
    """
    try:
        logger.info(f"Processing activity payload")
        logger.info(f"Payload Received: {payload}")
        
        # Extract the actual payload data
        # Handle both new wrapped format and legacy format
        if isinstance(payload, dict) and payload.get("type") == "audit_logs" and "payload" in payload:
            # New wrapped format: {"id": "uuid", "type": "audit_logs", "payload": {...}}
            payloads = payload.get("payload", {})
            original_payload = payload
        else:
            # Legacy format
            payloads = payload
            original_payload = None
        
        logger.info(f"Extracted payloads: {payloads}")
        
        # Process the payload through the activity interactor
        result = ActivityInteractor.process_payloads(payloads, original_payload=original_payload)
        
        logger.info(f"Activity processing completed. Result: {result}")
        return result
    except Exception as exc:
        logger.error(f"Activity processing failed: {exc}")
        raise self.retry(exc=exc, countdown=20)

