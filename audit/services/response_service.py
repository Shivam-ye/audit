import logging
from django.utils import timezone
import uuid

logger = logging.getLogger(__name__)


class ResponseService:
    """Service for building responses - business logic moved from ResponseBuilder"""

    @staticmethod
    def build_response(actor_full: dict, res_id: str, res_type: str, changes: dict, summary: str) -> dict:
        """
        Build a standardized response dictionary.
        
        Args:
            actor_full: Full actor information dict
            res_id: Resource ID string
            res_type: Resource type string
            changes: Dictionary of changes
            summary: Summary string
            
        Returns:
            Response dictionary
        """
        now = timezone.now()
        
        # Log the full changes for debugging
        logger.info(f"Full changes computed: {changes}")
        
        return {
            "id": str(uuid.uuid4()),
            "actor": actor_full,
            "verb": "updated",  # You can modify to pass actual verb if needed
            "object": {
                "id": res_id,
                "type": res_type,
                "fields": changes
            },
            "description": summary,
            "created_at": now.isoformat(),
            "updated_at": now.isoformat()
        }

