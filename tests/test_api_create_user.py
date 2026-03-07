from sqlalchemy import select

from app.db.db_models import User


def test_create_user_happy(client, session_fixture, test_user_valid):
    """
    In this scenario no users are in DB
    """
    response = client.post("v1/create_user", json=test_user_valid)

    user_obj = session_fixture.execute(select(User))
    user_objs = session_fixture.execute(select(User))

    user = user_obj.scalars().first()
    usesrs = user_objs.scalars().all()

    assert user is not None
    assert user.id == 1
    assert user.email == "test_user@email.com"
    assert len(usesrs) == 1

    assert response.status_code == 200
    assert response.json()["id"] == 1
    assert response.json()["username"] == "test_username"
    assert response.json()["email"] == "test_user@email.com"


def test_create_user_invalid_user(client, test_user_invalid):
    response = client.post("v1/create_user", json=test_user_invalid)

    assert response.status_code == 422


def test_client_username_exists(client, session_fixture, test_user_valid):
    new_user = User(
        id=1,
        username="test_username".lower(),
        email="new_test_email@email.com".lower(),
        password_hash="new_test_password_12345678",
    )
    session_fixture.add(new_user)
    session_fixture.commit()
    session_fixture.refresh(new_user)

    response = client.post("v1/create_user", json=test_user_valid)

    users_obj = session_fixture.execute(select(User))
    users = users_obj.scalars().all()

    assert response.status_code == 409
    assert response.json()["detail"] == "Email or User Name already exist"
    assert len(users) == 1


def test_create_user_email_exists(client, test_user_valid, session_fixture):

    new_user = User(
        id=1,
        username="new_test_username".lower(),
        email="test_user@email.com".lower(),
        password_hash="new_test_password_12345678",
    )
    session_fixture.add(new_user)
    session_fixture.commit()
    session_fixture.refresh(new_user)

    response = client.post("v1/create_user", json=test_user_valid)

    users_obj = session_fixture.execute(select(User))
    users = users_obj.scalars().all()

    assert response.status_code == 409
    assert response.json()["detail"] == "Email or User Name already exist"
    assert len(users) == 1
