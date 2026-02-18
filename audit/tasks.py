from __future__ import annotations
import logging
from typing import Optional, Any

from .config import app as celery_app
from .enums import CeleryTaskName, CeleryTaskQueue, MessageStatus
from .interactors.activity_interactor import ActivityInteractor
from .models import Message
from tools_box.workers.config import CeleryBaseConfig as BaseCeleryBaseConfig
from tools_box.newrelic.metric_client import NewRelicMetricsClientImpl


logger = logging.getLogger(__name__)


class AuditCeleryBaseConfig(BaseCeleryBaseConfig):
    """
    Custom CeleryBaseConfig that uses audit.models.Message instead of apps.payout.models.message.Message
    """
    task_registery: dict[str, Any] = {}
    autoretry_for = (Exception,)
    retry_backoff = True
    retry_kwargs = {"max_retries": 3}
    retryable_status = [MessageStatus.PENDING, MessageStatus.RETRY]

    def __init__(self):
        self.message_model = Message
        self.new_relic_client = NewRelicMetricsClientImpl()
        self.message_key = "db_message"
        self.logger = logging.getLogger(__name__)


def update_message_status(message_id: str, status: str, error_message: str = None):
    """
    Helper function to update Message status.
    
    Args:
        message_id: UUID of the message to update
        status: Status to set ('completed' or 'failed')
        error_message: Optional error message for failed status
    """
    if message_id:
        try:
            db_message = Message.objects.get(id=message_id)
            db_message.status = status
            if error_message:
                db_message.error_message = error_message
            db_message.save()
            logger.info(f"Updated message {message_id} status to {status}")
        except Message.DoesNotExist:
            logger.warning(f"Message {message_id} not found")


@celery_app.task(
    bind=True,
    base=AuditCeleryBaseConfig,
    name=CeleryTaskName.AUDIT_LOGS,
    queue=CeleryTaskQueue.AUDIT_LOG_QUEUE,
    max_retries=2,
)
def process_audit_log(
    self,
    payload: dict,
    *,
    message_id: Optional[str] = None,
    **kwargs
):
    """
    Celery task to process audit log payloads.
    
    Args:
        payload: The payload dict containing audit log data
        message_id: Optional UUID of the Message record to track status
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
        
        # Update message status if message_id is provided
        if message_id:
            update_message_status(message_id, "completed")
        
        return result
        
    except Exception as exc:
        logger.error(f"Audit log processing failed: {exc}")
        
        # Update message status if message_id is provided
        if message_id:
            update_message_status(message_id, "failed", str(exc))
        
        raise self.retry(exc=exc, countdown=20)


@celery_app.task(
    bind=True,
    base=AuditCeleryBaseConfig,
    name=CeleryTaskName.AUDIT_LOG_PROCESS,
    queue=CeleryTaskQueue.AUDIT_LOG_QUEUE,
    max_retries=2,
)
def process_activity_task(self, payload, message_id: Optional[str] = None):
    """
    Celery task to process activity payloads.
    
    Args:
        payload: The payload dict containing activity data (can be wrapped or legacy format)
        message_id: Optional UUID of the Message record to track status
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
        
        # Update message status if message_id is provided
        if message_id:
            update_message_status(message_id, "completed")
        
        return result
    except Exception as exc:
        logger.error(f"Activity processing failed: {exc}")
        
        # Update message status if message_id is provided
        if message_id:
            update_message_status(message_id, "failed", str(exc))
        
        raise self.retry(exc=exc, countdown=20)