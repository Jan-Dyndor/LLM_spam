import pytest

from app.authentication.auth import hash_password
from app.db.db_models import User


@pytest.mark.anyio
async def test_token_happy(client, session_fixture, test_useer_request_form_valid):

    new_user = User(
        username="test_username".lower(),
        email="test_user@email.com".lower(),
        password_hash=hash_password("test_password"),
    )

    session_fixture.add(new_user)
    await session_fixture.flush()
    await session_fixture.refresh(new_user)

    response = await client.post("v1/token", data=test_useer_request_form_valid)

    assert response.status_code == 200
    assert response.json()["access_token"] is not None
    assert response.json()["token_type"] == "bearer"
    assert len(response.json()) == 2


@pytest.mark.anyio
async def test_no_user_in_db(client, test_useer_request_form_valid):

    response = await client.post("v1/token", data=test_useer_request_form_valid)

    assert response.status_code == 401
    assert response.json()["detail"] == "Incorect email or password"


@pytest.mark.anyio
async def test_user_wrong_password(
    client, session_fixture, test_useer_request_form_valid
):
    new_user = User(
        username="test_username".lower(),
        email="test_user@email.com".lower(),
        password_hash=hash_password("!!!__WRONG_PASSWORD__!!"),
    )

    session_fixture.add(new_user)
    await session_fixture.flush()
    await session_fixture.refresh(new_user)

    response = await client.post("v1/token", data=test_useer_request_form_valid)

    assert response.status_code == 401
