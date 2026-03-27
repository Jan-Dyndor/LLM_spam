# LLM Spam Classifier API

Production-ready **FastAPI backend for spam classification powered by a Large Language Model (Google Gemini).**

This project demonstrates how to build a **robust AI-powered API service** with:

- structured LLM prompts
- strict output validation
- retry mechanisms
- caching
- authentication
- database persistence
- model evaluation pipelines

The system wraps an LLM behind a clean API layer and applies **backend engineering best practices for AI systems.**

For this taks I am using **gemini-2.5-flash-lite** and I recomend using this model. It was testes within appliction and working correctly.

# Running the Project

A) With Docker (quick setup):
1. Clone the repository:
   https://github.com/Jan-Dyndor/LLM_spam

2. Create new env file
```
.env.docker
```
This files should contain
```env
GEMINI_API_KEY=your_google_ai_studio_api_key
SECRET_KEY=your_secret_key
REDIS_HOST=redis
REDIS_PORT=6379
POSTGRES__DB_URL="postgresql+asyncpg://user:password@postgres:5432/db_name"
POSTGRES_PASSWORD=password
POSTGRES_USER=user
POSTGRES_DB=db_name
```

3. Build docker images in root of the project
```
docker compose build
```

4. Run docker containers
```
docker compose up
```
5. For app open 
```
http://0.0.0.0:8000/docs
```
6 For Grafana open
```
http://localhost:3000/login
```
**username: admin**

**password: admin**

Navigate to Dashboards -> App Observability

Start making requests , tests, have fun and look at your logs and metrcis! 

B) Witout Docker (dev setup):
Without Grafana stack

1. Install Redis

2. Install Postgress

3. Clone the repository:
   https://github.com/Jan-Dyndor/LLM_spam

4. Create a virtual environment:

```
python -m venv .venv
source .venv/bin/activate
```

5. Install the project dependencies:

```
pip install -e .
```

-e . installs the package based on pyproject.toml.

6. Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_google_ai_studio_api_key
SECRET_KEY=your_secret_key
REDIS_HOST=localhost
REDIS_PORT=6379
POSTGRES__DB_URL="postgresql+asyncpg://user:password@localhost:5432/db_name"
```
**Create this Data base by hand - with exatly the same parameters as in URL**
**Create also test DB (below credentials) by hand so all tests can pass**

```env
url="postgresql+asyncpg://jan:1234@localhost:5432/test_llm_spam_api"
```
7. Navigate to src/app and run project 

```
fastapi main.py
```

# Project Overview

**LLM Spam Classifier** is an API service that classifies text messages (emails, SMS, etc.) as:

- **spam**
- **ham** (not spam)

The service ensures reliability and consistency by enforcing:

- structured JSON responses from the LLM
- Pydantic validation
- deterministic prompt design
- API versioning
- caching of model responses
- retry logic for LLM calls
- user authentication
- database persistence
- evaluation with a golden dataset

The project is designed as a **production-style AI backend**, demonstrating how LLM models can be integrated into real backend systems.

---

# System Architecture

```text
The system follows a layered architecture.
Client
│
▼
FastAPI Router
│
▼
Service Layer
│
▼
LLM Client (Google Gemini)
│
▼
Structured JSON Response
│
▼
Pydantic Validation
│
▼
Database + API Response
```

### Workflow

1. Client sends request to `/v1/classify`
2. Input is validated using **Pydantic**
3. Router delegates processing to the **service layer**
4. Service builds a **structured prompt**
5. Gemini API is called
6. Model response is parsed and validated
7. Result is cached and stored in the database
8. Structured output is returned to the client

---

# Expected LLM Response Format

The LLM must return strictly formatted JSON:

```json
{
  "label": "spam" | "ham",
  "confidence": 0.0,
  "reason": "short explanation"
}
```

This response is validated by Pydantic models before being returned.

### Key Features

LLM Integration

- Google Gemini API
- structured prompts
- strict JSON output
- deterministic inference pipeline

### Authentication (JWT)

Endpoints requiring authentication:

- /classify
- /users/me/predictions
- /me
- /golden/data/evaluate_model
- /golden_data/get_all_metrics

## Authentication flow:

1. Create user
2. Obtain JWT token
3. Use token to access protected endpoints

## Redis Caching

This project uses Redis for caching model responses.

You must have a Redis instance running locally.

The /classify endpoint uses Redis caching.

Purpose

Avoid repeated calls to the LLM when the same text was already classified.

Behavior

```
User sends text
        │
        ▼
Check Redis cache
        │
   ┌────┴─────┐
   │          │
Cache hit   Cache miss
   │          │
Return       Call LLM
cached       │
response     ▼
         Save to cache
```

### Cache TTL

300 seconds (5min)

**Notes**

- Redis database is cleared when the application stops
- memory limits can be configured using:

  ```
  redis.conf
  maxmemory
  maxmemory-policy
  ```

  or inside docker-compose.yml.

The result is:

- cached in Redis

- saved in the database

## Retry Mechanism

The project uses Tenacity for retrying LLM calls.

Applied decorator:

```
@retry
```

Retry logic handles:

- transient API failures
- rate limit responses
- temporary network issues
  Custom retry control is implemented via:

```
should_retry()
```

Custom exception:

```
LLM_API_Error
```

This exception carries the underlying API status code, allowing Tenacity to decide whether retrying is appropriate.

## Async Architecture

The application is fully asynchronous.

Components converted to async:

- FastAPI endpoints

- SQLAlchemy database layer

- Google Gemini API client

- test suite

Benefits

- better concurrency

- improved scalability

- efficient handling of external API calls

The Gemini client is created during application lifespan and reused across requests.

## Database

The system stores:

- user accounts
- classification history
- model evaluation results

Main tables:

```
users
posts
metrics
gold_responses
```

## Stored Model Predictions

Every /classify request stores:

- input text

- predicted label

- model confidence

- explanation

- prompt version

- timestamp

Users can later retrieve their prediction history.

# API Endpoints

- Health Check

```
GET /health
```

Response:

```JSON
{
"status": "OK"
}
```

- Create User

```
  POST /create_user
```

Input:

```JSON
{
  "username": "string",
  "email": "user@example.com",
  "password": "string"
}
```

Response:

```JSON
{
  "username": "string",
  "email": "user@example.com",
  "id": 1
}
```

- Login

```
POST /token
```

Uses:

```
OAuth2PasswordRequestForm
```

Responses:

```JSON
{
  "access_token": "string",
  "token_type": "bearer"
}
```

- Current User

```
GET /me
```

Responses:

```JSON
{
  "username": "string",
  "emial" : "string@email.com",
  "id": 1
}
```

- Classify Text

Requires authentication.

```
POST /classify
```

Input:

```JSON
{
  "text": "You won a free iPhone"
}
```

Responses:

```JSON
{
  "label": "spam",
  "confidence": 0.97,
  "reason": "Message promotes a suspicious offer"
}
```

- Show my predictions ( AI model output)

```
POST /users/me/predictions
```

Requires authentication.

Response:

```JSON
{
  "id": 1,
  "user_id": 12,
  "model_name": "gemini-2.0-flash",
  "input_text": "You won a free iPhone!",
  "label": "spam",
  "confidence": 0.97,
  "reason": "The message promotes a suspicious prize which is a common spam pattern.",
  "prompt_version": "v1",
  "is_spam": 1,
  "date": "2026-03-05T12:43:07"
}
```

- Run model evaluation

```
POST /golden_data/evaluate_model"
```

Requires authentication.

Response:

```JSON
{
  "metrics": {
    "id": 1,
    "accuracy": 0.95,
    "precision": 0.96,
    "recall": 0.94,
    "f1_score": 0.95,
    "model_name": "gemini-2.0-flash",
    "date": "2026-03-16T14:30:00"
  },
  "model_responses": [
    {
      "metric_id": 1,
      "model_label": "spam",
      "confidence": 0.98,
      "reason": "Message contains typical spam patterns such as urgent financial opportunity.",
      "true_label": "spam",
      "text": "You have been selected for an exclusive investment opportunity."
    },
    {
      "metric_id": 1,
      "model_label": "ham",
      "confidence": 0.87,
      "reason": "The message appears to be a legitimate reminder.",
      "true_label": "ham",
      "text": "Reminder: your dentist appointment is scheduled for Monday at 15:30."
    }
  ]
}
```

Endpoint do async API call to AI model, calcualtes and saves metrics and responses

- Show all models metris and responses

```
GET /golden_data/get_all_metrics
```

Requires authentication.

Response:

```JSON
[
  {
    "id": 1,
    "accuracy": 0.95,
    "model_name": "gemini-2.0-flash",
    "f1": 0.94,
    "recall": 0.93,
    "precision": 0.96,
    "date": "2026-03-16T14:30:00",
    "model_responses": [
      {
        "metric_id": 1,
        "model_label": "spam",
        "confidence": 0.98,
        "reason": "Message contains typical spam patterns such as urgent financial opportunity.",
        "true_label": "spam",
        "text": "You have been selected for an exclusive investment opportunity."
      },
      {
        "metric_id": 1,
        "model_label": "ham",
        "confidence": 0.87,
        "reason": "The message appears to be a legitimate reminder.",
        "true_label": "ham",
        "text": "Reminder: your dentist appointment is scheduled for Monday at 15:30."
      }
    ]
  },
  {
    "id": 2,
    "accuracy": 0.90,
    "model_name": "gemini-2.0-flash",
    "f1": 0.89,
    "recall": 0.88,
    "precision": 0.91,
    "date": "2026-03-15T12:00:00",
    "model_responses": [
      {
        "metric_id": 2,
        "model_label": "spam",
        "confidence": 0.91,
        "reason": "The message promotes an unrealistic offer which indicates spam.",
        "true_label": "spam",
        "text": "Claim your free investment opportunity now."
      }
    ]
  }
]
```

### Golden Dataset Evaluation

The project includes a model evaluation pipeline.

Purpose

Monitor LLM performance over time.

Tables:

```
metrics
gold_responses
```

Metrics stored:

- accuracy

- precision

- recall

- F1 score

- model name

- evaluation date

Each evaluation run stores:

- predicted labels

- ground truth labels

- model explanations

The gold_responses table links predictions with metrics via:

```
metric_id
```

### Evaluation Endpoints

Two endpoints are provided.

**Retrieve stored evaluation results**

Returns previous evaluation runs.

**Run new evaluation**

Sends golden dataset examples to the LLM and computes fresh metrics.

**Due to Gemini free tier limits:**

```
20 requests per day
10 requests per minute
```

the golden dataset contains only two examples.

This is intentional and serves only as a demonstration of the evaluation pipeline.

## Project Structure

```
LLM_SPAM_CLASSIFIER/

src/app

llm_clients/
gemini.py

prompts/
prompt_v1.py

routers/
v1.py

schemas/
pydantic_schemas.py

services/
spam_classification.py

main.py

.env.docker
.env
pyproject.toml
README.md
```

## Planned Improvements

- Observability with Prometheus and Grafana
