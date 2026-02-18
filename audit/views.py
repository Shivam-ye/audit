from rest_framework import viewsets, status
from rest_framework.response import Response
from .interactors.activity_interactor import ActivityInteractor


class ActivityStreamViewSet(viewsets.ViewSet):
    """
    Handles activity stream POST requests (create audit events).
    Supports both new wrapped format and legacy format.
    
    New format:
    {
        "id": "uuid",
        "type": "audit_logs",
        "payload": { /* existing payload */ }
    }
    
    Legacy format:
    {
        "verb": "create",
        "actor": {...},
        "object": {...}
    }
    """

    def create(self, request):
        data = request.data
        
        # Check for new wrapped format
        if isinstance(data, dict) and data.get("type") == "audit_logs" and "payload" in data:
            # New wrapped format
            original_payload = data
            payloads = data.get("payload", {})
            # Ensure payloads is a list
            items = [payloads] if isinstance(payloads, dict) else payloads
        else:
            # Legacy format
            original_payload = None
            # Ensure payload is a list
            items = data if isinstance(data, list) else [data]

        # Delegate processing to interactor
        result = ActivityInteractor.process_payloads(items, original_payload=original_payload)

        # Check for validation errors returned by the interactor
        if result and "error" in result[0]:
            return Response(result[0], status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        return Response(result, status=status.HTTP_201_CREATED)
