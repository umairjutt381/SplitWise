from typing import Any

from pydantic import BaseModel


class APIResponseSchema(BaseModel):
    success: bool
    message: str
    code: int
    data: Any
