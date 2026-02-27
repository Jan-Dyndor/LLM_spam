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
from app.db.db_models import User, Predictions

router = APIRouter(prefix="/v1", tags=["v1"])


def get_reddis(request: Request) -> Redis:
    return request.app.state.redis


# Temporary fix - passing user_id in request body.
# Right now if user is in databese - so ealier created account and now his/her ID we assoscaite it with inforamtion in predictions table
# And allow user to save its question about spam to LLM
# If user is not in db his/her ask will not be saved


# Later we will do JWT authentication adn get rid of query_param user_id!! TODO
@router.post("/classify", response_model=LLM_Response)
async def ask_llm(
    user_id: int,
    input: InputText,
    redis: Redis = Depends(get_reddis),
    db: Session = Depends(get_db),
):

    value = await redis.get(input.text)  # string
    if value is not None:
        logger.info("CACHE HIT")
        value = LLM_Response.model_validate_json(value)
    else:
        value = classify_spam(input.text)
        model_output_json = value.model_dump_json()
        await redis.setex(input.text, 300, model_output_json)
        # value = LLM_Response.model_validate_json(model_output_json)
        # return value

    # model_output_validated = LLM_Response.model_validate_json(value)
    result_user_id = db.execute(select(User).where(User.id == user_id))
    user = result_user_id.scalars().first()
    logger.warning("Linia 54")
    if user:
        logger.warning("MAM USERA")
        new_prediction = Predictions(
            user_id=user_id,
            model_name="TEST",
            input_text=input.text,
            label=value.label,
            confidence=value.confidence,
            reason=value.reason,
            prompt_version="v1",
        )
        db.add(new_prediction)
        db.commit()
        db.refresh(new_prediction)

    return value


@router.post("/users", response_model=UserResponse)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):

    result_username = db.execute(select(User).where(User.username == user.username))

    existing_user = result_username.scalars().first()
    if existing_user:
        raise HTTPException(status_code=404, detail="Username already exists")

    result_email = db.execute(select(User).where(User.email == user.email))

    existing_email = result_email.scalars().first()
    if existing_email:
        raise HTTPException(status_code=404, detail="Email already exist")

    new_user = User(username=user.username, email=user.email)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user
