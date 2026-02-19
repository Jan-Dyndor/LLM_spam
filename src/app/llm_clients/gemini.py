import time
from functools import lru_cache

from dotenv import load_dotenv
from google import genai
from google.genai import types
from app.exceptions.exceptions import LLMError
from app.logging.logg import logger

test_text: str = (
    "get the most out of life ! viagra has helped millions of men !\nfor a good cause , wrongdoing is virtuous .\ni don ' t want to be anyone but the person i am .\nthe athlete makes himself , the coach doesn ' t make the athlete ."
)
model: str = "gemini-flash-lite-latest"


@lru_cache
def get_client():
    load_dotenv()
    logger.info("Created API client")
    return genai.Client()


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
    except Exception as e:
        logger.error(f"Google AI model {model} faled to respond")
        raise LLMError() from e

    duration_ms = (time.perf_counter() - start_time) * 1000

    if response.text is None:
        logger.error(f"Google AI model {model} returned empty response")
        raise ValueError("Model returned empty response")
    logger.info(f"Google AI model {model} returned OK in {duration_ms:.2f}ms")
    return response.text
