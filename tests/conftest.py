import json

import pytest

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
