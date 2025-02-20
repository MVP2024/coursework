from unittest.mock import Mock, patch

import pytest
import requests

from src.utils import get_currency_rates


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

    with patch("requests.get", return_value=mock_response):
        result = get_currency_rates(api_key, base_currency, target_currencies)
        expected_result = [{"валюта": "USD", "ставка": 0.01}, {"валюта": "EUR", "ставка": 0.02}]
        assert result == expected_result


def test_get_currency_rates_request_exception():
    api_key = "fake_api_key"
    base_currency = "RUB"

    with patch("requests.get") as mock_get:
        mock_get.side_effect = Exception("API request failed")

        with pytest.raises(ValueError, match="Ошибка при сохранении результата: API request failed"):
            get_currency_rates(api_key, base_currency, ["USD", "EUR"])


def test_get_currency_rates_no_target_currencies():
    """Проверка получения курсов валют без указания целевых валют"""
    api_key = "fake_api_key"
    mock_response = Mock()
    mock_response.json.return_value = {"conversion_rates": {"USD": 100, "EUR": 50, "GBP": 75}}
    mock_response.status_code = 200

    with patch("requests.get", return_value=mock_response):
        result = get_currency_rates(api_key)
        assert len(result) == 3
        assert all("валюта" in rate and "ставка" in rate for rate in result)


def test_get_currency_rates_invalid_api_key():
    """Проверка обработки недопустимого API-ключа"""
    with patch("requests.get") as mock_get:
        mock_get.side_effect = requests.exceptions.HTTPError("Invalid API key")

        with pytest.raises(ValueError, match="Не удалось получить курсы валют"):
            get_currency_rates("invalid_key")


def test_get_currency_rates_empty_rates():
    """Проверка обработки пустого списка курсов"""
    api_key = "fake_api_key"
    mock_response = Mock()
    mock_response.json.return_value = {"conversion_rates": {}}
    mock_response.status_code = 200

    with patch("requests.get", return_value=mock_response):
        with pytest.raises(ValueError, match="Не удалось получить курсы валют"):
            get_currency_rates(api_key)


def test_get_currency_rates_zero_rates():
    """Проверка обработки курсов с нулевыми значениями"""
    api_key = "fake_api_key"
    mock_response = Mock()
    mock_response.json.return_value = {"conversion_rates": {"USD": 0, "EUR": 0}}
    mock_response.status_code = 200

    with patch("requests.get", return_value=mock_response):
        result = get_currency_rates(api_key)
        assert result == []


def test_get_currency_rates_default_currencies():
    # Мокаем requests.get, чтобы вернуть тестовые данные
    with patch("requests.get") as mock_get, patch.dict("os.environ", {"API_KEY_currency": "test_key"}):
        mock_response = Mock()
        mock_response.json.return_value = {
            "conversion_rates": {"USD": 1.5, "EUR": 0.8, "GBP": 0, "JPY": -2}  # Нулевая ставка  # Отрицательная ставка
        }
        mock_get.return_value = mock_response
        mock_get.return_value.raise_for_status = Mock()

        # Вызываем функцию
        result = get_currency_rates()

        # Проверяем результат
        assert len(result) == 2  # Только USD и EUR
        assert {"валюта": "USD", "ставка": 0.67} in result
        assert {"валюта": "EUR", "ставка": 1.25} in result
