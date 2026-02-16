from dotenv import load_dotenv
from google import genai
from google.genai import types

from llm_spam.prompts.prompt_v1 import PROMPT

load_dotenv()


client = genai.Client()
model: str = "gemini-flash-lite-latest"


def generate_llm_response(text_to_classify: str) -> None:
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=f"<text>{text_to_classify}</text>"),
            ],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        system_instruction=PROMPT,
        thinking_config=types.ThinkingConfig(
            thinking_budget=0,  # klasyfikacja nie potrzebuje "myślenia"
        ),
        temperature=0.2,  # bardziej deterministyczne JSON
    )

    response = client.models.generate_content(
        model=model,
        contents=contents,
        config=generate_content_config,
    )
    print(response.text)
    print("==================")
    print(response)


generate_llm_response(
    "get the most out of life ! viagra has helped millions of men !\nfor a good cause , wrongdoing is virtuous .\ni don ' t want to be anyone but the person i am .\nthe athlete makes himself , the coach doesn ' t make the athlete ."
)
