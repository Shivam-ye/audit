from pydantic import BaseModel, Field, AliasChoices, field_validator
from .actor import Actor
from .resource import ResourceRef
from typing import Dict, Any, Optional


# Schema for the new wrapped payload format
class AuditLogsPayload(BaseModel):
    """Schema for wrapped audit_logs payload format"""
    id: str = Field(..., description="UUID for the audit log entry")
    type: str = Field(default="audit_logs", description="Type identifier")
    payload: Dict[str, Any] = Field(default_factory=dict, description="The actual audit payload")
    
    model_config = {
        "populate_by_name": True,
        "extra": "allow"
    }


# Schema for activity events with a nested 'object' field (e.g., XAPI-style)
class ActivityWithObject(BaseModel):
    verb: str = Field(default="updated")
    actor: Actor
    object: ResourceRef
    data: Dict[str, Any] = Field(default_factory=dict, alias=AliasChoices("data", "fields", "payload"))
    model_config = {
        "populate_by_name": True,
        "extra": "allow"
    }

# Schema for activity events with a nested 'resource' field (custom format)
class ActivityWithResource(BaseModel):
    verb: str = Field(default="updated")
    actor: Actor
    resource: ResourceRef
    data: Dict[str, Any] = Field(default_factory=dict, alias=AliasChoices("data", "fields", "payload"))
    model_config = {
        "populate_by_name": True,
        "extra": "allow"
    }

# Schema for flattened/normalized activity events with all fields at top level
class FlatActivity(BaseModel):
    verb: str = Field(default="updated")
    actor: Optional[Actor] = None
    actor_id: Optional[str] = None
    
    # Improved aliases for type 
    type: Optional[str] = Field(
        None,
        alias=AliasChoices("type", "resource_type", "object_type", "object.type")
    )
    
    # Improved aliases for id
    id: Optional[str] = Field(
        None,
        alias=AliasChoices("id", "resource_id", "object.id")
    )
    
    # Allow capturing the whole nested object
    object: Optional[Dict[str, Any]] = None

    model_config = {
        "populate_by_name": True,
        "extra": "allow"
    }

    # Converts actor from string ID to Actor dict, or passes through existing dict
    @field_validator('actor', mode='before')
    @classmethod
    def normalize_actor(cls, v):
        if isinstance(v, dict) and 'id' in v:
            return v
        if isinstance(v, str):
            return {'id': v}
        return None
