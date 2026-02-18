from tools_box.utils.base_classes.pydantic import BasePydanticModel
from pydantic import Field

class Actor(BasePydanticModel):
    id: str = Field(..., min_length=1)

    model_config = {"extra": "allow"}
