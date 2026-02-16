from fastapi import FastAPI
from llm_spam.models.pydantic_schemas import InputText, LLM_Response
from llm_spam.services.spam_classification import classify_spam

app = FastAPI()


@app.get("/health")
def health_check() -> dict:
    return {"Status": "OK"}


@app.post("/classify", response_model=LLM_Response)
async def ask_llm(input: InputText):
    return classify_spam(input.text)
