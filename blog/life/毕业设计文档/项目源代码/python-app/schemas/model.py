from pydantic import BaseModel
from typing import Literal

class ModelGenerateRequest(BaseModel):
    layoutId: int
    responseMode: Literal["url", "inline"] = "url"
