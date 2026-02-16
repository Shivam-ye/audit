from ..services.resource_service import ResourceService


class ResourceExtractor:
    """Thin wrapper - delegates to ResourceService"""

    @staticmethod
    def extract(payload, validated, payload_type):
        """Delegate to ResourceService"""
        return ResourceService.extract_resource(payload, validated, payload_type)
