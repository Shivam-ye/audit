from rest_framework import viewsets, status
from rest_framework.response import Response
from .interactors.activity_interactor import ActivityInteractor

class ActivityStreamViewSet(viewsets.ViewSet):
    """
    Handles activity stream POST requests (create audit events).
    Can be extended with GET/list methods later.
    """

    def create(self, request):
        # Ensure payload is a list
        items = request.data if isinstance(request.data, list) else [request.data]

        # Delegate processing to interactor
        result = ActivityInteractor.process_payloads(items)

        # Check for validation errors returned by the interactor
        if result and "error" in result[0]:
            return Response(result[0], status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        return Response(result, status=status.HTTP_201_CREATED)
