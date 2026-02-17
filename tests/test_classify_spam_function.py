from app.schemas.pydantic_schemas import LLM_Response
from unittest.mock import patch
from app.services.spam_classification import classify_spam
import pytest
from app.exceptions.exceptions import LLMInvalidJSONError


@patch("app.services.spam_classification.generate_llm_response")
def test_classify_happy(mock_llm_responce, user_input: str, ModelResponseHappy: str):
    mock_llm_responce.return_value = ModelResponseHappy

    result = classify_spam(user_input)

    assert isinstance(result, LLM_Response)
    assert result.label == "spam"
    assert result.confidence == 0.95
    assert (
        result.reason
        == "Contains unsolicited promotion for Viagra, a common spam topic."
    )


@patch("app.services.spam_classification.generate_llm_response")
def test_classify_invalid_json(mock_llm, user_input: str, ModelResponseNotJson: str):
    mock_llm.return_value = ModelResponseNotJson
    with pytest.raises(LLMInvalidJSONError):
        classify_spam(user_input)
