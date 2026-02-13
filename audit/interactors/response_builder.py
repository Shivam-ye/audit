from typing import Dict, Any
from django.utils import timezone
import uuid

class ResponseBuilder:

    @staticmethod
    def build(actor_full: dict, res_id: str, res_type: str, changes: dict, summary: str) -> dict:
        now = timezone.now()
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

