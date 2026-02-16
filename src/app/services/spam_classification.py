import json

from app.llm_clients.gemini import generate_llm_response
from app.schemas.pydantic_schemas import LLM_Response
from app.prompts.prompt_v1 import PROMPT


def classify_spam(text: str) -> LLM_Response:
    raw_output = generate_llm_response(text, PROMPT)

    json_output = json.loads(raw_output)

    validated_output = LLM_Response.model_validate(json_output)

    return validated_output
