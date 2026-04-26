from pydantic import BaseModel
from typing import Any, Literal, Optional


class JobCreateRequest(BaseModel):
    type: Literal["layout", "model"]
    payload: dict[str, Any]


class JobCreateResponse(BaseModel):
    jobId: str
    status: int

class JobStatusResponse(BaseModel):
    jobId: str
    status: int


class JobDetailResponse(BaseModel):
    jobId: str
    status: int
    result: Optional[dict[str, Any]] = None
