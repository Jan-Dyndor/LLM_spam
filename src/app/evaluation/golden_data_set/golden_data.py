import pandas as pd

from app.schemas.pydantic_schemas import LLM_Response


dataset_name = [
    {
        "text": "You have been selected for an exclusive investment opportunity. Act fast.",
        "label": "spam",
    },
    {
        "text": "Reminder: your dentist appointment is scheduled for Monday at 15:30.",
        "label": "ham",
    },
]

test_df = pd.DataFrame(dataset_name)

example_response = LLM_Response(label="spam", confidence=0.56, reason="Test")
example_response2 = LLM_Response(label="spam", confidence=1, reason="222")
list_examples = [example_response, example_response2]
