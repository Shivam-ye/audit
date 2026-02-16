from ..services.validation_service import ValidationService


class PayloadValidator:
    """Thin wrapper - delegates to ValidationService"""

    @staticmethod
    def validate(payload):
        """Delegate to ValidationService"""
        return ValidationService.validate(payload)
