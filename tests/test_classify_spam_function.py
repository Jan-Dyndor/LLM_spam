from unittest.mock import patch

import pytest
from tenacity import wait_fixed

from app.exceptions.exceptions import LLMInvalidJSONError, LLMInvalidValidationError
from app.schemas.pydantic_schemas import LLM_Response
from app.services.spam_classification import classify_spam


@pytest.mark.anyio
# # Patch Tenacity wait in tests to avoid real sleep delays
# @patch("tenacity.nap.time.sleep") There are issues with this solution in async so I found this     with mock.patch.object(classify_spam.retry, "wait", wait_fixed(0)):
@patch("app.services.spam_classification.generate_llm_response")
async def test_classify_happy(
    mock_llm_responce, user_input: str, Model_Response_Happy: str
):
    with patch.object(classify_spam.retry, "wait", wait_fixed(0)):  # type: ignore
        mock_llm_responce.return_value = Model_Response_Happy
        result = await classify_spam(user_input)

    assert isinstance(result, LLM_Response)
    assert result.label == "spam"
    assert result.confidence == 0.95
    assert (
        result.reason
        == "Contains unsolicited promotion for Viagra, a common spam topic."
    )


@pytest.mark.anyio
@patch("app.services.spam_classification.generate_llm_response")
async def test_classify_invalid_json(
    mock_llm, user_input: str, Model_Response_Not_Json: str
):
    mock_llm.return_value = Model_Response_Not_Json

    with patch.object(classify_spam.retry, "wait", wait_fixed(0)):  # type: ignore
        with pytest.raises(LLMInvalidJSONError):
            await classify_spam(user_input)

    assert mock_llm.call_count == 3  # Tenacity should try to invoke retry 3 tiems


@pytest.mark.anyio
@patch("app.services.spam_classification.generate_llm_response")
async def test_classify_wrong_validation_label(
    mock_llm, user_input, Model_Response_Wrong_Validation_Label
):
    mock_llm.return_value = Model_Response_Wrong_Validation_Label

    with patch.object(classify_spam.retry, "wait", wait_fixed(0)):  # type: ignore
        with pytest.raises(LLMInvalidValidationError):
            await classify_spam(user_input)
    assert mock_llm.call_count == 3


@pytest.mark.anyio
@patch("app.services.spam_classification.generate_llm_response")
async def test_classify_wrong_validation_confidence_1(
    mock_llm, user_input, Model_Response_Wrong_Validation_Confidence_1
):
    mock_llm.return_value = Model_Response_Wrong_Validation_Confidence_1

    with patch.object(classify_spam.retry, "wait", wait_fixed(0)):  # type: ignore
        with pytest.raises(LLMInvalidValidationError):
            await classify_spam(user_input)

    assert mock_llm.call_count == 3


@patch("app.services.spam_classification.generate_llm_response")
@pytest.mark.anyio
async def test_classify_wrong_validation_confdence_2(
    mock_llm, user_input, Model_Response_Wrong_Validation_Confidence_2
):
    mock_llm.return_value = Model_Response_Wrong_Validation_Confidence_2

    with patch.object(classify_spam.retry, "wait", wait_fixed(0)):  # type: ignore
        with pytest.raises(LLMInvalidValidationError):
            await classify_spam(user_input)

    assert mock_llm.call_count == 3


@patch("app.services.spam_classification.generate_llm_response")
@pytest.mark.anyio
async def test_classify_wrong_validation_reason(
    mock_llm, user_input, Model_Response_Wrong_Validation_Reason
):
    mock_llm.return_value = Model_Response_Wrong_Validation_Reason
    with patch.object(classify_spam.retry, "wait", wait_fixed(0)):  # type: ignore
        with pytest.raises(LLMInvalidValidationError):
            await classify_spam(user_input)

    assert mock_llm.call_count == 3


# Test Retry mechanism


@pytest.mark.anyio
@patch("app.services.spam_classification.generate_llm_response")
async def test_classify_wrong_json_then_happy(
    mock_llm, user_input, Model_Response_Happy, Model_Response_Not_Json
):
    invalid_out = Model_Response_Not_Json
    valid_out = Model_Response_Happy
    mock_llm.side_effect = [invalid_out, valid_out]
    with patch.object(classify_spam.retry, "wait", wait_fixed(0)):  # type: ignore
        await classify_spam(user_input)

    assert mock_llm.call_count == 2


@pytest.mark.anyio
@patch("app.services.spam_classification.generate_llm_response")
async def test_classify_wrong_validation_then_happy(
    mock_llm,
    user_input,
    Model_Response_Happy,
    Model_Response_Wrong_Validation_Confidence_1,
):
    valid = Model_Response_Happy
    invalid = Model_Response_Wrong_Validation_Confidence_1
    mock_llm.side_effect = [invalid, valid]

    with patch.object(classify_spam.retry, "wait", wait_fixed(0)):  # type: ignore
        await classify_spam(user_input)

    assert mock_llm.call_count == 2
