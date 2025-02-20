import unittest
from unittest.mock import Mock, patch

import requests

from src.utils import get_stock_price


class TestGetStockPrice(unittest.TestCase):

    @patch("src.utils.requests.get")
    def test_get_stock_price_success(self, mock_get):
        # Настройка имитации ответа от API
        mock_response = Mock()
        mock_response.json.return_value = {"Global Quote": {"05. price": "150.00"}}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        # Вызов функции
        symbols = ["AAPL", "GOOGL"]
        result = get_stock_price(symbols, api_key_stock="test_api_key")

        # Проверка результата
        expected_result = [{"акция": "AAPL", "цена": 150.00}, {"акция": "GOOGL", "цена": 150.00}]
        self.assertEqual(result, expected_result)

    @patch("src.utils.requests.get")
    def test_get_stock_price_request_exception(self, mock_get):
        # Настройка имитации исключения при запросе
        mock_get.side_effect = requests.exceptions.RequestException("Ошибка запроса")

        # Вызов функции
        symbols = ["AAPL"]
        result = get_stock_price(symbols, api_key_stock="test_api_key")

        # Проверка результата
        expected_result = [{"акция": "AAPL", "цена": "Ошибка при получении данных"}]
        self.assertEqual(result, expected_result)

    @patch.dict("os.environ", {"API_KEY_stock_price": ""})  # Устанавливаем пустую переменную окружения
    def test_get_stock_price_not_api_key(self):
        # Проверка на отсутствие API ключа, когда он не передан
        with self.assertRaises(ValueError) as context:
            get_stock_price(["AAPL"])  # api_key_stock по умолчанию будет None
        self.assertEqual(str(context.exception), "Ошибка при сохранении результата: API_KEY не установлен.")


def test_get_stock_price_multiple_symbols_with_errors():
    """Проверка получения цен акций с частичными ошибками"""
    symbols = ["AAPL", "INVALID", "GOOGL"]

    def side_effect(url, *args, **kwargs):
        if "AAPL" in url:
            response = Mock()
            response.json.return_value = {"Global Quote": {"05. price": "150.00"}}
            return response
        elif "INVALID" in url:
            raise requests.exceptions.RequestException("Symbol not found")
        elif "GOOGL" in url:
            response = Mock()
            response.json.return_value = {"Global Quote": {"05. price": "2500.00"}}
            return response

    with patch("src.utils.requests.get", side_effect=side_effect):
        result = get_stock_price(symbols, api_key_stock="test_key")

        assert len(result) == 3
        assert result[0]["акция"] == "AAPL"
        assert result[0]["цена"] == 150.00
        assert result[1]["акция"] == "INVALID"
        assert result[1]["цена"] == "Ошибка при получении данных"
        assert result[2]["акция"] == "GOOGL"
        assert result[2]["цена"] == 2500.00


def test_get_stock_price_no_global_quote():
    """Проверка обработки ответа без Global Quote"""
    symbols = ["AAPL"]

    def side_effect(url, *args, **kwargs):
        response = Mock()
        response.json.return_value = {}
        return response

    with patch("src.utils.requests.get", side_effect=side_effect):
        result = get_stock_price(symbols, api_key_stock="test_key")

        assert len(result) == 1
        assert result[0]["акция"] == "AAPL"
        assert result[0]["цена"] == "Данные недоступны"


def test_get_stock_price_invalid_price():
    """Проверка обработки некорректной цены"""
    symbols = ["AAPL"]

    def side_effect(url, *args, **kwargs):
        response = Mock()
        response.json.return_value = {"Global Quote": {"05. price": "invalid"}}
        return response

    with patch("src.utils.requests.get", side_effect=side_effect):
        result = get_stock_price(symbols, api_key_stock="test_key")

        assert len(result) == 1
        assert result[0]["акция"] == "AAPL"
        assert result[0]["цена"] == "Данные недоступны"
