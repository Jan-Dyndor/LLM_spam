from sqlalchemy import select

from app.db.db_models import User


def test_create_user_happy(client, session_fixture, test_user_valid):
    """
    In this scenario no users are in DB
    """
    response = client.post("v1/create_user", json=test_user_valid)

    user_obj = session_fixture.execute(select(User))

    user = user_obj.scalars().first()
    assert user is not None
    assert user.id == 1
    assert user.email == "test_user@email.com"

    assert response.status_code == 200
    assert response.json()["id"] == 1
    assert response.json()["username"] == "test_username"
    assert response.json()["email"] == "test_user@email.com"
