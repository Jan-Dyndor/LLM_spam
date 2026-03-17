from unittest.mock import patch

import pandas as pd
import pytest
from pandas import testing as tm

from app.evaluation.evaluate_model import (
    calcualte_metrics,
    eval_model,
    preprocess_to_df,
)


# TEST preporcess_to_df function
def test_preprocess_to_df_happy(model_responses_goloden_data_test):

    df = preprocess_to_df(model_responses_goloden_data_test)

    expected_model_label_column = pd.Series(["spam", "spam"], name="model_label")
    expected_true_label_column = pd.Series(["spam", "ham"], name="true_label")
    expected_text_column = pd.Series(
        [
            "You have been selected for an exclusive investment opportunity. Act fast.",
            "Reminder: your dentist appointment is scheduled for Monday at 15:30.",
        ],
        name="text",
    )

    tm.assert_series_equal(df["model_label"], expected_model_label_column)
    tm.assert_series_equal(df["true_label"], expected_true_label_column)
    tm.assert_series_equal(df["text"], expected_text_column)


# TEST calcualte_metrics function
def test_calculate_metrics(correct_df_to_calc_metrics):

    accuracy, f1, recall, precision, data_dict = calcualte_metrics(
        correct_df_to_calc_metrics
    )
    print(correct_df_to_calc_metrics)

    assert accuracy == 0.5
    assert round(f1, 3) == 0.667
    assert recall == 1.0
    assert precision == 0.5

    assert isinstance(data_dict, list)
    assert len(data_dict) == 2


# Test whole function without external API calls
@pytest.mark.anyio
@patch("app.evaluation.evaluate_model.ask_llm_godlen_data")
async def test_happy_evaluation(ask_llm_mock, model_responses_goloden_data_test):

    ask_llm_mock.return_value = (
        model_responses_goloden_data_test  # list of LLM response objects
    )
    accuracy, f1, recall, precision, data = await eval_model()
    assert accuracy == 0.5
    assert round(f1, 3) == 0.667
    assert recall == 1.0
    assert precision == 0.5

    assert isinstance(data, list)
    assert len(data) == 2
