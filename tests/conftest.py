import json
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock

import jwt
import pytest
from fastapi.testclient import TestClient
from pydantic import BaseModel, SecretStr
from pydantic_settings import BaseSettings
from sqlalchemy import StaticPool, create_engine
from sqlalchemy.orm import sessionmaker

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
def session_fixture():
    engine = create_engine(
        url="sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )

    Base.metadata.create_all(bind=engine)

    session_test_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    SessionLocalTest = session_test_factory()
    with SessionLocalTest as sesion_test:
        yield sesion_test


@pytest.fixture()
def client(session_fixture, redis_fixture, settings_fixture):
    def get_session_override():
        return session_fixture

    def redis_override():
        return redis_fixture

    def settigns_override():
        return settings_fixture

    app.dependency_overrides[get_db] = get_session_override
    app.dependency_overrides[get_reddis] = redis_override
    app.dependency_overrides[get_settings] = settigns_override

    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()
