from pydantic import BaseModel, Field

class ResourceRef(BaseModel):
    id: str = Field(..., min_length=1)
    type: str = Field(..., min_length=1)
    model_config = {"extra": "allow"}