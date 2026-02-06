import json
import uuid
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .models import AuditHistory
# from deepdiff import DeepDiff
# from typing import Any, Dict, Optional


def compute_changed_fields(old_dict, new_dict):
    changes = {}
    all_keys = set(old_dict) | set(new_dict)
    for key in all_keys:
        old_val = old_dict.get(key)
        new_val = new_dict.get(key)
        if old_val != new_val:
            changes[key] = [old_val, new_val]
    return changes


def make_summary(changes):
    if not changes:
        return ""
    parts = []
    for field, (old, new) in changes.items():
        if old is None:
            parts.append(f"{field} set to {new}")
        elif new is None:
            parts.append(f"{field} removed")
        else:
            parts.append(f"{field} changed from {old} to {new}")
    return " and ".join(parts).capitalize()


@csrf_exempt
def activity_stream(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    items = data if isinstance(data, list) else [data]
    if not items:
        return JsonResponse([], safe=False)

    response = []

    for item in items:
        actor = item.get("actor", {})
        verb = item.get("verb", "").strip().lower()
        obj = item.get("object", {})

        obj_id = obj.get("id")
        obj_type = obj.get("type")

        # New state = remove id & type, rest is fields
        new_fields = {k: v for k, v in obj.items() if k not in ("id", "type")}

        if not actor.get("id") or not obj_id or not obj_type or not verb:
            continue

        # Get previous snapshot
        last = AuditHistory.objects.filter(
            resource_type=obj_type,
            resource_id=obj_id
        ).order_by('-version').first()

        old_fields = last.full_fields_after if last else {}

        # Map verb to display form
        verb_map = {
            "created": "created",
            "updated": "updated",
            "deleted": "deleted"
        }
        display_verb = verb_map.get(verb, verb)

        changes = compute_changed_fields(old_fields, new_fields)

        # Skip if no real change (except delete)
        if not changes and verb != "deleted":
            continue

        summary = make_summary(changes)

        now = timezone.now()

        # Save
        AuditHistory.objects.create(
            resource_type=obj_type,
            resource_id=obj_id,
            version=(last.version + 1) if last else 1,
            operation=verb,
            actor=actor,
            actor_id=actor.get("id"),
            changes=changes,
            summary=summary,
            full_fields_after=new_fields,
            timestamp=now,
        )

        # Response item - exactly 6 keys
        response.append({
            "id": str(uuid.uuid4()),
            "actor": actor,
            "verb": display_verb,
            "object": {
                "id": obj_id,
                "type": obj_type,
                "fields": changes
            },
            "description": summary,
            "created_at": now.isoformat(),
            "updated_at": now.isoformat()
        })

    return JsonResponse(response, safe=False)