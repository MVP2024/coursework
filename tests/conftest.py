from typing import List, Dict, Any

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

