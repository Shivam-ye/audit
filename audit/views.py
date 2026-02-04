import json
import uuid
from typing import Any, Dict, List, Optional, Union
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone


def compute_changes(
    old: Optional[Dict[str, Any]] = None,
    new: Optional[Dict[str, Any]] = None,
    full_object: Optional[Dict[str, Any]] = None,
) -> Dict[str, List[Any]]:
    """
    Compute diff in the [old, new] format.
    - create: [null, value]
    - update: [old_value, new_value] only for changed keys
    - delete: [old_value, null]
    """
    old = old or {}
    new = new or {}
    changes = {}

    # ── Case: full object provided (common in create / simple update)
    if full_object is not None:
        for k, v in full_object.items():
            changes[k] = [None, v]  # treat as create-style
        return changes

    # ── Classic old_fields + new_fields style
    all_keys = set(old.keys()) | set(new.keys())

    for key in all_keys:
        old_val = old.get(key)
        new_val = new.get(key)

        # Skip unchanged fields (very useful for update events)
        if old_val == new_val:
            continue

        # Special case: field removed → [old, None]
        if key in old and key not in new:
            changes[key] = [old_val, None]
        # Field added → [None, new]
        elif key not in old and key in new:
            changes[key] = [None, new_val]
        # Changed
        else:
            changes[key] = [old_val, new_val]

    return changes


@csrf_exempt
def activity_stream(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method Not Allowed – only POST"}, status=405)

    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": f"Parse error: {str(e)}"}, status=400)

    # Normalize to list
    if isinstance(payload, dict):
        activities = [payload]
    elif isinstance(payload, list):
        activities = payload
    else:
        return JsonResponse({"error": "Payload must be object or array"}, status=400)

    if not activities:
        return JsonResponse([], safe=False)

    now = timezone.now().isoformat()

    response_list: List[Dict] = []

    for activity in activities:
        act_id = str(uuid.uuid4())

        # ── Extract core fields with safe defaults
        actor = activity.get("actor") or {}
        verb = str(activity.get("verb", "")).strip().lower()

        if not verb:
            continue  # skip invalid entries

        obj_input = activity.get("object", {}) or {}

        obj_id = obj_input.get("id", "")
        obj_type = obj_input.get("type", "")

        # ── Try multiple common input patterns
        old_fields = obj_input.get("old_fields") or obj_input.get("before") or {}
        new_fields = obj_input.get("new_fields") or obj_input.get("after") or {}
        full_obj = obj_input.get("fields") or obj_input.get("data") or None

        # Compute changes
        changes = compute_changes(
            old=old_fields,
            new=new_fields,
            full_object=full_obj,
        )

        # For delete events → make it more explicit
        if verb == "delete" and changes:
            # Ensure removed fields show [value, null]
            pass  # already handled

        response_item = {
            "id": act_id,
            "actor": {
                "id": actor.get("id", ""),
                "name": actor.get("name", ""),
                "type": actor.get("type", "user"),
                # add more if you have them (email, role, etc.)
            },
            "verb": verb,
            "object_type": obj_type,
            "object_id": obj_id,
            "changes": changes,               # ← renamed from "fields" – more clear
            # Alternative: keep "fields" if you must stay 100% compatible
            # "fields": changes,
            "description": str(activity.get("description", "")).strip(),
            "created_at": activity.get("created_at") or now,
            "updated_at": activity.get("updated_at") or now,
            # Optional – very useful for debugging / filtering
            # "source": "api" / "web" / "system"
        }

        response_list.append(response_item)

    return JsonResponse(response_list, safe=False, status=201)