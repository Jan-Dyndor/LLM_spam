from fastapi import APIRouter

from app.schemas.pydantic_schemas import InputText, LLM_Response
from app.services.spam_classification import classify_spam

router = APIRouter(prefix="/v1", tags=["v1"])


@router.post("/classify", response_model=LLM_Response)
async def ask_llm(input: InputText):
    return classify_spam(input.text)
