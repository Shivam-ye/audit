import json
import uuid
from typing import Dict, Any
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import logging

# Setup logging for debugging (production mein file mein log kar sakte ho)
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def compute_changes(old_fields: Dict[str, Any], new_fields: Dict[str, Any], operation: str) -> Dict[str, Dict[str, Any]]:
    """
    Computes changes in {"old": val, "new": val} format.
    - Only includes changed fields.
    - For create: old = None for all new fields.
    - For delete: new = None for all old fields.
    - Handles nested dicts recursively if needed (for complex objects).
    - Skips unchanged fields to save storage.
    """
    changes = {}
    all_keys = set(old_fields.keys()) | set(new_fields.keys())

    def compute_diff(old_val: Any, new_val: Any) -> Dict[str, Any] | None:
        if old_val == new_val:
            return None
        return {"old": old_val, "new": new_val}

    for key in all_keys:
        old_val = old_fields.get(key)
        new_val = new_fields.get(key)

        # Handle nested dicts (recursive for bigger/complex JSON)
        if isinstance(old_val, dict) and isinstance(new_val, dict):
            nested_changes = compute_changes(old_val, new_val, operation)
            if nested_changes:
                changes[key] = nested_changes
            continue

        diff = compute_diff(old_val, new_val)
        if diff:
            changes[key] = diff

    # Operation-specific overrides
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
    """
    Auto-generates a human-readable summary if description not provided.
    E.g., "Status changed from todo to in_progress and due_date set to 2026-02-12"
    """
    if not changes:
        return "No changes detected"
    parts = []
    for field, diff in changes.items():
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
        logger.warning("Invalid method: %s", request.method)
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        logger.error("Invalid JSON in request")
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    # Normalize to list for bulk handling
    if isinstance(data, dict):
        activities = [data]
    elif isinstance(data, list):
        activities = data
    else:
        logger.error("Unsupported payload type")
        return JsonResponse({"error": "Payload must be dict or list"}, status=400)

    if not activities:
        return JsonResponse([], safe=False)

    now = timezone.now().isoformat()
    response_list = []

    for activity in activities:
        event_id = str(uuid.uuid4())

        # Extract with validation
        actor = activity.get("actor", {})
        if not actor.get("id"):
            logger.warning("Missing actor.id, skipping")
            continue

        operation = activity.get("verb", "").strip().lower()
        if operation not in {"create", "update", "delete"}:
            logger.warning("Invalid operation: %s, defaulting to unknown", operation)
            operation = "unknown"

        obj = activity.get("object", {})
        if not obj.get("id") or not obj.get("type"):
            logger.warning("Missing resource id/type, skipping")
            continue

        # Handle various input styles flexibly
        old_fields = obj.get("old_fields") or obj.get("before") or {}
        new_fields = obj.get("new_fields") or obj.get("after") or {}
        
        # Full fields support for create/delete/mixed
        if "fields" in obj:
            if operation == "create":
                new_fields = {**new_fields, **obj["fields"]}
            elif operation == "delete":
                old_fields = {**old_fields, **obj["fields"]}
            else:  # update
                # Assume fields are new for mixed
                new_fields = {**new_fields, **obj["fields"]}

        changes = compute_changes(old_fields, new_fields, operation)

        resource = {
            "type": obj.get("type", ""),
            "id": obj.get("id", "")
        }

        summary = activity.get("description", "").strip() or generate_summary(changes)

        response_item = {
            "event_id": event_id,
            "timestamp": activity.get("created_at") or now,
            "actor": {
                "id": actor.get("id", ""),
                "name": actor.get("name", ""),
                "type": actor.get("type", "user")
            },
            "operation": operation,
            "resource": resource,
            "changes": changes,
            "summary": summary
        }

        response_list.append(response_item)
        logger.info("Processed activity: %s by %s", operation, actor.get("id"))

    return JsonResponse(response_list, safe=False, status=201)

