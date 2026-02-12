from pydantic import BaseModel, Field, AliasChoices, field_validator
from .actor import Actor
from .resource import ResourceRef
from typing import Dict, Any, Optional

class ActivityWithObject(BaseModel):
    verb: str = Field(default="updated")
    actor: Actor
    object: ResourceRef
    data: Dict[str, Any] = Field(default_factory=dict, alias=AliasChoices("data", "fields", "payload"))
    model_config = {
        "populate_by_name": True,
        "extra": "allow"
    }

class ActivityWithResource(BaseModel):
    verb: str = Field(default="updated")
    actor: Actor
    resource: ResourceRef
    data: Dict[str, Any] = Field(default_factory=dict, alias=AliasChoices("data", "fields", "payload"))
    model_config = {
        "populate_by_name": True,
        "extra": "allow"
    }

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

    @field_validator('actor', mode='before')
    @classmethod
    def normalize_actor(cls, v):
        if isinstance(v, dict) and 'id' in v:
            return v
        if isinstance(v, str):
            return {'id': v}
        return None