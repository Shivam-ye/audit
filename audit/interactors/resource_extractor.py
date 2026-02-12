import uuid
from typing import Dict, Any
from ..schemas import FlatActivity

class ResourceExtractor:

    @staticmethod
    def extract(payload: dict, validated: Any, payload_type: str) -> tuple[str, str, dict]:
        res_id = str(uuid.uuid4())
        res_type = "unknown"
        data: Dict[str, Any] = {}

        if payload_type == "object":
            res_id = validated.object.id
            res_type = validated.object.type
            data = payload["object"].copy()
        elif payload_type == "resource":
            res_id = validated.resource.id
            res_type = validated.resource.type
            data = payload["resource"].copy()
        elif payload_type == "flat":
            flat: FlatActivity = validated
            if flat.id:
                res_id = str(flat.id)
            if flat.type:
                res_type = flat.type
            if "object" in payload and isinstance(payload["object"], dict):
                obj = payload["object"]
                if "id" in obj and not flat.id:
                    res_id = str(obj["id"])
                if obj.get("type") and res_type == "unknown":
                    res_type = str(obj["type"])
                data = obj.copy()
            if not data:
                exclude = {
                    "verb", "action", "event", "operation",
                    "actor", "actor_id", "user_id", "by", "created_by", "updated_by",
                    "id", "type", "object", "resource", "context", "description",
                    "object_type", "resource_type"
                }
                data = {k: v for k, v in payload.items() if k not in exclude}

        # Remove id/type from data
        data.pop("id", None)
        data.pop("type", None)

        return res_id, res_type, data
