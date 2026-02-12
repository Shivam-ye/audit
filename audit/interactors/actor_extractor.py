from typing import Dict, Any
from ..schemas import FlatActivity

class ActorExtractor:

    @staticmethod
    def extract(payload: dict, validated: Any, payload_type: str) -> tuple[Dict[str, Any], str]:
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

