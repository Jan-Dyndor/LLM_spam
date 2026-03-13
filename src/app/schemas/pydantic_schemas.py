from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Literal
from datetime import datetime


class InputText(BaseModel):
    text: str = Field(min_length=1, max_length=500)


class LLM_Response(BaseModel):
    label: Literal["spam", "ham"]
    confidence: float = Field(ge=0, le=1)
    reason: str = Field(min_length=1)


class UserBase(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    email: EmailStr = Field(min_length=1, max_length=100)


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=50)


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str


class PredictionsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    model_name: str
    input_text: str
    label: str
    confidence: float
    reason: str
    prompt_version: str
    is_spam: int | None = None
    date: datetime


# JWT
class Token(BaseModel):
    access_token: str
    token_type: str


# Model metrics
class CurrentModelMetrics(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    accuracy: float
    f1: float
    recall: float
    precision: float
    date: datetime


class PreviousModelMetrics(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    previous_metrics: list[CurrentModelMetrics]


class ModelMetricsALL(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    current_metris: CurrentModelMetrics
    previous_metrics: PreviousModelMetrics


class ModelResponseGolden(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    model_label: str
    confidence: float
    reason: str
    true_label: str


class ModelResponseGoldenALL(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    all_resp: list[ModelResponseGolden]


class Final(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    metrics: ModelMetricsALL
    responses: ModelResponseGoldenALL
