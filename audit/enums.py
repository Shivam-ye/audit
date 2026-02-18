from enum import Enum

class CeleryTaskName(str, Enum):
    """Celery task names for audit processing"""
    AUDIT_LOG_PROCESS = "audit_log_process"
    AUDIT_LOGS = "audit_logs"


class CeleryTaskQueue(str, Enum):
    """Celery task queue names"""
    AUDIT_LOG_QUEUE = "audit_log_queue"
    DEFAULT = "default"


# Import MessageStatus from tools_box
from tools_box.workers.enums import MessageStatus

__all__ = ['CeleryTaskName', 'CeleryTaskQueue', 'MessageStatus']

