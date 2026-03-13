import asyncio

import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
)

from app.evaluation.golden_data_set.golden_data import (
    output_string_llm,
    test_df,
)
from app.schemas.pydantic_schemas import LLM_Response
from app.services.spam_classification import classify_spam

# SCIKIT LEARN METRIC Calcualtion fuynctions


async def ask_llm_godlen_data() -> list[LLM_Response]:
    """
    Function send concurent async request to Google AI API
    """

    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(classify_spam(input)) for input in test_df["text"]]

    responses = [task.result() for task in tasks]

    return responses


def preprocess_to_df(model_responses: list[LLM_Response]) -> pd.DataFrame:

    model_responses_dict = [response.model_dump() for response in model_responses]

    df = pd.DataFrame.from_records(model_responses_dict)

    df.rename(columns={"label": "model_label"}, inplace=True)
    df["true_label"] = test_df["label"]
    return df


def calcualte_metrics(dataframe: pd.DataFrame):  # -> pd.DataFrame:
    y_true = dataframe["true_label"]
    y_preds = dataframe["model_label"]

    accuracy = accuracy_score(y_true, y_preds)
    f1 = f1_score(y_true, y_preds, pos_label="spam")
    recall = recall_score(y_true, y_preds, pos_label="spam")
    precision = precision_score(y_true, y_preds, pos_label="spam")

    data_dict = dataframe.to_dict(orient="records")

    return accuracy, f1, recall, precision, data_dict


async def eval_model():
    # responces = await ask_llm_godlen_data() na czas debugowania
    responces_df = preprocess_to_df(output_string_llm)
    accuracy, f1, recall, precision, data = calcualte_metrics(responces_df)

    print(data)
    return float(accuracy), float(f1), float(recall), float(precision), data


# Zastanow sie nad tym jak to przerobic na lepsze api
# moze wgl nie trzymac tego w pandas DF? Zobaczymy
