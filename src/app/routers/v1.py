from fastapi import APIRouter, Depends, Request, HTTPException
from redis.asyncio import Redis

from app.logging.logg import logger
from app.schemas.pydantic_schemas import (
    InputText,
    LLM_Response,
    UserCreate,
    UserResponse,
)
from app.services.spam_classification import classify_spam

from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.db_models import User

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


@router.post("/users", response_model=UserResponse)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):

    result = db.execute(select(User).where(User.username == user.username))

    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exist")

    result = db.execute(select(User).where(User.email == user.email))

    existing_email = result.scalars().first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already exist")

    new_user = User(username=user.username, email=user.email)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user
