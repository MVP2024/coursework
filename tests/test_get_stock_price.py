import unittest
from unittest.mock import patch, Mock
from src.utils import get_stock_price
import requests


class TestGetStockPrice(unittest.TestCase):


	@patch('src.utils.requests.get')
	def test_get_stock_price_success(self, mock_get):
		# Настройка имитации ответа от API
		mock_response = Mock()
		mock_response.json.return_value = {
			"Global Quote": {
				"05. price": "150.00"
			}
		}
		mock_response.raise_for_status = Mock()
		mock_get.return_value = mock_response

		# Вызов функции
		symbols = ["AAPL", "GOOGL"]
		result = get_stock_price(symbols, api_key_stock="test_api_key")

		# Проверка результата
		expected_result = [
			{"акция": "AAPL", "цена": 150.00},
			{"акция": "GOOGL", "цена": 150.00}
		]
		self.assertEqual(result, expected_result)

	@patch('src.utils.requests.get')
	def test_get_stock_price_request_exception(self, mock_get):
		# Настройка имитации исключения при запросе
		mock_get.side_effect = requests.exceptions.RequestException("Ошибка запроса")

		# Вызов функции
		symbols = ["AAPL"]
		result = get_stock_price(symbols, api_key_stock="test_api_key")

		# Проверка результата
		expected_result = [
			{"акция": "AAPL", "цена": "Ошибка при получении данных"}
		]
		self.assertEqual(result, expected_result)


	def test_get_stock_price_no_api_key(self):
		# Проверка на отсутствие API ключа
		with self.assertRaises(ValueError) as context:
			get_stock_price(["AAPL"], api_key_stock=None)
		self.assertEqual(str(context.exception), "API_KEY не установлен.")


	def test_get_stock_price_not_api_key(self):
		# Проверка на отсутствие API ключа, когда он не передан
		with self.assertRaises(ValueError) as context:
			get_stock_price(["AAPL"])  # api_key_stock по умолчанию будет None
		self.assertEqual(str(context.exception), "API_KEY не установлен.")


