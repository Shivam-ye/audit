import json
import uuid
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from deepdiff import DeepDiff
from .models import AuditHistory


def flatten_dict(d, parent_key='', sep='.'):
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def clean_path(path):
    if path.startswith("root['") and path.endswith("']"):
        return path[6:-2]
    if path.startswith("root."):
        return path[5:]
    return path


def compute_diff(old_data, new_data):
    if not old_data:
        flat_new = flatten_dict(new_data)
        return {clean_path(k): [None, v] for k, v in flat_new.items()}

    diff = DeepDiff(old_data, new_data, ignore_order=True, verbose_level=2)

    changes = {}

    # Added fields
    if 'values_added' in diff:
        for path, value in diff['values_added'].items():
            changes[clean_path(path)] = [None, value]

    if 'dictionary_item_added' in diff:
        for path, value in diff['dictionary_item_added'].items():
            changes[clean_path(path)] = [None, value]

    # Removed fields - yeh important fix hai
    if 'values_removed' in diff:
        for path, value in diff['values_removed'].items():
            changes[clean_path(path)] = [value, None]

    if 'dictionary_item_removed' in diff:
        for path, value in diff['dictionary_item_removed'].items():
            changes[clean_path(path)] = [value, None]

    # Changed values
    if 'values_changed' in diff:
        for path, change in diff['values_changed'].items():
            changes[clean_path(path)] = [change['old_value'], change['new_value']]

    # Type changes
    if 'type_changes' in diff:
        for path, change in diff['type_changes'].items():
            changes[clean_path(path)] = [change['old_value'], change['new_value']]

    return changes


def generate_summary(changes):
    if not changes:
        return "No changes detected"

    parts = []
    for field_path, (old, new) in changes.items():
        field = clean_path(field_path).replace('.', ' → ')
        if old is None:
            parts.append(f"{field} set to {new}")
        elif new is None:
            parts.append(f"{field} removed (was {old})")
        else:
            parts.append(f"{field} changed from {old} to {new}")

    return " and ".join(parts).capitalize()


def find_actor_id(data):
    candidates = [
        'actor.id', 'actor_id', 'user_id', 'user', 'username',
        'created_by', 'updated_by', 'by', 'author'
    ]
    for key in candidates:
        keys = key.split('.')
        value = data
        for k in keys:
            value = value.get(k, {})
        if value and isinstance(value, (str, int)):
            return str(value)
    return "unknown"


def find_resource_id(data):
    for key in ['id', 'object_id', 'entity_id', 'resource_id', 'record_id', 'task_id']:
        if key in data:
            return str(data[key])
    return str(uuid.uuid4())


def find_resource_type(data):
    return "unknown"


verb_map = {
    "create": "created",
    "created": "created",
    "add": "created",
    "update": "updated",
    "updated": "updated",
    "edit": "updated",
    "change": "updated",
    "delete": "deleted",
    "deleted": "deleted",
    "remove": "deleted"
}


@csrf_exempt
def activity_stream(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    items = data if isinstance(data, list) else [data]

    result = []

    for payload in items:
        actor_id = find_actor_id(payload)
        resource_id = find_resource_id(payload)
        resource_type = find_resource_type(payload)

        verb_raw = (
            payload.get("verb") or
            payload.get("action") or
            payload.get("event") or
            payload.get("operation") or
            "updated"
        ).lower().strip()

        verb = verb_map.get(verb_raw, "updated")

        exclude = {
            "verb", "action", "event", "operation",
            "actor", "actor_id", "user_id", "user", "username",
            "id", "object_id", "entity_id", "resource_id", "task_id"
        }
        fields = {k: v for k, v in payload.items() if k not in exclude}

        if "object" in payload and isinstance(payload["object"], dict):
            fields.update(payload["object"])
        if "data" in payload and isinstance(payload["data"], dict):
            fields.update(payload["data"])

        last_entry = AuditHistory.objects.filter(
            resource_type=resource_type,
            resource_id=resource_id
        ).order_by('-version').first()

        old_fields = last_entry.full_fields_after if last_entry else {}

        changes = compute_diff(old_fields, fields)

        summary = generate_summary(changes)

        now = timezone.now()

        AuditHistory.objects.create(
            resource_type=resource_type,
            resource_id=resource_id,
            version=(last_entry.version + 1) if last_entry else 1,
            operation=verb,
            actor={"id": actor_id},
            actor_id=actor_id,
            changes=changes,
            summary=summary,
            full_fields_after=fields,
            timestamp=now,
        )

        result.append({
            "id": str(uuid.uuid4()),
            "actor": {
                "id": actor_id
            },
            "verb": verb,
            "object": {
                "id": resource_id,
                "type": resource_type,
                "fields": changes
            },
            "description": summary,
            "created_at": now.isoformat(),
            "updated_at": now.isoformat()
        })

    return JsonResponse(result, safe=False)