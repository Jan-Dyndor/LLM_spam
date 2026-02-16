from dotenv import load_dotenv
from google import genai
from google.genai import types


load_dotenv()
client = genai.Client()
model: str = "gemini-flash-lite-latest"
test_text: str = (
    "get the most out of life ! viagra has helped millions of men !\nfor a good cause , wrongdoing is virtuous .\ni don ' t want to be anyone but the person i am .\nthe athlete makes himself , the coach doesn ' t make the athlete ."
)


def generate_llm_response(text_to_classify: str, prompt: str):
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

    response = client.models.generate_content(
        model=model,
        contents=contents,
        config=generate_content_config,
    )
    if response.text is None:
        raise ValueError("Model returned empty response")
    return response.text
