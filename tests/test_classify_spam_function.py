from unittest.mock import patch

import pytest

from app.exceptions.exceptions import LLMInvalidJSONError, LLMInvalidValidationError
from app.schemas.pydantic_schemas import LLM_Response
from app.services.spam_classification import classify_spam


@patch("tenacity.nap.time.sleep")  # Turn off tenacity timer -- speed tests
@patch("app.services.spam_classification.generate_llm_response")
def test_classify_happy(
    mock_llm_responce, _mock_sleep, user_input: str, Model_Response_Happy: str
):
    mock_llm_responce.return_value = Model_Response_Happy
    result = classify_spam(user_input)

    assert isinstance(result, LLM_Response)
    assert result.label == "spam"
    assert result.confidence == 0.95
    assert (
        result.reason
        == "Contains unsolicited promotion for Viagra, a common spam topic."
    )


@patch("tenacity.nap.time.sleep")
@patch("app.services.spam_classification.generate_llm_response")
def test_classify_invalid_json(
    mock_llm, _mock_sleep, user_input: str, Model_Response_Not_Json: str
):
    mock_llm.return_value = Model_Response_Not_Json
    with pytest.raises(LLMInvalidJSONError):
        classify_spam(user_input)
    assert mock_llm.call_count == 3  # Tenacity should try to invoke retry 3 tiems


@patch("tenacity.nap.time.sleep")
@patch("app.services.spam_classification.generate_llm_response")
def test_classify_wrong_validation_label(
    mock_llm, _mock_sleep, user_input, Model_Response_Wrong_Validation_Label
):
    mock_llm.return_value = Model_Response_Wrong_Validation_Label
    with pytest.raises(LLMInvalidValidationError):
        classify_spam(user_input)
    assert mock_llm.call_count == 3


@patch("tenacity.nap.time.sleep")
@patch("app.services.spam_classification.generate_llm_response")
def test_classify_wrong_validation_confidence_1(
    mock_llm, _mock_sleep, user_input, Model_Response_Wrong_Validation_Confidence_1
):
    mock_llm.return_value = Model_Response_Wrong_Validation_Confidence_1
    with pytest.raises(LLMInvalidValidationError):
        classify_spam(user_input)
    assert mock_llm.call_count == 3


@patch("tenacity.nap.time.sleep")
@patch("app.services.spam_classification.generate_llm_response")
def test_classify_wrong_validation_confdence_2(
    mock_llm, _mock_sleep, user_input, Model_Response_Wrong_Validation_Confidence_2
):
    mock_llm.return_value = Model_Response_Wrong_Validation_Confidence_2
    with pytest.raises(LLMInvalidValidationError):
        classify_spam(user_input)
    assert mock_llm.call_count == 3


@patch("tenacity.nap.time.sleep")
@patch("app.services.spam_classification.generate_llm_response")
def test_classify_wrong_validation_reason(
    mock_llm, _mock_sleep, user_input, Model_Response_Wrong_Validation_Reason
):
    mock_llm.return_value = Model_Response_Wrong_Validation_Reason
    with pytest.raises(LLMInvalidValidationError):
        classify_spam(user_input)
    assert mock_llm.call_count == 3


# Test Retry mechanism


@patch("tenacity.nap.time.sleep")
@patch("app.services.spam_classification.generate_llm_response")
def test_classify_wrong_json_then_happy(
    mock_llm, _mock_sleep, user_input, Model_Response_Happy, Model_Response_Not_Json
):
    invalid_out = Model_Response_Not_Json
    valid_out = Model_Response_Happy
    mock_llm.side_effect = [invalid_out, valid_out]

    classify_spam(user_input)
    assert mock_llm.call_count == 2


@patch("tenacity.nap.time.sleep")
@patch("app.services.spam_classification.generate_llm_response")
def test_classify_wrong_validation_then_happy(
    mock_llm,
    _mock_sleep,
    user_input,
    Model_Response_Happy,
    Model_Response_Wrong_Validation_Confidence_1,
):
    valid = Model_Response_Happy
    invalid = Model_Response_Wrong_Validation_Confidence_1
    mock_llm.side_effect = [invalid, valid]

    classify_spam(user_input)
    assert mock_llm.call_count == 2
