
from typing import Literal
from pydantic import BaseModel, Field


class TokenResponse(BaseModel):
    access_token: str = Field(
        description="Token JWT de acesso à API"
    )
    token_type: Literal["bearer"] = "bearer"
