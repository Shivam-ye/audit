from django.utils import timezone
from ..models import AuditHistory


class HistoryService:
    """Service for database operations on AuditHistory - business logic moved from ActivityInteractor"""

    @staticmethod
    def get_last_history(res_type: str, res_id: str):
        """
        Get the last AuditHistory record for a resource.
        
        Args:
            res_type: Resource type
            res_id: Resource ID
            
        Returns:
            AuditHistory object or None
        """
        return AuditHistory.objects.filter(
            resource_type=res_type,
            resource_id=res_id
        ).order_by('-version').first()

    @staticmethod
    def create_history(res_type: str, res_id: str, operation: str, actor_full: dict, 
                       actor_id: str, changes: dict, summary: str, data: dict, last_version: int = None):
        """
        Create a new AuditHistory record.
        
        Args:
            res_type: Resource type
            res_id: Resource ID
            operation: Operation type (created, updated, deleted)
            actor_full: Full actor information dict
            actor_id: Actor ID string
            changes: Dictionary of changes
            summary: Summary string
            data: Full fields after dict
            last_version: Previous version number (if exists)
            
        Returns:
            Created AuditHistory object in the similar form
        """
        version = (last_version + 1) if last_version else 1
        now = timezone.now()
        
        return AuditHistory.objects.create(
            resource_type=res_type,
            resource_id=res_id,
            version=version,
            operation=operation,
            actor=actor_full,
            actor_id=actor_id,
            changes=changes,
            summary=summary,
            full_fields_after=data,
            timestamp=now,
        )
    print("task_completed")

