from pydantic import ValidationError
from ..schemas import FlatActivity, ActivityWithObject, ActivityWithResource


class ValidationService:
    """Service for validating payloads - business logic moved from PayloadValidator"""

    @staticmethod
    def validate(payload):
        """
        Return validated object and its type ('object', 'resource', or 'flat')
        Ensures payload is a dict first.
        """
        print("FULL PAYLOAD:", payload)
        if not isinstance(payload, dict):
            raise ValueError(f"Invalid payload, expected dict but got {type(payload).__name__}: {payload}")

        if "object" in payload and isinstance(payload["object"], dict) and "type" in payload["object"]:
            return ActivityWithObject.model_validate(payload), "object"
        elif "resource" in payload and isinstance(payload["resource"], dict) and "type" in payload["resource"]:
            return ActivityWithResource.model_validate(payload), "resource"
        else:
            return FlatActivity.model_validate(payload), "flat"

