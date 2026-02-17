import json
from pydantic import ValidationError
from app.exceptions.exceptions import LLMInvalidJSONError, LLMInvalidValidationError
from app.llm_clients.gemini import generate_llm_response
from app.prompts.prompt_v1 import PROMPT
from app.schemas.pydantic_schemas import LLM_Response


def classify_spam(text: str) -> LLM_Response:
    raw_output = generate_llm_response(text, PROMPT)

    try:
        json_output = json.loads(raw_output)
    except json.JSONDecodeError as error:
        raise LLMInvalidJSONError() from error

    try:
        validated_output = LLM_Response.model_validate(json_output)
    except ValidationError as error:
        raise LLMInvalidValidationError() from error

    return validated_output
