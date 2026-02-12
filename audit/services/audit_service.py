from typing import Dict
from django.views.decorators.csrf import csrf_exempt
from deepdiff import DeepDiff

# Utility Functions
def flatten_dict(d: Dict, parent_key: str = '', sep: str = '.') -> Dict:
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def clean_path(path: str) -> str:
    path = path.replace("root", "").strip(".")
    path = path.replace("['", ".").replace("']", "")
    path = path.replace("][", ".")
    return path.strip(".")


def compute_diff(old_data: Dict, new_data: Dict) -> Dict[str, list]:
    changes = {}

    if not old_data:  # Create
        flat_new = flatten_dict(new_data)
        for k, v in flat_new.items():
            clean_key = clean_path(k)
            changes[clean_key] = [None, v]
        return changes

    diff = DeepDiff(old_data, new_data, ignore_order=True, verbose_level=2)

    for path in diff.get('dictionary_item_added', []):
        value = new_data
        keys = path.strip("root['").rstrip("']").split("']['")
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key, {})
        clean_key = clean_path(path)
        changes[clean_key] = [None, value]

    for path, change in diff.get('values_changed', {}).items():
        clean_key = clean_path(path)
        changes[clean_key] = [change.get('old_value'), change.get('new_value')]

    for path in diff.get('dictionary_item_removed', []):
        value = old_data
        keys = path.strip("root['").rstrip("']").split("']['")
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key, {})
        clean_key = clean_path(path)
        changes[clean_key] = [value, None]

    for cat in ['iterable_item_added', 'iterable_item_removed', 'type_changes']:
        for path, val in diff.get(cat, {}).items():
            old = val.get('old_value') if isinstance(val, dict) else None
            new = val.get('new_value') if isinstance(val, dict) else val
            clean_key = clean_path(path)
            changes[clean_key] = [old, new]

    return changes

def generate_summary(changes: Dict[str, list]) -> str:
    if not changes:
        return "No changes detected."
    parts = []
    for key, (old, new) in changes.items():
        field = key  # already cleaned
        if old is None:
            parts.append(f"{field} set to {new}")
        elif new is None:
            parts.append(f"{field} removed (was {old})")
        else:
            parts.append(f"{field} changed from {old} to {new}")
    text = " and ".join(parts).capitalize()
    return text if text.endswith(".") else text + "."


verb_map = {
    "create": "created", "created": "created", "add": "created",
    "update": "updated", "updated": "updated", "edit": "updated", "change": "updated",
    "delete": "deleted", "deleted": "deleted", "remove": "deleted",
}
