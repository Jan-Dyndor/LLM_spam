import json
from app.main import app
import pytest
from unittest.mock import AsyncMock
from app.schemas.pydantic_schemas import LLM_Response
from app.routers.v1 import get_reddis


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


# Fixtures to test Redis
@pytest.fixture
def override_redis():
    fake_redis = AsyncMock()
    app.dependency_overrides[get_reddis] = lambda: fake_redis
    yield fake_redis
    app.dependency_overrides.clear()


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
