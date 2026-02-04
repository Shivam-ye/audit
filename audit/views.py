import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def compare_json(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST method required"}, status=400)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    old = data.get("old", {})
    new = data.get("new", {})

    added = {}
    removed = {}
    changed = {}

    for key in new:
        if key not in old:
            added[key] = new[key]
        elif old[key] != new[key]:
            changed[key] = {
                "old": old[key],
                "new": new[key]
            }

    for key in old:
        if key not in new:
            removed[key] = old[key]

    return JsonResponse({
        "added": added,
        "removed": removed,
        "changed": changed
    })
