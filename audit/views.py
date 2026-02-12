import json
import uuid
from typing import Dict, Any
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from pydantic import ValidationError
from .models import AuditHistory
from .schemas import FlatActivity, ActivityWithObject, ActivityWithResource
from .services.audit_service import  compute_diff ,generate_summary, verb_map

@csrf_exempt
def activity_stream(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    try:
        raw_data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    items = raw_data if isinstance(raw_data, list) else [raw_data]
    result = []

    for payload in items:
        actor_id = "unknown"
        actor_full = {"id": "unknown"}
        res_id = str(uuid.uuid4())
        res_type = "unknown"
        data: Dict[str, Any] = {}

        try:
            # Structured to object
            if "object" in payload and isinstance(payload["object"], dict) and "type" in payload["object"]:
                validated = ActivityWithObject.model_validate(payload)
                actor_full = validated.actor.model_dump(exclude_none=True)
                actor_id = validated.actor.id
                res_id = validated.object.id
                res_type = validated.object.type
                data = payload["object"].copy()
                data.pop("id", None)
                data.pop("type", None)

            # Structured to resource
            elif "resource" in payload and isinstance(payload["resource"], dict) and "type" in payload["resource"]:
                validated = ActivityWithResource.model_validate(payload)
                actor_full = validated.actor.model_dump(exclude_none=True)
                actor_id = validated.actor.id
                res_id = validated.resource.id
                res_type = validated.resource.type
                data = payload["resource"].copy()
                data.pop("id", None)
                data.pop("type", None)

            # Flat / mixed style
            else:
                flat = FlatActivity.model_validate(payload)

                # Actor
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

                # ID & Type
                if flat.id:
                    res_id = str(flat.id)
                if flat.type:
                    res_type = flat.type

                # Prefer nested object for data + id + type
                if "object" in payload and isinstance(payload["object"], dict):
                    obj = payload["object"]
                    if "id" in obj and not flat.id:
                        res_id = str(obj["id"])
                    if obj.get("type") and res_type == "unknown":
                        res_type = str(obj["type"])
                    data = obj.copy()
                    data.pop("id", None)
                    data.pop("type", None)

                # Last fallback — root level (excluding metadata)
                if not data:
                    exclude = {
                        "verb", "action", "event", "operation",
                        "actor", "actor_id", "user_id", "by", "created_by", "updated_by",
                        "id", "type", "object", "resource", "context", "description",
                        "object_type", "resource_type"
                    }
                    data = {k: v for k, v in payload.items() if k not in exclude}

        except ValidationError as e:
            errors = [
                {"field": ".".join(map(str, err['loc'])), "message": err['msg']}
                for err in e.errors(include_url=False, include_input=False)
            ]
            return JsonResponse({"error": "Validation failed", "details": errors}, status=422)

        # Enforce type for non-delete operations
        verb_raw = payload.get("verb", "updated").lower().strip()
        verb = verb_map.get(verb_raw, "updated")

        if res_type == "unknown" and verb not in ["deleted", "delete"]:
            return JsonResponse({
                "error": "Resource type is required for create/update",
                "details": [{
                    "field": "type / object.type / resource.type / object_type / resource_type",
                    "message": "Required and cannot be empty"
                }]
            }, status=422)

        # Diff & save
        last = AuditHistory.objects.filter(
            resource_type=res_type,
            resource_id=res_id
        ).order_by('-version').first()

        old = last.full_fields_after if last else {}
        changes = compute_diff(old, data)
        summary = generate_summary(changes)
        now = timezone.now()

        AuditHistory.objects.create(
            resource_type=res_type,
            resource_id=res_id,
            version=(last.version + 1) if last else 1,
            operation=verb,
            actor=actor_full,
            actor_id=actor_id,
            changes=changes,
            summary=summary,
            full_fields_after=data,
            timestamp=now,
        )

        # Response
        result.append({
            "id": str(uuid.uuid4()),
            "actor": actor_full,
            "verb": verb,
            "object": {
                "id": res_id,
                "type": res_type,
                "fields": changes
            },
            "description": summary,
            "created_at": now.isoformat(),
            "updated_at": now.isoformat()
        })

    return JsonResponse(result, safe=False)