from fastapi import APIRouter, Depends, Request
from redis.asyncio import Redis

from app.logging.logg import logger
from app.schemas.pydantic_schemas import InputText, LLM_Response
from app.services.spam_classification import classify_spam


router = APIRouter(prefix="/v1", tags=["v1"])


def get_reddis(request: Request) -> Redis:
    return request.app.state.redis


@router.post("/classify", response_model=LLM_Response)
async def ask_llm(input: InputText, redis: Redis = Depends(get_reddis)):

    value = await redis.get(input.text)
    if value is not None:
        logger.info("CACHE HIT")
    else:
        model_output = classify_spam(input.text)
        model_output_json = model_output.model_dump_json()
        await redis.setex(input.text, 300, model_output_json)
        return model_output

    return LLM_Response.model_validate_json(value)
