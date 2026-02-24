import time
from functools import lru_cache

from google import genai
from app.config.settings import get_settings
from google.genai import types

from app.config.settings import Settings
from app.exceptions.exceptions import LLM_API_Error
from app.logging.logg import logger

# from app.main import get_settings

model: str = "gemini-flash-lite-latest"


@lru_cache
def get_client():
    settings: Settings = get_settings()
    logger.info("Created API client")
    return genai.Client(api_key=settings.gemini_api_key.get_secret_value())


def generate_llm_response(text_to_classify: str, prompt: str):
    start_time = time.perf_counter()
    logger.info("Send request to Google AI API")
    client = get_client()
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=f"<text>{text_to_classify}</text>"),
            ],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        system_instruction=prompt,
        thinking_config=types.ThinkingConfig(
            thinking_budget=0,
        ),
        temperature=0.2,
    )

    try:
        response = client.models.generate_content(
            model=model,
            contents=contents,
            config=generate_content_config,
        )

    except Exception as error:
        error_code = getattr(error, "code", None)
        error_mess = getattr(error, "message", None)
        logger.exception(
            f"Google AI model {model} faled to respond wich code {error_code} and message {error_mess}"
        )
        raise LLM_API_Error(api_status_code=error_code) from error

    duration_ms = (time.perf_counter() - start_time) * 1000

    if response.text is None:
        logger.error(f"Google AI model {model} returned empty response - retry")
        raise LLM_API_Error(api_status_code=-1)
    logger.info(f"Google AI model {model} returned OK in {duration_ms:.2f}ms")
    return response.text
