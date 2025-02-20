import json

import pandas as pd

from src.reports import spending_by_category


# Создаем тестовые данные
def create_test_data():
    return pd.DataFrame(
        {
            "Категория": ["Еда", "Транспорт", "Еда", "Развлечения"],
            "Дата операции": [
                "01.01.2023 12:00:00",
                "15.01.2023 12:00:00",
                "20.02.2023 12:00:00",
                "10.03.2023 12:00:00",
            ],
            "Сумма операции": [100.0, 50.0, 200.0, 150.0],
        }
    )


def test_spending_by_category_no_data():
    transactions_df = create_test_data()
    result_data = json.loads(spending_by_category(transactions_df, "Недвижимость"))

    expected_result = {"transactions": [], "total_spending": 0.0}
    assert result_data == expected_result


def test_invalid_transactions_type():
    try:
        spending_by_category("Некорректный тип", "Еда")
    except ValueError as e:
        assert "transactions должно быть DataFrame." in str(e)
    else:
        assert False, "Expected ValueError was not raised."


def test_spending_by_category_empty_dataframe():
    empty_df = pd.DataFrame(columns=["Категория", "Дата операции", "Сумма операции"])
    result_data = json.loads(spending_by_category(empty_df, "Еда"))

    expected_result = {"transactions": [], "total_spending": 0.0}
    assert result_data == expected_result


def test_spending_by_category_valid():
    transactions_df = create_test_data()
    result_data = json.loads(spending_by_category(transactions_df, "Еда", "20.03.2023"))

    expected_result = {
        "transactions": [
            {"Категория": "Еда", "Дата операции": "01.01.2023 12:00:00", "Сумма операции": 100.0},
            {"Категория": "Еда", "Дата операции": "20.02.2023 12:00:00", "Сумма операции": 200.0},
        ],
        "total_spending": 300.0,
    }
    assert result_data == expected_result


def test_spending_by_category_with_date():
    transactions_df = create_test_data()
    result_data = json.loads(spending_by_category(transactions_df, "Еда", "15.01.2023"))

    expected_result = {
        "transactions": [
            {"Категория": "Еда", "Дата операции": "01.01.2023 12:00:00", "Сумма операции": 100.0},
        ],
        "total_spending": 100.0,
    }
    assert result_data == expected_result
