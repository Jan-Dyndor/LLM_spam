from pydantic import BaseModel, Field
from typing import Literal


class InputText(BaseModel):
    text: str = Field(min_length=1, max_length=500)


class LLM_Response(BaseModel):
    label: Literal["spam", "ham"]
    confidence: float = Field(ge=0, le=1)
    reason: str = Field(min_length=1)
