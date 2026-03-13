import time
from functools import lru_cache

from google import genai
from google.genai import types

from app.config.settings import Settings, get_settings
from app.exceptions.exceptions import LLM_API_Error
from app.logging.logg import logger


@lru_cache
def get_client():
    settings: Settings = get_settings()
    logger.info("Created API client")
    return genai.Client(api_key=settings.gemini_api_key.get_secret_value()).aio


async def generate_llm_response(text_to_classify: str, prompt: str):
    settings = get_settings()
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
        temperature=settings.ai_model.temperature,
    )

    try:
        response = await client.models.generate_content(
            # model=settings.ai_model.model_name,
            model="gemini-2.5-flash",
            contents=contents,
            config=generate_content_config,
        )

    except Exception as error:
        error_code = getattr(error, "code", None)
        error_mess = getattr(error, "message", None)
        logger.exception(
            f"Google AI model {settings.ai_model.model_name} faled to respond wich code {error_code} and message {error_mess}"
        )
        raise LLM_API_Error(api_status_code=error_code) from error

    duration_ms = (time.perf_counter() - start_time) * 1000

    if response.text is None:
        logger.error(
            f"Google AI model {settings.ai_model.model_name} returned empty response - retry"
        )
        raise LLM_API_Error(api_status_code=-1)
    logger.info(
        f"Google AI model {settings.ai_model.model_name} returned OK in {duration_ms:.2f}ms"
    )
    return response.text
