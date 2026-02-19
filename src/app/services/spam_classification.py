import json
from pydantic import ValidationError
from app.exceptions.exceptions import LLMInvalidJSONError, LLMInvalidValidationError
from app.llm_clients.gemini import generate_llm_response
from app.prompts.prompt_v1 import PROMPT
from app.schemas.pydantic_schemas import LLM_Response
from app.logging.logg import logger


def classify_spam(text: str) -> LLM_Response:

    raw_output = generate_llm_response(text, PROMPT)
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
