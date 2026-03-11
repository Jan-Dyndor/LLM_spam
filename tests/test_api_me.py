import pytest
from sqlalchemy import select

from app.authentication.auth import hash_password
from app.db.db_models import User


@pytest.mark.anyio
async def test_me_happy(client, session_fixture, valid_token_fixture):
    new_user = User(
        username="test_username".lower(),
        email="test_user@email.com".lower(),
        password_hash=hash_password("test_password"),
    )

    session_fixture.add(new_user)
    await session_fixture.commit()
    await session_fixture.refresh(new_user)

    headers = {"Authorization": f"Bearer {valid_token_fixture}"}

    response = await client.get("v1/me", headers=headers)

    assert response.status_code == 200
    assert response.json()["id"] == 1
    assert response.json()["username"] == "test_username"


@pytest.mark.anyio
async def test_me_invalid_token(client, invalid_token_fixture):

    headers = {"Authorization": f"Bearer {invalid_token_fixture}"}

    response = await client.get("v1/me", headers=headers)

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or expired token"


@pytest.mark.anyio
async def test_me_no_user_in_db(client, valid_token_fixture, session_fixture):

    headers = {"Authorization": f"Bearer {valid_token_fixture}"}

    response = await client.get("v1/me", headers=headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"

    user_obj = await session_fixture.execute(select(User))
    user = user_obj.scalars().all()
    assert user == []
    assert len(user) == 0


@pytest.mark.anyio
async def test_me_no_headers(client):
    response = await client.get("v1/me")

    assert response.status_code == 401


@pytest.mark.anyio
async def test_me_wrong_token_int(client, invalid_token_int):

    headers = {"Authorization": f"Bearer {invalid_token_int}"}

    response = await client.get("v1/me", headers=headers)

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or expired token"
