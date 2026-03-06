from unittest.mock import patch

from sqlalchemy import select

from app.db.db_models import Predictions, User
from app.exceptions.exceptions import LLMInvalidJSONError, LLMInvalidValidationError

# NO AUTH TEST - assume OK authorization with JWT
# NO CACHE TESTS


def test_health_happy(client, health_happy_path):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == health_happy_path


@patch("app.routers.v1.verify_access_token")
@patch("app.routers.v1.classify_spam")
def test_ask_llm_happy_no_auth(
    mock_llm,
    mock_verify_token,
    user_input,
    Model_Response_Happy_JSON_Validated,
    Model_Response_Happy_REDIS,
    redis_fixture,
    client,
    session_fixture,
):
    # Add User to DB
    new_user = User(
        id=1, username="test_user", email="test@email.com", password_hash="test"
    )
    session_fixture.add(new_user)
    session_fixture.commit()
    session_fixture.refresh(new_user)

    mock_verify_token.return_value = "1"
    mock_llm.return_value = Model_Response_Happy_JSON_Validated
    redis_fixture.get.return_value = None

    response = client.post("/v1/classify", json={"text": user_input})
    assert response.status_code == 200
    assert response.json()["label"] == "spam"
    assert response.json()["confidence"] == 0.95
    assert (
        response.json()["reason"]
        == "Contains unsolicited promotion for Viagra, a common spam topic."
    )

    redis_fixture.setex.assert_awaited_once_with(
        user_input, 300, Model_Response_Happy_REDIS
    )
    endpoint_db_result_object = session_fixture.execute(
        select(Predictions).where(Predictions.user_id == 1)
    )
    all_data_obj = session_fixture.execute(select(Predictions))
    all_data = all_data_obj.scalars().all()
    endpoint_bd_result = endpoint_db_result_object.scalars().first()
    assert endpoint_bd_result is not None
    assert endpoint_bd_result.confidence == 0.95
    assert len(all_data) == 1


def test_ask_llm_wrong_user_input(
    user_input_wrong_empty, redis_fixture, client, session_fixture
):
    response = client.post("/v1/classify", json={"text": user_input_wrong_empty})

    redis_fixture.get.assert_not_awaited()
    data_obj = session_fixture.execute(select(Predictions))
    data = data_obj.scalars().all()

    assert response.status_code == 422
    assert data == []


def test_ask_llm_wrong_user_input_int(
    user_input_wrong_int, redis_fixture, client, session_fixture
):
    response = client.post("/v1/classify", json={"text": user_input_wrong_int})

    redis_fixture.get.assert_not_awaited()
    data_obj = session_fixture.execute(select(Predictions))
    data = data_obj.scalars().all()
    assert data == []
    assert response.status_code == 422


def test_ask_llm_wrong_user_input_too_long(
    user_input_wrong_too_long, redis_fixture, client, session_fixture
):
    response = client.post("/v1/classify", json={"text": user_input_wrong_too_long})
    redis_fixture.get.assert_not_awaited()
    data_obj = session_fixture.execute(select(Predictions))
    data = data_obj.scalars().all()
    assert response.status_code == 422

    assert data == []


@patch("app.routers.v1.verify_access_token")
@patch("app.routers.v1.classify_spam")
def test_ask_llm_wrong_llm_response_json(
    mock_llm, mock_verify_token, user_input, redis_fixture, client, session_fixture
):

    mock_verify_token.return_value = "1"
    mock_llm.side_effect = LLMInvalidJSONError()
    redis_fixture.get.return_value = None

    response = client.post("/v1/classify", json={"text": user_input})

    redis_fixture.setex.assert_not_awaited()
    data_obj = session_fixture.execute(select(Predictions))
    data = data_obj.scalars().all()

    assert response.status_code == 502
    assert response.json()["message"] == "LLM returned invalid JSON"
    assert data == []


@patch("app.routers.v1.verify_access_token")
@patch("app.routers.v1.classify_spam")
def test_ask_llm_wrong_llm_response_walidation(
    mock_llm, mock_verify_token, user_input, redis_fixture, client, session_fixture
):
    mock_verify_token.return_value = "1"
    mock_llm.side_effect = LLMInvalidValidationError()
    redis_fixture.get.return_value = None

    response = client.post("/v1/classify", json={"text": user_input})
    data_obj = session_fixture.execute(select(Predictions))
    data = data_obj.scalars().all()

    redis_fixture.setex.assert_not_awaited()
    assert response.status_code == 502
    assert response.json()["message"] == "LLM returned invalid Pydantic Model"
    assert data == []


# # CACHE HIT TESTS
@patch("app.routers.v1.verify_access_token")
@patch("app.routers.v1.classify_spam")
def test_ask_llm_cache_hit(
    mock_llm,
    mock_verify_token,
    user_input,
    redis_fixture,
    Model_Response_Happy_REDIS_Response,
    client,
    session_fixture,
):
    mock_verify_token.return_value = "1"
    redis_fixture.get.return_value = Model_Response_Happy_REDIS_Response

    response = client.post("/v1/classify", json={"text": user_input})

    data_obj = session_fixture.execute(select(Predictions))
    data = data_obj.scalars().all()

    assert response.status_code == 200
    assert response.json()["label"] == "spam"
    assert response.json()["confidence"] == 0.95
    assert (
        response.json()["reason"]
        == "Contains unsolicited promotion for Viagra, a common spam topic."
    )

    mock_llm.assert_not_called()  # classify_spam function not called
    redis_fixture.assert_not_awaited()

    assert data == []
