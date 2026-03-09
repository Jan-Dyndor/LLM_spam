from sqlalchemy import select

from app.authentication.auth import hash_password
from app.db.db_models import Predictions, User


def test_predictions_happy(client, valid_token_fixture, session_fixture):
    new_user = User(
        username="test_user",
        email="test_user@email.com",
        password_hash=hash_password("test_password"),
    )
    session_fixture.add(new_user)
    session_fixture.commit()
    session_fixture.refresh(new_user)

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
    session_fixture.commit()

    headers = {"Authorization": f"Bearer {valid_token_fixture}"}

    response = client.get("v1/users/me/predictions", headers=headers)

    all_pred_obj = session_fixture.execute(select(Predictions))
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
    assert all_preds[1].label == "ham 2"


def test_predictions_invalid_token(client, invalid_token_fixture):

    headers = {"Authorization": f"Bearer {invalid_token_fixture}"}

    response = client.get("v1/users/me/predictions", headers=headers)

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or expired token"


def test_predictions_no_user_in_db(client, valid_token_fixture):
    headers = {"Authorization": f"Bearer {valid_token_fixture}"}

    response = client.get("v1/users/me/predictions", headers=headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "No user with ID 1 found in DB"
    # ID = 1 because in token sub = 1


def test_predictions_wrong_token_int(client, invalid_token_int):

    headers = {"Authorization": f"Bearer {invalid_token_int}"}

    response = client.get("v1/users/me/predictions", headers=headers)

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or expired token"
