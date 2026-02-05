import json
import uuid
from typing import Dict, Any

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.core.cache import cache
import logging

from .models import AuditHistory

logger = logging.getLogger(__name__)


def compute_changes(old_fields: Dict[str, Any], new_fields: Dict[str, Any], operation: str) -> Dict[str, Dict[str, Any]]:
    changes = {}
    all_keys = set(old_fields.keys()) | set(new_fields.keys())

    def compute_diff(old_val: Any, new_val: Any) -> Dict[str, Any] | None:
        if old_val == new_val:
            return None
        return {"old": old_val, "new": new_val}

    for key in all_keys:
        old_val = old_fields.get(key)
        new_val = new_fields.get(key)

        if isinstance(old_val, dict) and isinstance(new_val, dict):
            nested_changes = compute_changes(old_val, new_val, operation)
            if nested_changes:
                changes[key] = nested_changes
            continue

        diff = compute_diff(old_val, new_val)
        if diff:
            changes[key] = diff

    if operation == "create":
        for key in new_fields:
            if key not in changes:
                changes[key] = {"old": None, "new": new_fields[key]}
    elif operation == "delete":
        for key in old_fields:
            if key not in changes:
                changes[key] = {"old": old_fields[key], "new": None}

    return changes


def generate_summary(changes: Dict[str, Dict[str, Any]]) -> str:
    if not changes:
        return "No changes detected"
    parts = []
    for field, diff in changes.items():
        if isinstance(diff.get("old"), dict) or "old" not in diff:
            parts.append(f"{field} updated")
            continue
        if diff["old"] is None:
            parts.append(f"{field} set to {diff['new']}")
        elif diff["new"] is None:
            parts.append(f"{field} removed")
        else:
            parts.append(f"{field} changed from {diff['old']} to {diff['new']}")
    return " and ".join(parts).capitalize()


@csrf_exempt
def activity_stream(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    activities = data if isinstance(data, list) else [data]
    if not activities:
        return JsonResponse([], safe=False)

    now = timezone.now()
    response_list = []

    for activity in activities:
        actor = activity.get("actor", {})
        obj = activity.get("object", {})
        obj_id = obj.get("id")
        obj_type = obj.get("type")

        if not actor.get("id") or not obj_id or not obj_type:
            logger.warning("Missing required fields, skipping")
            continue

        # Get last known fields from DB
        last_entry = AuditHistory.objects.filter(
            resource_type=obj_type,
            resource_id=obj_id
        ).order_by('-version').first()

        last_known_fields = last_entry.full_fields_after if last_entry else {}

        # New fields from request
        new_input_fields = obj.get("fields") or obj.get("new_fields") or {}

        # Determine operation
        operation = activity.get("verb", "").strip().lower()
        if not operation:
            if not last_known_fields and new_input_fields:
                operation = "create"
            elif last_known_fields and not new_input_fields:
                operation = "delete"
            else:
                operation = "update"

        # Compute differences
        changes = compute_changes(last_known_fields, new_input_fields, operation)

        if not changes and operation != "delete":
            logger.info("No changes detected for %s, skipping entry", obj_id)
            continue

        # Summary
        summary = activity.get("description", "").strip() or generate_summary(changes)

        # New version number
        new_version_number = (last_entry.version + 1) if last_entry else 1

        # Save to PostgreSQL
        audit_entry = AuditHistory.objects.create(
            resource_type=obj_type,
            resource_id=obj_id,
            version=new_version_number,
            operation=operation,
            actor_id=actor.get("id"),
            actor=actor,
            timestamp=activity.get("created_at") or now,
            event_id=uuid.uuid4(),
            changes=changes,
            summary=summary,
            full_fields_after=new_input_fields,
        )

        # Optional: cache last fields for faster next read
        cache.set(f"last_fields_{obj_type}_{obj_id}", new_input_fields, timeout=86400 * 7)

        response_item = {
            "resource": {"type": obj_type, "id": obj_id},
            "actor": actor,
            "current_update": {
                "version": audit_entry.version,
                "event_id": str(audit_entry.event_id),
                "timestamp": audit_entry.timestamp.isoformat(),
                "operation": audit_entry.operation,
                "changes": audit_entry.changes,
                "summary": audit_entry.summary,
            },
        }

        response_list.append(response_item)

    return JsonResponse(response_list, safe=False, status=201)