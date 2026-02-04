from rest_framework.decorators import api_view
from rest_framework.response import Response
from datetime import datetime

# ---------------------------
# In-memory store (GLOBAL)
# ---------------------------
STORE = {}


# ---------------------------
# Diff logic (CORE)
# ---------------------------
def diff_json(old, new):
    changes = {}
    all_keys = set(old.keys()).union(set(new.keys()))

    for key in all_keys:
        old_val = old.get(key)
        new_val = new.get(key)

        if old_val != new_val:
            changes[key] = {
                "from": old_val,
                "to": new_val
            }

    return changes


# ---------------------------
# POST /audit/update
# ---------------------------
@api_view(["POST"])
def update_audit(request):
    service = request.data.get("service")
    user_id = request.data.get("userId")
    new_data = request.data.get("data")

    # basic validation
    if not service or not user_id or not isinstance(new_data, dict):
        return Response(
            {"error": "Invalid input"},
            status=400
        )

    # init service store
    if service not in STORE:
        STORE[service] = {
            "current": {},
            "history": [],
            "version": 0
        }

    service_store = STORE[service]
    previous_data = service_store["current"]

    # calculate diff
    changes = diff_json(previous_data, new_data)

    # increment version
    service_store["version"] += 1

    # save history
    service_store["history"].append({
        "version": service_store["version"],
        "userId": user_id,
        "changedAt": datetime.utcnow().isoformat(),
        "changes": changes
    })

    # update current snapshot (FULL JSON)
    service_store["current"] = new_data

    return Response({
        "service": service,
        "currentState": new_data
    })


# ---------------------------
# GET /audit/history/<service>
# ---------------------------
@api_view(["GET"])
def get_history(request, service):
    if service not in STORE:
        return Response({
            "service": service,
            "history": []
        })

    return Response({
        "service": service,
        "history": STORE[service]["history"]
    })
