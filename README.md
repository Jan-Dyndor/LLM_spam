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
