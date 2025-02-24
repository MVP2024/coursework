from unittest.mock import Mock

import pandas as pd
import pytest


@pytest.fixture
def mock_load_data_from_excel():
    mock_read_excel = Mock()
    mock_read_excel.return_value = pd.DataFrame(
        {"Категория": ["Test"], "Сумма операции": [100], "Дата операции": ["01.01.2025 12:00:00"]}
    )
    return mock_read_excel


@pytest.fixture
def mock_load_data():
    return [
        {"Дата операции": "01.01.2023 12:00:00", "Сумма операции": -100},
        {"Дата операции": "02.01.2023 12:00:00", "Сумма операции": -50},
    ]


@pytest.fixture
def mock_currency_rates():
    return [{"валюта": "USD", "ставка": 75.0}, {"валюта": "EUR", "ставка": 85.0}]


@pytest.fixture
def mock_stock_prices():
    return [{"акция": "AAPL", "цена": 150.0}, {"акция": "AMZN", "цена": 3000.0}]


@pytest.fixture
def transactions_data():
    return [
        {"Категория": "Еда", "Сумма операции": -100},
        {"Категория": "Транспорт", "Сумма операции": -50},
        {"Категория": "Зарплата", "Сумма операции": 1000},
        {"Категория": "Инвестиции", "Сумма операции": 200},
        {"Категория": "Бонусы (включая кэшбэк)", "Сумма операции": 50},
    ]


@pytest.fixture
def sample_transactions():
    return pd.DataFrame(
        {
            "Категория": ["Еда", "Транспорт", "Еда", "Развлечения"],
            "Сумма операции": [-100, -50, -200, -75],
            "Дата операции": [
                "01.01.2025 12:00:00",
                "15.01.2025 12:00:00",
                "20.01.2025 12:00:00",
                "10.12.2024 12:00:00",
            ],
        }
    )
