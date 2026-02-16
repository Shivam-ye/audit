from typing import Dict, Any
from ..schemas import FlatActivity


class ActorService:
    """Service for extracting actor information - business logic moved from ActorExtractor"""

    @staticmethod
    def extract_actor(payload: dict, validated: Any, payload_type: str) -> tuple[Dict[str, Any], str]:
        """
        Extract actor information from various payload formats.
        
        Args:
            payload: The raw payload dictionary
            validated: The validated Pydantic model
            payload_type: Type of payload ('object', 'resource', or 'flat')
            
        Returns:
            Tuple of (actor_full dict, actor_id string)
        """
        actor_full = {"id": "unknown"}
        actor_id = "unknown"

        if payload_type in ["object", "resource"]:
            actor_full = validated.actor.model_dump(exclude_none=True)
            actor_id = validated.actor.id
        elif payload_type == "flat":
            flat: FlatActivity = validated
            if flat.actor:
                actor_full = flat.actor.model_dump(exclude_none=True)
                actor_id = flat.actor.id
            elif flat.actor_id:
                actor_id = str(flat.actor_id)
                actor_full = {"id": actor_id}
            elif "actor" in payload and isinstance(payload["actor"], dict) and "id" in payload["actor"]:
                actor_full = payload["actor"].copy()
                actor_id = str(payload["actor"]["id"])
            else:
                actor_id = payload.get("user_id") or payload.get("created_by") or "unknown"
                actor_full = {"id": actor_id}

        return actor_full, actor_id

