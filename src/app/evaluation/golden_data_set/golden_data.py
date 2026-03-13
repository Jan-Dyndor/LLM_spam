import pandas as pd

from app.schemas.pydantic_schemas import LLM_Response

test_data = [
    # {
    #     "text": "Earn $5000 per week from home with no experience required.",
    #     "label": "spam",
    # },
    # {
    #     "text": "Dear user, your package is on hold. Pay the shipping fee here.",
    #     "label": "spam",
    # },
    {
        "text": "You have been selected for an exclusive investment opportunity. Act fast.",
        "label": "spam",
    },
    {
        "text": "Reminder: your dentist appointment is scheduled for Monday at 15:30.",
        "label": "not_spam",
    },
    # {
    #     "text": "Please find attached the updated project documentation.",
    #     "label": "not_spam",
    # },
    # {
    #     "text": "The team meeting has been moved to 2 PM due to a scheduling conflict.",
    #     "label": "not_spam",
    # },
]

test_df = pd.DataFrame(test_data)

output_string = [
    {
        "label": "spam",
        "confidence": 0.95,
        "reason": "Contains unsolicited promotion for Viagra, a common spam topic.",
    },
    {
        "label": "spam",
        "confidence": 0.95,
        "reason": "Contains unsolicited promotion for Viagra, a common spam topic.",
    },
]

output_string_llm: list[LLM_Response] = [
    LLM_Response.model_validate(output) for output in output_string
]
