from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.services.spam_classification import classify_spam

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
