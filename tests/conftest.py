import json
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock

import jwt
import pandas as pd
import pytest
from httpx import ASGITransport, AsyncClient
from pydantic import BaseModel, SecretStr
from pydantic_settings import BaseSettings
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config.settings import get_settings
from app.db.database import get_db
from app.db.db_models import Base
from app.main import app
from app.routers.v1 import get_reddis
from app.schemas.pydantic_schemas import LLM_Response


@pytest.fixture
def health_happy_path() -> dict:
    return {"Status": "OK"}


@pytest.fixture
def user_input() -> str:
    return "get the most out of life ! viagra has helped millions of men !\nfor a good cause , wrongdoing is virtuous .\ni don ' t want to be anyone but the person i am .\nthe athlete makes himself , the coach doesn ' t make the athlete ."


@pytest.fixture
def user_input_wrong_empty() -> str:
    return ""


@pytest.fixture
def user_input_wrong_int() -> int:
    return 34


@pytest.fixture
def Model_Response_Happy() -> str:
    return """ 
    {
   "label":"spam",
   "confidence":0.95,
   "reason":"Contains unsolicited promotion for Viagra, a common spam topic."
    }
    """


@pytest.fixture
def Model_Response_Happy_JSON_Validated() -> LLM_Response:
    output_string = """ 
    {
   "label":"spam",
   "confidence":0.95,
   "reason":"Contains unsolicited promotion for Viagra, a common spam topic."
    }
    """

    output_string_json = json.loads(output_string)
    return LLM_Response.model_validate(output_string_json)


@pytest.fixture
def Model_Response_Not_Json() -> str:
    return """ 
    {
   label:spam,
   confidence:0.95,
   reason:Contains unsolicited promotion for Viagra, a common spam topic."
    }
    """


@pytest.fixture
def Model_Response_Wrong_Validation_Label() -> str:
    return """ 
    {
   "label":"wrong label",
   "confidence":0.95,
   "reason":"Contains unsolicited promotion for Viagra, a common spam topic."
    }
    """


@pytest.fixture
def Model_Response_Wrong_Validation_Confidence_1() -> str:
    return """ 
    {
   "label":"spam",
   "confidence":"wrong label",
   "reason":"Contains unsolicited promotion for Viagra, a common spam topic."
    }
    """


@pytest.fixture
def Model_Response_Wrong_Validation_Confidence_2() -> str:
    return """ 
    {
   "label":"spam",
   "confidence": -99,
   "reason":"Contains unsolicited promotion for Viagra, a common spam topic."
    }
    """


@pytest.fixture
def Model_Response_Wrong_Validation_Reason() -> str:
    return """ 
    {
   "label":"spam",
   "confidence": -99,
   "reason":""
    }
    """


@pytest.fixture
def user_input_wrong_too_long() -> str:
    return "A" * 501


@pytest.fixture
def Model_Response_Happy_REDIS() -> str:
    output_string = """ 
    {
   "label":"spam",
   "confidence":0.95,
   "reason":"Contains unsolicited promotion for Viagra, a common spam topic."
    }
    """

    output_string_json = json.loads(output_string)
    model_validated = LLM_Response.model_validate(output_string_json)
    return model_validated.model_dump_json()


@pytest.fixture
def Model_Response_Happy_REDIS_Response() -> bytes:
    output_string = """ 
    {
   "label":"spam",
   "confidence":0.95,
   "reason":"Contains unsolicited promotion for Viagra, a common spam topic."
    }
    """
    output_string_json = json.loads(output_string)
    model_validated = LLM_Response.model_validate(output_string_json)
    model_val_str = model_validated.model_dump_json()
    return model_val_str.encode()


@pytest.fixture()
def test_user_valid():

    return {
        "username": "test_username",
        "email": "test_user@email.com",
        "password": "test_password_12345678",
    }


@pytest.fixture()
def test_user_invalid():

    return {
        "username": "test_username",
        "email": "test_user@email.com",
        "password": "",
    }


@pytest.fixture
def test_useer_request_form_valid():

    return {
        "username": "test_username",
        "password": "test_password",
    }


# APP DEPENDS fixtures


@pytest.fixture
def redis_fixture():
    return AsyncMock()


@pytest.fixture
def settings_fixture():
    class AI_Model(BaseModel):
        model_name: str = "test_model"
        temperature: float = -99
        promp_version: str = "test_prompt"

    class Settings(BaseSettings):
        secret_key: SecretStr = "test_keys" * 5  # type: ignore x5 so I want get InsecureKeyLengthWarning
        # key should be long enought
        algorythm: str = "HS256"
        access_token_expire_minutes: int = 2
        ai_model: AI_Model = AI_Model()

    return Settings()


@pytest.fixture()
def valid_token_fixture(settings_fixture):
    settings = settings_fixture
    payload = {"sub": "1", "exp": datetime.now(UTC) + timedelta(minutes=5)}
    return jwt.encode(
        payload, settings.secret_key.get_secret_value(), settings.algorythm
    )


@pytest.fixture
def invalid_token_int(settings_fixture):
    settings = settings_fixture
    payload = {"sub": "INVALID_INT", "exp": datetime.now(UTC) + timedelta(minutes=5)}

    return jwt.encode(
        payload, settings.secret_key.get_secret_value(), settings.algorythm
    )


@pytest.fixture()
def invalid_token_fixture():
    return "invalid_token"


@pytest.fixture()
def expired_token_fixture(settings_fixture):
    settings = settings_fixture
    payload = {"sub": "1", "exp": 0}
    return jwt.encode(
        payload, settings.secret_key.get_secret_value(), settings.algorythm
    )


@pytest.fixture()
async def session_fixture():
    engine = create_async_engine(
        url="sqlite+aiosqlite://", connect_args={"check_same_thread": False}
    )

    AsyncSessionLocalTest = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocalTest() as session_test:
        yield session_test

    await engine.dispose()


@pytest.fixture()
async def client(session_fixture, redis_fixture, settings_fixture):
    def get_session_override():
        yield session_fixture

    def redis_override():
        return redis_fixture

    def settigns_override():
        return settings_fixture

    app.dependency_overrides[get_db] = get_session_override
    app.dependency_overrides[get_reddis] = redis_override
    app.dependency_overrides[get_settings] = settigns_override

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client

    app.dependency_overrides.clear()


# =============
# Test model eval function
# =============
@pytest.fixture
def model_responses_goloden_data_test():

    example_response_1 = LLM_Response(
        label="spam", confidence=0.56, reason="Test response 1"
    )

    example_response_2 = LLM_Response(
        label="spam", confidence=1, reason="Test response 2"
    )
    return [example_response_1, example_response_2]


@pytest.fixture
def model_input_golden_data_test():
    test_data_json = [
        {
            "text": "You have been selected for an exclusive investment opportunity. Act fast.",
            "label": "spam",
        },
        {
            "text": "Reminder: your dentist appointment is scheduled for Monday at 15:30.",
            "label": "ham",
        },
    ]
    return pd.DataFrame(test_data_json)


@pytest.fixture
def correct_df_to_calc_metrics(
    model_input_golden_data_test, model_responses_goloden_data_test
):

    model_responses = [
        response.model_dump() for response in model_responses_goloden_data_test
    ]

    df = pd.DataFrame.from_records(model_responses)
    df = df.rename(columns={"label": "model_label"})
    df["true_label"] = model_input_golden_data_test["label"]
    df["text"] = model_input_golden_data_test["text"]
    return df
