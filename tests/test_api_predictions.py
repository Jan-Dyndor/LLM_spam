import pytest
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.authentication.auth import hash_password
from app.db.db_models import Predictions, User


@pytest.mark.anyio
async def test_predictions_happy(client, valid_token_fixture, session_fixture):
    new_user = User(
        username="test_user",
        email="test_user@email.com",
        password_hash=hash_password("test_password"),
    )
    session_fixture.add(new_user)
    await session_fixture.commit()
    await session_fixture.refresh(new_user)

    new_pred_1 = Predictions(
        user_id=new_user.id,
        input_text="Test 1",
        model_name="test_model 1",
        label="spam 1",
        reason="Test spam reason 1",
        prompt_version="test_version 1 ",
        confidence=0.0,
    )

    new_pred_2 = Predictions(
        user_id=new_user.id,
        input_text="Test 2",
        model_name="test_model 2",
        label="ham 2",
        reason="Test spam reason 2",
        prompt_version="test_version 2",
        confidence=1.0,
    )

    session_fixture.add_all([new_user, new_pred_1, new_pred_2])
    await session_fixture.commit()

    headers = {"Authorization": f"Bearer {valid_token_fixture}"}

    response = await client.get("v1/users/me/predictions", headers=headers)

    all_pred_obj = await session_fixture.execute(select(Predictions))
    all_preds = all_pred_obj.scalars().all()

    assert response.status_code == 200

    assert all_preds != []
    assert isinstance(all_preds, list)
    assert all_preds[0].id == 1
    assert all_preds[0].confidence == 0.0
    assert all_preds[0].label == "spam 1"

    assert all_preds[1].id == 2
    assert all_preds[1].confidence == 1.0
    assert all_preds[1].label == "ham 2"

    # Different way - its how we do it in endpoint by using relationships
    user_obj = await session_fixture.execute(
        select(User).options(selectinload(User.spam)).where(User.id == 1)
    )
    user = user_obj.scalars().first()

    spam = user.spam
    print(spam)
    assert isinstance(spam, list)
    assert spam[0].id == 1
    assert spam[0].confidence == 0.0
    assert spam[0].label == "spam 1"

    assert spam[1].id == 2
    assert spam[1].confidence == 1.0
    assert spam[1].label == "ham 2"


@pytest.mark.anyio
async def test_predictions_invalid_token(client, invalid_token_fixture):

    headers = {"Authorization": f"Bearer {invalid_token_fixture}"}

    response = await client.get("v1/users/me/predictions", headers=headers)

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or expired token"


@pytest.mark.anyio
async def test_predictions_no_user_in_db(client, valid_token_fixture):
    headers = {"Authorization": f"Bearer {valid_token_fixture}"}

    response = await client.get("v1/users/me/predictions", headers=headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "No user with ID 1 found in DB"
    # ID = 1 because in token sub = 1


@pytest.mark.anyio
async def test_predictions_wrong_token_int(client, invalid_token_int):

    headers = {"Authorization": f"Bearer {invalid_token_int}"}

    response = await client.get("v1/users/me/predictions", headers=headers)

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or expired token"
