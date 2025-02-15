import pytest
import pandas as pd
from unittest.mock import patch
from src.views import main

from typing import List, Dict, Any
import os
import pytest
import pandas as pd
from unittest.mock import patch, MagicMock


# Фикстура для функции `load_data_from_excel`
@pytest.fixture
def mock_load_data_from_excel():
    with patch('src.utils.pd.read_excel') as mock_read_excel:
        yield mock_read_excel

@pytest.fixture
def sample_excel_data():
    # Создаем пример DataFrame, который будет возвращен при вызове pd.read_excel
    data = {
        'Категория': ['Еда', 'Транспорт', 'Развлечения'],
        'Сумма операции': [-100, -50, -20],
        'Дата операции': ['01.01.2025 12:00:00', '02.01.2025 12:00:00', '03.01.2025 12:00:00']
    }
    return pd.DataFrame(data)


# Фикстуры для функции `filter_transactions`
@pytest.fixture
def sample_transactions() -> List[Dict[str, Any]]:
    return [
        {"Дата операции": "01.01.2025 12:00:00", "Сумма операции": -100, "Категория": "Еда"},
        {"Дата операции": "15.01.2025 12:00:00", "Сумма операции": -50, "Категория": "Транспорт"},
        {"Дата операции": "20.01.2025 12:00:00", "Сумма операции": -20, "Категория": "Развлечения"},
        {"Дата операции": "05.02.2025 12:00:00", "Сумма операции": -30, "Категория": "Еда"},
        {"Дата операции": "01.02.2025 12:00:00", "Сумма операции": -10, "Категория": "Транспорт"},
    ]


# Фикстуры для функции `get_currency_rates`
@pytest.fixture
def mock_requests_get():
    with patch('src.utils.requests.get') as mock_get:
        yield mock_get


# Фикстуры для функции `analyze_transactions`
@pytest.fixture
def transactions_data():
    return [
        {'Категория': 'Еда', 'Сумма операции': -100},
        {'Категория': 'Транспорт', 'Сумма операции': -50},
        {'Категория': 'Зарплата', 'Сумма операции': 1000},
        {'Категория': 'Инвестиции', 'Сумма операции': 200},
        {'Категория': 'Бонусы (включая кэшбэк)', 'Сумма операции': 50},
    ]


# Фикстуры для функции `main`
@pytest.fixture
def mock_env_vars():
    with patch.dict('os.environ', {'API_KEY_currency': 'test_key', 'API_KEY_stock_price': 'test_key'}):
        yield

@pytest.fixture
def mock_1_load_data_from_excel():
    with patch('src.utils.load_data_from_excel', return_value=[{"Дата операции": "01.01.2023 00:00:00", "Сумма операции": 100}]):
        yield

@pytest.fixture
def mock_analyze_transactions():
    with patch('src.utils.analyze_transactions', return_value={"total": 100}):
        yield

@pytest.fixture
def mock_get_currency_rates():
    with patch('src.utils.get_currency_rates', return_value={"USD": 75.0, "EUR": 85.0, "CNY": 12.0}):
        yield

@pytest.fixture
def mock_get_stock_price():
    with patch('src.utils.get_stock_price', return_value={"AAPL": 150.0, "AMZN": 3000.0}):
        yield