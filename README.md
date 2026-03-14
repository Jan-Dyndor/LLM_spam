# LLM Spam Classifier API

**Production-ready FastAPI backend for spam classification powered by a Large Language Model (Google Gemini).**

This project demonstrates how to wrap an LLM behind a clean API layer with strict validation, structured prompts, and production-oriented architecture.

---

## Overview

**LLM Spam Classifier** is a backend service that classifies email or SMS messages as:

- **spam**
- **ham** (not spam)

The system enforces:

- **Strict JSON responses** from the LLM
- **Pydantic-based** input/output validation
- **Clear separation of concerns**
- **Deterministic inference**
- **Versioned API design**

This project focuses on clean architecture, robust LLM integration, and AI backend engineering best practices.

---

## How the System Works

1. **Client** sends a POST request to: `/v1/classify`
2. **Input** is validated via Pydantic.
3. **Router** delegates to the service layer.
4. **Service layer**:
   - Builds structured prompt
   - Calls Gemini API
   - Parses JSON output
   - Validates structured response
5. **Validated response** is returned to the client.

### Expected Model Output

```json
{
  "label": "spam" | "ham",
  "confidence": 0.0 - 1.0,
  "reason": "short explanation"
}
```

```json
LLM_SPAM_CLASSIFIER/
│
├── src/
│   └── app/
│       ├── llm_clients/
│       │   └── gemini.py
│       │
│       ├── prompts/
│       │   └── prompt_v1.py
│       │
│       ├── routers/
│       │   └── v1.py
│       │
│       ├── schemas/
│       │   └── pydantic_schemas.py
│       │
│       ├── services/
│       │   └── spam_classification.py
│       │
│       └── main.py
│
├── .env
├── pyproject.toml
├── requirements.txt
└── README.md
```

## ADD LATER

- to pip isntall pre-commit and then isnall pre-commit for ruff
- write about tenacity retry -pplied @retry to classify_spam, allowing exceptions from generate_llm_response to propagate and be handled by Tenacity. Introduced should_retry to control retry behavior based on API status codes and custom LLM exceptions.
  Added a new LLM_API_Error carrying the underlying API status code.
- Added Redis cache to /classify endpoint. It allows to check whether someone already asked AI to classify the same string. If yes : return cahced version if no ask LLM model. Added TTl of 300 second (5 min) to each user query to LLM. Remember. to set up maxmemory in dockercompose file. USer also can set up maxmemory and policy in Redis in redis.conf file - write about that. Also remeber to mention that after every app shutdown Redis DB is cleaned!
- Add that user has to add his/hers Google Srudio API Key in .env file in root of the projekct anemd as GEMINI_API_KEY=......
  REDIS**HOST=redis
  REDIS**PORT=6379 .env file also have this so it will overwrite the settings if neded and will be easier to use Docker also add SECRET_KEY fou can generate one by using python -c "import secrets; print(secrets.token_hex(32))"
  - Added Database and full JWT authentication. Now endpoints :
    /classify require logging , after auth it saves user input and model output od DB

        Inoput {

    "text": "string"
    }

responce:
{
"label": "spam",
"confidence": 1,
"reason": "string"
}
/create_user - create user wit user name ( unique), email (unique) and password ( later is hashed)
Input:
{
"username": "string",
"email": "user@example.com",
"password": "stringst"
}

        responce :
        {
        "username": "string",
        "email": "user@example.com",
        "id": 0
        }

/token - endpoint provides user with JWT TOKEN
Input from OAuth2PasswordRequestForm
{
"access_token": "string",
"token_type": "string"
}
/me - get info about current loged user - model response
{
"username": "string",
"email": "user@example.com",
"id": 0
}
/my_posts - endpoint is only avaliabe to logged users, it allows to check model responces, and detials aboput the model call
Responce:
[
{
"id": 0,
"user_id": 0,
"model_name": "string",
"input_text": "string",
"label": "string",
"confidence": 0,
"reason": "string",
"prompt_version": "string",
"is_spam": 0,
"date": "2026-03-05T12:43:07.701Z"
}
]
/ health
output: {
"Status": "OK"
}
So user have to be logged to be able to use /classify endpint and his/her respnse from AI model is saved in DB later to be viewd

- changed DB from sync to async , changed endpoints to asycn , chenkged Google genai client to async client andd added to lifespan as cache so client is reused at each API connection
- rewriteded all tests to async

- added new tables i DB gold_responses and metrics. Table metrics will hold data like accurac, recall, pecision, f1 score model nanme and date - those metrics are calcuated based on the model results from Golden Data set. Table gold_responsec contains fields like metric_id ( its ofregin key to table metrics , since we can send few examples to test model responses and we calcualte metrics to theose responces as a whoel we have an opstion to connect mterics reesults to specific data that model worked on), model_label (spam / ham),confidence , reason, true_lable from golden data set ane text based on. what model decides.

Also I added endpoint to send godlen_data to Google AI model and calcuatle fresh metrics. This endpoint saves those metrics and output of mdoel to above tables and retrives the prvious metricvs and results of mdoel work and sends it back to user

- GOLDEN data is only 2 examples beacuse rare limiting in google AI API high ( 20 RPD and 10 RPM). So ot save some API use one 2 examples - it is just to demonstrate thats important no monitor model performance
