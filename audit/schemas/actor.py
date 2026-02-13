from pydantic import BaseModel, Field

class Actor(BaseModel):
    id: str = Field(..., min_length=1)

    model_config = {"extra": "allow"}