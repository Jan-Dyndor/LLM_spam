from unittest.mock import patch

from fastapi.testclient import TestClient
from app.exceptions.exceptions import LLMInvalidJSONError, LLMInvalidValidationError
from app.main import app


client = TestClient(app)


def test_health_happy(health_happy_path):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == health_happy_path


@patch("app.routers.v1.classify_spam")
def test_user_input_happy_mocekd_inside_function(
    mock_llm, user_input, Model_Response_Happy_JSON_Validated
):
    mock_llm.return_value = Model_Response_Happy_JSON_Validated

    response = client.post("/v1/classify", json={"text": user_input})
    assert response.status_code == 200
    assert response.json()["label"] == "spam"
    assert response.json()["confidence"] == 0.95
    assert (
        response.json()["reason"]
        == "Contains unsolicited promotion for Viagra, a common spam topic."
    )


@patch("app.routers.v1.classify_spam")
def test_ask_llm_wrong_llm_response_json(mock_llm, user_input):
    mock_llm.side_effect = LLMInvalidJSONError()
    response = client.post("/v1/classify", json={"text": user_input})
    assert response.status_code == 502
    assert response.json()["message"] == "LLM returned invalid JSON"


@patch("app.routers.v1.classify_spam")
def test_ask_llm_wrong_llm_response_walidation(mock_llm, user_input):
    mock_llm.side_effect = LLMInvalidValidationError()
    response = client.post("/v1/classify", json={"text": user_input})
    assert response.status_code == 502
    assert response.json()["message"] == "LLM returned invalid Pydantic Model"
