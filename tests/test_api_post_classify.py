from unittest.mock import patch

from fastapi.testclient import TestClient

from app.exceptions.exceptions import LLMInvalidJSONError, LLMInvalidValidationError
from app.main import app

client = TestClient(app)


# NO CACHE TESTS


def test_health_happy(health_happy_path):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == health_happy_path


@patch("app.routers.v1.classify_spam")
def test_ask_llm_happy(
    mock_llm,
    user_input,
    Model_Response_Happy_JSON_Validated,
    Model_Response_Happy_REDIS,
    override_redis,
):
    mock_llm.return_value = Model_Response_Happy_JSON_Validated
    override_redis.get.return_value = None

    response = client.post("/v1/classify", json={"text": user_input})
    assert response.status_code == 200
    assert response.json()["label"] == "spam"
    assert response.json()["confidence"] == 0.95
    assert (
        response.json()["reason"]
        == "Contains unsolicited promotion for Viagra, a common spam topic."
    )

    override_redis.set.assert_awaited_once_with(user_input, Model_Response_Happy_REDIS)


def test_ask_llm_wrong_user_input(user_input_wrong_empty, override_redis):
    response = client.post("/v1/classify", json={"text": user_input_wrong_empty})
    assert response.status_code == 422
    override_redis.get.assert_not_awaited()


def test_ask_llm_wrong_user_input_int(user_input_wrong_int, override_redis):
    response = client.post("/v1/classify", json={"text": user_input_wrong_int})
    assert response.status_code == 422
    override_redis.get.assert_not_awaited()


def test_ask_llm_wrong_user_input_too_long(user_input_wrong_too_long, override_redis):
    response = client.post("/v1/classify", json={"text": user_input_wrong_too_long})
    assert response.status_code == 422
    override_redis.get.assert_not_awaited()


@patch("app.routers.v1.classify_spam")
def test_ask_llm_wrong_llm_response_json(mock_llm, user_input, override_redis):
    mock_llm.side_effect = LLMInvalidJSONError()
    override_redis.get.return_value = None
    response = client.post("/v1/classify", json={"text": user_input})
    assert response.status_code == 502
    assert response.json()["message"] == "LLM returned invalid JSON"
    override_redis.set.assert_not_awaited()


@patch("app.routers.v1.classify_spam")
def test_ask_llm_wrong_llm_response_walidation(mock_llm, user_input, override_redis):
    mock_llm.side_effect = LLMInvalidValidationError()
    override_redis.get.return_value = None
    response = client.post("/v1/classify", json={"text": user_input})
    assert response.status_code == 502
    assert response.json()["message"] == "LLM returned invalid Pydantic Model"
    override_redis.set.assert_not_awaited()


# CACHE HIT TESTS
@patch("app.routers.v1.classify_spam")
def test_ask_llm_cache_hit(
    mock_llm, user_input, override_redis, Model_Response_Happy_REDIS_Response
):

    override_redis.get.return_value = Model_Response_Happy_REDIS_Response
    response = client.post("/v1/classify", json={"text": user_input})
    print(response)
    assert response.status_code == 200
    assert response.json()["label"] == "spam"
    assert response.json()["confidence"] == 0.95
    assert (
        response.json()["reason"]
        == "Contains unsolicited promotion for Viagra, a common spam topic."
    )
    mock_llm.assert_not_called()  # classify_spam function not called
    override_redis.assert_not_awaited()
