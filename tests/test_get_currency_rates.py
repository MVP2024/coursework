import pytest
from unittest.mock import patch, Mock
from src.utils import get_currency_rates
import requests  # Импортируем requests

def test_get_currency_rates_success():
    api_key = "fake_api_key"
    base_currency = "RUB"
    target_currencies = ["USD", "EUR"]

    # Мокируем ответ API
    mock_response = Mock()
    mock_response.json.return_value = {
        "conversion_rates": {
            "USD": 100,
            "EUR": 50,
        }
    }
    mock_response.status_code = 200

    with patch('requests.get', return_value=mock_response):
        result = get_currency_rates(api_key, base_currency, target_currencies)
        expected_result = [
            {"валюта": "USD", "ставка": 0.01},
            {"валюта": "EUR", "ставка": 0.02}
        ]
        assert result == expected_result



def test_get_currency_rates_request_exception():
    api_key = "fake_api_key"
    base_currency = "RUB"
