import json
from unittest.mock import patch, mock_open, Mock
import os
import pytest

from src.views import events





def test_events_success(mock_load_data, mock_currency_rates, mock_stock_prices):
    """
    Проверка успешного выполнения функции events.
    """
    with patch('src.views.load_data_from_excel', return_value=mock_load_data), \
        patch('src.views.get_currency_rates', return_value=mock_currency_rates), \
        patch('src.views.get_stock_price', return_value=mock_stock_prices), \
        patch('os.path.exists', return_value=True), \
        patch('builtins.open', mock_open()):
        result = events("2023-01-01", "M")
        result_dict = json.loads(result)

        assert isinstance(result_dict, dict)
        assert "Диапазон дат" in result_dict
        assert "Результат анализа" in result_dict
        assert "Курсы валют" in result_dict
        assert "Биржевые цены" in result_dict


def test_events_invalid_range_type():
    """
    Проверка обработки недопустимого типа диапазона.
    """
    with pytest.raises(ValueError, match="Недопустимое значение range_type"):
        events("2023-01-01", "INVALID")


def test_events_file_not_found():
    """
    Проверка обработки отсутствующего файла данных.
    """
    with patch('os.path.exists', return_value=False):
        with pytest.raises(FileNotFoundError):
            events("2023-01-01", "M")


def test_events_empty_transactions():
    """
    Проверка обработки пустого списка транзакций.
    """
    with patch('src.views.load_data_from_excel', return_value=[]):
        with pytest.raises(ValueError, match="Список транзакций пуст"):
            events("2023-01-01", "M")


def test_events_missing_transaction_keys():
    """
    Проверка обработки транзакций с отсутствующими ключами.
    """
    with patch('src.views.load_data_from_excel', return_value=[{"Incomplete": "Transaction"}]):
        with pytest.raises(ValueError, match="Транзакция должна содержать ключи"):
            events("2023-01-01", "M")


def test_events_missing_currency_api_key(mock_load_data):
    """
    Проверка обработки отсутствующего API-ключа для курсов валют.
    """
    with patch('src.views.load_data_from_excel', return_value=mock_load_data), \
        patch.dict(os.environ, {"API_KEY_currency": ""}):
        with pytest.raises(ValueError, match="API_KEY для получения курсов валют не установлен"):
            events("2023-01-01", "M")


def test_events_missing_stock_api_key(mock_load_data, mock_currency_rates):
    """
    Проверка обработки отсутствующего API-ключа для цен акций.
    """
    with patch('src.views.load_data_from_excel', return_value=mock_load_data), \
        patch('src.views.get_currency_rates', return_value=mock_currency_rates), \
        patch.dict(os.environ, {"API_KEY_stock_price": ""}):
        with pytest.raises(ValueError, match="API_KEY для получения цен акций не установлен"):
            events("2023-01-01", "M")


def test_events_range_type_week():
    """
    Проверка расчета диапазона для недели.
    """
    with patch('src.views.load_data_from_excel', return_value=[
        {"Дата операции": "01.01.2023 12:00:00", "Сумма операции": -100}
    ]), \
        patch('src.views.get_currency_rates', return_value=[]), \
        patch('src.views.get_stock_price', return_value=[]):
        result = events("2023-01-01", "W")
        result_dict = json.loads(result)

        assert result_dict["Диапазон дат"]["Начало"] == "2022-12-26"
        assert result_dict["Диапазон дат"]["Конец"] == "2023-01-01"


def test_events_range_type_year():
    """
    Проверка расчета диапазона для года.
    """
    with patch('src.views.load_data_from_excel', return_value=[
        {"Дата операции": "01.01.2023 12:00:00", "Сумма операции": -100}
    ]), \
        patch('src.views.get_currency_rates', return_value=[]), \
        patch('src.views.get_stock_price', return_value=[]):
        result = events("2023-01-01", "Y")
        result_dict = json.loads(result)

        assert result_dict["Диапазон дат"]["Начало"] == "2023-01-01"
        assert result_dict["Диапазон дат"]["Конец"] == "2023-01-01"


def test_events_range_type_all():
    """
    Проверка расчета диапазона для всех данных.
    """
    with patch('src.views.load_data_from_excel', return_value=[
        {"Дата операции": "01.01.2023 12:00:00", "Сумма операции": -100}
    ]), \
        patch('src.views.get_currency_rates', return_value=[]), \
        patch('src.views.get_stock_price', return_value=[]):
        result = events("2023-01-01", "ALL")
        result_dict = json.loads(result)

        assert result_dict["Диапазон дат"]["Начало"] == "0001-01-01"
        assert result_dict["Диапазон дат"]["Конец"] == "2023-01-01"


def test_events_json_save_error(mock_load_data, mock_currency_rates, mock_stock_prices):
    """
    Проверка обработки ошибки при сохранении JSON.
    """
    with patch('src.views.load_data_from_excel', return_value=mock_load_data), \
        patch('src.views.get_currency_rates', return_value=mock_currency_rates), \
        patch('src.views.get_stock_price', return_value=mock_stock_prices), \
        patch('builtins.open', side_effect=IOError("Ошибка записи")):
        with pytest.raises(ValueError, match="Ошибка при сохранении результата: Ошибка записи"):
            events("2023-01-01", "M")


def test_events_invalid_date_format():
    """
    Проверка обработки некорректного формата даты.
    """
    with pytest.raises(ValueError, match="time data"):
        events("invalid_date", "M")


def test_events_settings_file_json_decode_error(mock_load_data, mock_currency_rates, mock_stock_prices):
    """
    Проверка обработки ошибки декодирования JSON при чтении файла настроек
    """
    with patch('src.views.load_data_from_excel', return_value=mock_load_data), \
         patch('src.views.get_currency_rates', return_value=mock_currency_rates), \
         patch('src.views.get_stock_price', return_value=mock_stock_prices), \
         patch('os.path.exists', return_value=True), \
         patch('builtins.open', mock_open(read_data='invalid json')), \
         patch('json.load', side_effect=json.JSONDecodeError("", "", 0)):
        result = events("2023-01-01", "M")
        assert result is not None
