from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from redis.asyncio import Redis
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.authentication.auth import (
    create_access_token,
    hash_password,
    oauth2_scheme,
    verify_access_token,
    verify_password,
)
from app.config.settings import Settings, get_settings
from app.db.database import get_db
from app.db.db_models import Predictions, User
from app.logging.logg import logger
from app.schemas.pydantic_schemas import (
    InputText,
    LLM_Response,
    PredictionsResponse,
    Token,
    UserCreate,
    UserResponse,
)
from app.services.spam_classification import classify_spam

router = APIRouter(prefix="/v1", tags=["v1"])


def get_reddis(request: Request) -> Redis:
    return request.app.state.redis


@router.post("/classify", response_model=LLM_Response)
async def ask_llm(
    input: InputText,
    redis: Redis = Depends(get_reddis),
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme),
    settings: Settings = Depends(get_settings),
):
    user_id = verify_access_token(token, settings)

    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_id_int = int(user_id)
    except TypeError, ValueError:
        logger.exception(f"Issue while converting user_id {user_id} to int")
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    value = await redis.get(input.text)
    if value is not None:
        logger.info("CACHE HIT")
        value = LLM_Response.model_validate_json(value)
    else:
        value = await classify_spam(input.text)
        model_output_json = value.model_dump_json()
        await redis.setex(input.text, 300, model_output_json)

    if user_id:
        logger.info("Attempt to save user query to DB")
        result_user_id = await db.execute(select(User).where(User.id == user_id))
        user = result_user_id.scalars().first()
        if user:
            new_prediction = Predictions(
                user_id=user_id,
                model_name=settings.ai_model.model_name,
                input_text=input.text,
                label=value.label,
                confidence=value.confidence,
                reason=value.reason,
                prompt_version=settings.ai_model.promp_version,
            )
            db.add(new_prediction)
            await db.commit()
            await db.refresh(new_prediction)
            logger.info(f"Saved user {user_id_int} query to DB")
    else:
        logger.info(f"No user {user_id_int} in DB - prediction did not save")

    return value


@router.post("/create_user", response_model=UserResponse)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):

    result_username = await db.execute(
        select(User).where(func.lower(User.username) == user.username.lower())
    )
    result_email = await db.execute(
        select(User).where(func.lower(User.email) == user.email.lower())
    )
    existing_user = result_username.scalars().first()
    existing_email = result_email.scalars().first()

    if existing_user or existing_email:
        raise HTTPException(status_code=409, detail="Email or User Name already exist")

    new_user = User(
        username=user.username,
        email=user.email.lower(),
        password_hash=hash_password(user.password),  # hash user password
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data=Depends(OAuth2PasswordRequestForm),
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    """Return Token to user"""
    result = await db.execute(
        select(User).where(func.lower(User.username) == form_data.username.lower())
    )
    user = result.scalars().first()

    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=401,
            detail="Incorect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expire = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expire, settings=settings
    )
    return Token(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
    settings=Depends(get_settings),
):
    """Get current authenticated user"""
    user_id = verify_access_token(token, settings)

    if user_id is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_id_int = int(user_id)
    except (TypeError, ValueError) as err:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from err

    result = await db.execute(select(User).where(User.id == user_id_int))
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


@router.get("/users/me/predictions", response_model=list[PredictionsResponse])
async def show_user_predictions(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme),
    settings: Settings = Depends(get_settings),
):
    user_id = verify_access_token(token, settings)
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_id_int = int(user_id)
    except (TypeError, ValueError) as err:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from err

    result_user = await db.execute(
        select(User).options(selectinload(User.spam)).where(User.id == user_id_int)
    )

    existing_user = result_user.scalars().first()  # user or None

    if not existing_user:
        logger.warning(f"No user with ID {user_id_int} found in DB")
        raise HTTPException(
            status_code=404, detail=f"No user with ID {user_id} found in DB"
        )

    predictions = existing_user.spam
    return predictions
