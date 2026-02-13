from pydantic import ValidationError
from ..schemas import FlatActivity, ActivityWithObject, ActivityWithResource

class PayloadValidator:

    @staticmethod
    def validate(payload: dict):
        """Return validated object and its type ('object', 'resource', or 'flat')"""
        if "object" in payload and isinstance(payload["object"], dict) and "type" in payload["object"]:
            return ActivityWithObject.model_validate(payload), "object"
        elif "resource" in payload and isinstance(payload["resource"], dict) and "type" in payload["resource"]:
            return ActivityWithResource.model_validate(payload), "resource"
        else:
            return FlatActivity.model_validate(payload), "flat"

