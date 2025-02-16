import json
from unittest.mock import patch

import pytest

from src.views import main


@patch("src.views.load_data_from_excel")
@patch("src.views.get_currency_rates")
@patch("src.views.get_stock_price")
def test_main_success(mock_get_stock_price, mock_get_currency_rates, mock_load_data_from_excel):
    mock_load_data_from_excel.return_value = [
        {"Дата операции": "01.01.2023 12:00:00", "Сумма операции": -100},
        {"Дата операции": "02.01.2023 12:00:00", "Сумма операции": -50},
    ]
    mock_get_currency_rates.return_value = [{"валюта": "USD", "ставка": 75.0}, {"валюта": "EUR", "ставка": 85.0}]
    mock_get_stock_price.return_value = {"AAPL": 150.0, "AMZN": 3000.0}

    result = main("2023-01-01", "M")

    # Преобразуем строку JSON обратно в словарь
    result_dict = json.loads(result)

    assert isinstance(result_dict, dict)
    assert "Диапазон дат" in result_dict
    assert "Результат анализа" in result_dict
    assert "Курсы валют" in result_dict
    assert "Биржевые цены" in result_dict


def test_main_invalid_range_type():
    """Тест с недопустимым значением range_type."""
    with pytest.raises(ValueError, match="Недопустимое значение range_type."):
        main("2023-01-01", "INVALID")


def test_main_file_not_found():
    """Тест с отсутствующим файлом данных."""
    with patch("os.path.exists", return_value=False):
        with pytest.raises(FileNotFoundError):
            main("2023-01-01", "M")


def test_main_empty_transactions(mock_load_data_from_excel):
    """Тест с пустым списком транзакций."""
    with patch("src.views.load_data_from_excel", return_value=[]):
        with pytest.raises(ValueError, match="Список транзакций пуст."):
            main("2023-01-01", "M")


def test_main_missing_transaction_keys(mock_load_data_from_excel):
    """Тест с отсутствующими ключами в транзакциях."""
    with patch("src.views.load_data_from_excel", return_value=[{"Дата операции": "01.01.2023 00:00:00"}]):
        with pytest.raises(ValueError, match="Транзакция должна содержать ключи:"):
            main("2023-01-01", "M")


def test_main_missing_api_key_currency(mock_1_load_data_from_excel, mock_analyze_transactions):
    """Тест с отсутствующим API_KEY для курсов валют."""
    with patch.dict("os.environ", {"API_KEY_currency": ""}):
        with pytest.raises(ValueError, match="API_KEY для получения курсов валют не установлен."):
            main("2023-01-01", "M")


def test_main_missing_api_key_stock(mock_1_load_data_from_excel, mock_analyze_transactions, mock_get_currency_rates):
    """Тест с отсутствующим API_KEY для цен акций."""
    with patch.dict("os.environ", {"API_KEY_stock_price": ""}):
        with pytest.raises(ValueError, match="API_KEY для получения цен акций не установлен."):
            main("2023-01-01", "M")


def test_main_json_save_error(
    mock_env_vars,
    mock_1_load_data_from_excel,
    mock_analyze_transactions,
    mock_get_currency_rates,
    mock_get_stock_price,
):
    """Тест с ошибкой записи в файл user_settings.json."""
    with patch("builtins.open", side_effect=Exception("Ошибка записи в файл")):
        with pytest.raises(Exception, match="Ошибка записи в файл"):
            main("2023-01-01", "M")


def test_main_currency_api_error(mock_env_vars, mock_1_load_data_from_excel, mock_analyze_transactions):
    """Тест с ошибкой при получении курсов валют."""
    with patch("src.views.get_currency_rates", side_effect=Exception("Ошибка API курсов валют")):
        with pytest.raises(Exception, match="Ошибка API курсов валют"):
            main("2023-01-01", "M")


@patch("src.views.get_currency_rates", return_value=[{"валюта": "USD", "ставка": 75.0}])
@patch("src.views.get_stock_price", side_effect=Exception("Ошибка API цен акций"))
def test_main_stock_api_error(
    mock_stock_price, mock_currency_rates, mock_env_vars, mock_1_load_data_from_excel, mock_analyze_transactions
):
    """Тест с ошибкой при получении цен акций."""
    with pytest.raises(Exception, match="Ошибка API цен акций"):
        main("2023-01-01", "M")


def test_main_invalid_date_format_empty():
    """Тест с пустой строкой в качестве даты."""
    with pytest.raises(ValueError, match="time data '' does not match format '%Y-%m-%d'"):
        main("", "M")


def test_main_invalid_date_format_nonexistent():
    """Тест с несуществующей датой."""
    with pytest.raises(ValueError) as excinfo:
        main("2023-02-30", "M")
    assert "day is out of range for month" in str(excinfo.value)


def test_main_range_type_week():
    """Тест с диапазоном 'W'."""
    with patch(
        "src.views.load_data_from_excel",
        return_value=[
            {"Дата операции": "01.01.2023 12:00:00", "Сумма операции": -100},
            {"Дата операции": "02.01.2023 12:00:00", "Сумма операции": -50},
        ],
    ):
        result = main("2023-01-01", "W")

        # Преобразуем строку JSON обратно в словарь
        result = json.loads(result)

        assert result["Диапазон дат"]["Начало"] == "2022-12-26"  # Понедельник предыдущей недели
        assert result["Диапазон дат"]["Конец"] == "2023-01-01"


def test_main_range_type_year():
    """Тест с диапазоном 'Y'."""
    with patch(
        "src.views.load_data_from_excel",
        return_value=[
            {"Дата операции": "01.01.2023 12:00:00", "Сумма операции": -100},
            {"Дата операции": "02.01.2023 12:00:00", "Сумма операции": -50},
        ],
    ):
        result = main("2023-01-01", "Y")

        # Преобразуем строку JSON обратно в словарь
        result = json.loads(result)

        assert result["Диапазон дат"]["Начало"] == "2023-01-01"
        assert result["Диапазон дат"]["Конец"] == "2023-01-01"


def test_main_range_type_all():
    """Тест с диапазоном 'ALL'."""
    with patch(
        "src.views.load_data_from_excel",
        return_value=[
            {"Дата операции": "01.01.2023 12:00:00", "Сумма операции": -100},
            {"Дата операции": "02.01.2023 12:00:00", "Сумма операции": -50},
        ],
    ):
        result = main("2023-01-01", "ALL")

        # Преобразуем строку JSON обратно в словарь
        result_dict = json.loads(result)

        assert result_dict["Диапазон дат"]["Начало"] == "0001-01-01"  # Минимальная дата
        assert result_dict["Диапазон дат"]["Конец"] == "2023-01-01"


def test_main_analyze_transactions_error():
    """Тест с ошибкой в функции analyze_transactions."""
    with patch(
        "src.views.load_data_from_excel",
        return_value=[
            {"Дата операции": "01.01.2023 12:00:00", "Сумма операции": -100},
            {"Дата операции": "02.01.2023 12:00:00", "Сумма операции": -50},
        ],
    ):
        with patch("src.views.analyze_transactions", side_effect=Exception("Ошибка анализа транзакций")):
            with pytest.raises(Exception, match="Ошибка анализа транзакций"):
                main("2023-01-01", "M")


def test_main_invalid_date_format():
    """Тест с неверным форматом даты."""
    with pytest.raises(ValueError, match="time data 'invalid_date' does not match format '%Y-%m-%d'"):
        main("invalid_date", "M")
