from unittest.mock import patch

import pytest
from sqlalchemy import select, text

from app.db.db_models import Predictions, User
from app.exceptions.exceptions import LLMInvalidJSONError, LLMInvalidValidationError


@pytest.mark.anyio
async def test_health_happy(client, health_happy_path):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == health_happy_path


# AUTH TETS
@pytest.mark.anyio
async def test_invalid_token(client, user_input, invalid_token_fixture):
    """Function will test invalid token value - function verify_access_token returns None"""

    headers = {"Authorization": f"Bearer {invalid_token_fixture}"}
    response = await client.post(
        "v1/classify", json={"text": user_input}, headers=headers
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or expired token"


@pytest.mark.anyio
async def test_expired_token(client, expired_token_fixture, user_input):
    """
    Function tests expire token
    """
    headers = {"Authorization": f"Bearer {expired_token_fixture}"}
    response = await client.post(
        "v1/classify", json={"text": user_input}, headers=headers
    )
    assert response.status_code == 401


# NO AUTH TEST - assume OK authorization with JWT (mocked auth)


@pytest.mark.anyio
@patch("app.routers.v1.classify_spam")
async def test_ask_llm_happy(
    mock_llm,
    user_input,
    Model_Response_Happy_JSON_Validated,
    Model_Response_Happy_REDIS,
    redis_fixture,
    client,
    session_fixture,
    token_fxture_factory,
):
    """
    Function tests the whole endpoint - Auth , DB

    Mocked is API call. and Redis cache

    """
    # Add User to DB
    new_user = User(username="test_user", email="test@email.com", password_hash="test")
    session_fixture.add(new_user)
    await session_fixture.flush()
    await session_fixture.refresh(new_user)

    token = token_fxture_factory(new_user.id)

    mock_llm.return_value = Model_Response_Happy_JSON_Validated
    redis_fixture.get.return_value = None

    headers = {"Authorization": f"Bearer {token}"}

    response = await client.post(
        "/v1/classify", json={"text": user_input}, headers=headers
    )

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
    endpoint_db_result_object = await session_fixture.execute(
        select(Predictions).where(Predictions.user_id == int(new_user.id))
    )
    all_data_obj = await session_fixture.execute(select(Predictions))
    all_data = all_data_obj.scalars().all()
    endpoint_bd_result = endpoint_db_result_object.scalars().first()
    assert endpoint_bd_result is not None
    assert endpoint_bd_result.confidence == 0.95
    assert len(all_data) == 1

    # DB Clean-up
    await session_fixture.execute(text("delete from predictions"))
    await session_fixture.commit()
    await session_fixture.execute(text("delete from users"))
    await session_fixture.commit()


@pytest.mark.anyio
async def test_ask_llm_wrong_user_input(
    user_input_wrong_empty,
    redis_fixture,
    client,
    session_fixture,
    token_fxture_factory,
):

    token = token_fxture_factory(1)
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.post(
        "/v1/classify", json={"text": user_input_wrong_empty}, headers=headers
    )

    redis_fixture.get.assert_not_awaited()
    data_obj = await session_fixture.execute(select(Predictions))
    data = data_obj.scalars().all()

    assert response.status_code == 422
    assert data == []


@pytest.mark.anyio
async def test_ask_llm_wrong_user_input_int(
    user_input_wrong_int,
    redis_fixture,
    client,
    session_fixture,
    token_fxture_factory,
):
    token = token_fxture_factory(1)
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.post(
        "/v1/classify", json={"text": user_input_wrong_int}, headers=headers
    )

    redis_fixture.get.assert_not_awaited()
    data_obj = await session_fixture.execute(select(Predictions))
    data = data_obj.scalars().all()
    assert data == []
    assert response.status_code == 422


@pytest.mark.anyio
async def test_ask_llm_wrong_user_input_too_long(
    user_input_wrong_too_long,
    redis_fixture,
    client,
    session_fixture,
    token_fxture_factory,
):
    """
    Function do not test REDIS
    Only user input.
    """
    token = token_fxture_factory(1)
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.post(
        "/v1/classify", json={"text": user_input_wrong_too_long}, headers=headers
    )
    redis_fixture.get.assert_not_awaited()
    data_obj = await session_fixture.execute(select(Predictions))
    data = data_obj.scalars().all()
    assert response.status_code == 422

    assert data == []


@pytest.mark.anyio
@patch("app.routers.v1.classify_spam")
async def test_ask_llm_wrong_llm_response_json(
    mock_llm,
    user_input,
    redis_fixture,
    client,
    session_fixture,
    token_fxture_factory,
):
    """Function tests /classify endpoint with API LLM error and no DB queries were done"""

    token = token_fxture_factory(1)  # valid token
    headers = {"Authorization": f"Bearer {token}"}
    # mock_verify_token.return_value = "1"
    mock_llm.side_effect = LLMInvalidJSONError()
    redis_fixture.get.return_value = None

    response = await client.post(
        "/v1/classify", json={"text": user_input}, headers=headers
    )

    redis_fixture.setex.assert_not_awaited()
    data_obj = await session_fixture.execute(select(Predictions))
    data = data_obj.scalars().all()

    assert response.status_code == 502
    assert response.json()["message"] == "LLM returned invalid JSON"
    assert data == []


@pytest.mark.anyio
@patch("app.routers.v1.classify_spam")
async def test_ask_llm_wrong_llm_response_walidation(
    mock_llm,
    user_input,
    redis_fixture,
    client,
    session_fixture,
    token_fxture_factory,
):
    """Function tests /classify endpoint with API LLM error and no DB queries were done"""
    token = token_fxture_factory(1)
    headers = {"Authorization": f"Bearer {token}"}

    mock_llm.side_effect = LLMInvalidValidationError()
    redis_fixture.get.return_value = None

    response = await client.post(
        "/v1/classify", json={"text": user_input}, headers=headers
    )
    data_obj = await session_fixture.execute(select(Predictions))
    data = data_obj.scalars().all()

    redis_fixture.setex.assert_not_awaited()
    assert response.status_code == 502
    assert response.json()["message"] == "LLM returned invalid Pydantic Model"
    assert data == []


# # CACHE HIT TESTS
@pytest.mark.anyio
@patch("app.routers.v1.classify_spam")
async def test_ask_llm_cache_hit(
    mock_llm,
    user_input,
    redis_fixture,
    Model_Response_Happy_REDIS_Response,
    client,
    session_fixture,
    token_fxture_factory,
):
    """Function test /classify endpoint with redis cache hit, saving output to DB assuming User id = 1 alredy in DB"""

    new_user = User(username="test_user", email="test@email.com", password_hash="test")

    session_fixture.add(new_user)
    await session_fixture.flush()
    await session_fixture.refresh(new_user)

    token = token_fxture_factory(new_user.id)
    headers = {"Authorization": f"Bearer {token}"}

    redis_fixture.get.return_value = Model_Response_Happy_REDIS_Response

    response = await client.post(
        "/v1/classify", json={"text": user_input}, headers=headers
    )

    data_obj = await session_fixture.execute(
        select(Predictions).where(Predictions.user_id == new_user.id)
    )
    data = data_obj.scalars().first()

    mock_llm.assert_not_called()  # classify_spam function not called
    redis_fixture.setex.assert_not_awaited()

    assert response.status_code == 200
    assert response.json()["label"] == "spam"
    assert response.json()["confidence"] == 0.95
    assert (
        response.json()["reason"]
        == "Contains unsolicited promotion for Viagra, a common spam topic."
    )
    assert data.model_name == "test_model"

    # DB clean-up
    await session_fixture.execute(text("delete from predictions"))
    await session_fixture.execute(text("delete from users"))
    await session_fixture.commit()


@pytest.mark.anyio
@patch("app.routers.v1.classify_spam")
async def test_ask_llm_no_user_in_db(
    mock_llm,
    user_input,
    client,
    session_fixture,
    redis_fixture,
    Model_Response_Happy_JSON_Validated,
    Model_Response_Happy_REDIS,
    token_fxture_factory,
):
    """Function tests /classify endpoint in scenerio that somehow  User who invoked endpoint is not present in DB = no saving model output"""

    token = token_fxture_factory(1)

    headers = {"Authorization": f"Bearer {token}"}
    users_obj = await session_fixture.execute(select(User))
    users = users_obj.scalars().all()
    assert users == []

    redis_fixture.get.return_value = None
    mock_llm.return_value = Model_Response_Happy_JSON_Validated

    response = await client.post(
        "/v1/classify", json={"text": user_input}, headers=headers
    )

    assert response.status_code == 200
    assert response.json()["label"] == "spam"
    redis_fixture.setex.assert_awaited_once_with(
        user_input, 300, Model_Response_Happy_REDIS
    )

    predictions_obj = await session_fixture.execute(select(Predictions))
    preds = predictions_obj.scalars().all()
    assert preds == []


@pytest.mark.anyio
async def test_ask_llm_wrong_token_int(client, invalid_token_int, user_input):

    headers = {"Authorization": f"Bearer {invalid_token_int}"}

    response = await client.post(
        "v1/classify", headers=headers, json={"text": user_input}
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or expired token"
