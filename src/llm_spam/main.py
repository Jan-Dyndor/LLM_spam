from dotenv import load_dotenv
from fastapi import FastAPI
from google import genai
from google.genai import types
import json
from llm_spam.models.pydantic_schemas import InputText, LLM_Response
from llm_spam.prompts.prompt_v1 import PROMPT

load_dotenv()


app = FastAPI()


@app.get("/health")
def health_check() -> dict:
    return {"Status": "OK"}


client = genai.Client()
model: str = "gemini-flash-lite-latest"
test_text: str = (
    "get the most out of life ! viagra has helped millions of men !\nfor a good cause , wrongdoing is virtuous .\ni don ' t want to be anyone but the person i am .\nthe athlete makes himself , the coach doesn ' t make the athlete ."
)


@app.post("/classify", response_model=LLM_Response)
async def ask_llm(input: InputText):
    llm = await generate_llm_response(input.text)
    return llm


def generate_llm_response(text_to_classify: str):
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
    return json.loads(response.text)
