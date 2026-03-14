import pandas as pd

test_data = [
    {
        "text": "You have been selected for an exclusive investment opportunity. Act fast.",
        "label": "spam",
    },
    {
        "text": "Reminder: your dentist appointment is scheduled for Monday at 15:30.",
        "label": "ham",
    },
]

test_df = pd.DataFrame(test_data)
