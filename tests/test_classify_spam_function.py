from unittest.mock import patch

import pytest
from pydantic import ValidationError

from app.exceptions.exceptions import LLMInvalidJSONError, LLMInvalidValidationError
from app.schemas.pydantic_schemas import LLM_Response
from app.services.spam_classification import classify_spam


@patch("app.services.spam_classification.generate_llm_response")
def test_classify_happy(mock_llm_responce, user_input: str, Model_Response_Happy: str):
    mock_llm_responce.return_value = Model_Response_Happy

    result = classify_spam(user_input)

    assert isinstance(result, LLM_Response)
    assert result.label == "spam"
    assert result.confidence == 0.95
    assert (
        result.reason
        == "Contains unsolicited promotion for Viagra, a common spam topic."
    )


@patch("app.services.spam_classification.generate_llm_response")
def test_classify_invalid_json(mock_llm, user_input: str, Model_Response_Not_Json: str):
    mock_llm.return_value = Model_Response_Not_Json
    with pytest.raises(LLMInvalidJSONError):
        classify_spam(user_input)


@patch("app.services.spam_classification.generate_llm_response")
def test_classify_wrong_validation_label(
    mock_llm, user_input, Model_Response_Wrong_Validation_Label
):
    mock_llm.return_value = Model_Response_Wrong_Validation_Label
    with pytest.raises(LLMInvalidValidationError):
        classify_spam(user_input)


@patch("app.services.spam_classification.generate_llm_response")
def test_classify_wrong_validation_confidence_1(
    mock_llm, user_input, Model_Response_Wrong_Validation_Confidence_1
):
    mock_llm.return_value = Model_Response_Wrong_Validation_Confidence_1
    with pytest.raises(LLMInvalidValidationError):
        classify_spam(user_input)


@patch("app.services.spam_classification.generate_llm_response")
def test_classify_wrong_validation_confdence_2(
    mock_llm, user_input, Model_Response_Wrong_Validation_Confidence_2
):
    mock_llm.return_value = Model_Response_Wrong_Validation_Confidence_2
    with pytest.raises(LLMInvalidValidationError):
        classify_spam(user_input)


@patch("app.services.spam_classification.generate_llm_response")
def test_classify_wrong_validation_reason(
    mock_llm, user_input, Model_Response_Wrong_Validation_Reason
):
    mock_llm.return_value = Model_Response_Wrong_Validation_Reason
    with pytest.raises(LLMInvalidValidationError):
        classify_spam(user_input)
