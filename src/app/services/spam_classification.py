import json
from app.exceptions.exceptions import LLMInvalidJSONError
from app.llm_clients.gemini import generate_llm_response
from app.schemas.pydantic_schemas import LLM_Response
from app.prompts.prompt_v1 import PROMPT


def classify_spam(text: str) -> LLM_Response:
    # raw_output = generate_llm_response(text, PROMPT)

    raw_output = "sdfsdf"

    try:
        json_output = json.loads(raw_output)
    except json.JSONDecodeError as error:
        raise LLMInvalidJSONError() from error

    validated_output = LLM_Response.model_validate(json_output)

    return validated_output
