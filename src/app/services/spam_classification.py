import json

from pydantic import ValidationError
from tenacity import (
    before_sleep_log,
    retry,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential,
)

from app.exceptions.exceptions import LLMInvalidJSONError, LLMInvalidValidationError
from app.logging.logg import logger
from app.retry_utils.retry import should_retry
from app.schemas.pydantic_schemas import LLM_Response
import logging


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=3),
    retry=retry_if_exception(should_retry),
    reraise=True,
    before_sleep=before_sleep_log(logger=logger, log_level=logging.WARNING),
)
def classify_spam(text: str) -> LLM_Response:

    # raw_output = generate_llm_response(text, PROMPT)
    raw_output = """ 
    {
   label:spam,
   confidence:0.95,
   reason:Contains unsolicited promotion for Viagra, a common spam topic."
    }
    """

    logger.info("Validation of AI output")
    try:
        json_output = json.loads(raw_output)
    except json.JSONDecodeError as error:
        logger.error("AI model returned invalid JSON object")
        raise LLMInvalidJSONError() from error

    try:
        validated_output = LLM_Response.model_validate(json_output)
    except ValidationError as error:
        logger.error("AI model returned invalid Pydantic model")
        raise LLMInvalidValidationError() from error

    logger.info("Finished validation of AI output")
    return validated_output
