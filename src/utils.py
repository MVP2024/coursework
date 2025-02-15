import os
from collections import defaultdict
from datetime import datetime, timedelta
import pandas as pd
import requests
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional

from src.decorators import report_to_file
from src.logger import setup_logger

# Настройка логгера для модуля utils
logger = setup_logger(__name__)

# Загружаем переменные окружения из файла .env
load_dotenv()

# Применяем декоратор
@report_to_file()
def load_data_from_excel(file_path: str) -> List[Dict[str, Any]]:
    """Загрузка данных из Excel и преобразование в список словарей.

    Args:
        file_path (str): Путь к файлу Excel.

    Returns:
        List[Dict[str, Any]]: Список словарей, представляющих данные из Excel.

    Raises:
        FileNotFoundError: Если файл не найден.
    """
    logger.info(f"Загрузка данных из Excel: {file_path}")

    # Проверка существования файла
    if not os.path.exists(file_path):
        logger.info(f"Файл не найден: {file_path}")
        raise FileNotFoundError(f"Файл не найден: {file_path}")

    try:
        df = pd.read_excel(file_path, na_filter=True)
        logger.info("Данные успешно загружены.")
    except Exception as e:
        logger.error(f"Ошибка при загрузке данных из Excel: {e}")
        return []

    df.fillna(value=0, inplace=True)  # Заменит все NaN на 0
    return df.to_dict(orient='records')


# Применяем декоратор
@report_to_file()
def get_currency_rates(api_key_currency: Optional[str] = None, base_currency: str = "RUB", target_currencies: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """Загружает данные о курсе валют с API и возвращает список словарей.

    Args:
        api_key_currency (Optional[str]): API-ключ для доступа к курсам валют.
        base_currency (str): Базовая валюта для конвертации. По умолчанию "RUB".
        target_currencies (Optional[List[str]]): Список целевых валют для получения курсов.

    Returns:
        List[Dict[str, Any]]: Список словарей с курсами валют.

    Raises:
        ValueError: Если API_KEY не установлен или не удалось получить курсы валют.
    """
    logger.info("Получение курсов валют.")

    # Если API-ключ не передан, пытаемся загрузить его из переменных окружения
    if api_key_currency is None or api_key_currency == "":
        api_key_currency = os.getenv('API_KEY_currency')

    if not api_key_currency:  # Проверка на None и пустую строку после загрузки из окружения
        logger.error("API_KEY не установлен.")
        raise ValueError("API_KEY не установлен.")

    logger.info("API_KEY_currency загружен.")  # Логируем, что ключ загружен

    # URL API для получения курсов валют
    url = f"https://v6.exchangerate-api.com/v6/{api_key_currency}/latest/{base_currency}"
    headers = {"apikey": api_key_currency}

    try:
        # Отправляем GET-запрос к API
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Проверяем, что запрос успешен

        # Парсим JSON-ответ
        data = response.json()

        # Извлекаем курсы валют
        rates = data.get("conversion_rates", {})
        logger.info("Курсы валют успешно получены.")

        # Формируем список словарей в нужном формате
        if target_currencies:
            currency_rates = [
                {"валюта": currency, "ставка": round(1 / rates[currency], 2)}
                for currency in target_currencies
                if currency in rates
            ]
        else:
            currency_rates = [{"валюта": currency, "ставка": round(1 / rate, 2)} for currency, rate in rates.items()]

        return currency_rates

    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при получении курсов валют: {e}")
        raise ValueError("Не удалось получить курсы валют.") from e


# Применяем декоратор
@report_to_file()
def get_stock_price(symbols: List[str], api_key_stock: Optional[str] = None) -> List[Dict[str, Any]]:
    """Получение текущей стоимости акций по списку символов с использованием Alpha Vantage API.

    Args:
        symbols (List[str]): Список символов акций для получения цен.
        api_key_stock (Optional[str]): API-ключ для доступа к данным акций.

    Returns:
        List[Dict[str, Any]]: Список словарей с текущими ценами акций.

    Raises:
        ValueError: Если API_KEY не установлен или не удалось получить данные акций.
    """
    logger.info("Получение цен акций.")

    # Если API-ключ не передан, пытаемся загрузить его из переменных окружения
    if api_key_stock is None or api_key_stock == "":
        api_key_stock = os.getenv('API_KEY_stock_price')

    if not api_key_stock:  # Проверка на None и пустую строку после загрузки из окружения
        logger.error("API_KEY не установлен.")
        raise ValueError("API_KEY не установлен.")

    logger.info("API_KEY_stock_price загружен.")  # Логируем, что ключ загружен

    stock_prices = []

    for symbol in symbols:
        # URL API для получения данных об акции
        url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={api_key_stock}"

        try:
            # Отправляем GET-запрос к API
            response = requests.get(url)
            response.raise_for_status()  # Проверяем, что запрос успешен

            # Парсим JSON-ответ
            data = response.json()

            # Извлекаем текущую стоимость акции
            price = data.get("Global Quote", {}).get("05. price", "N/A")

            # Добавляем данные в список
            stock_prices.append({
                "акция": symbol,
                "цена": float(price) if price != "N/A" else "Данные недоступны"
            })
            logger.info(f"Цена для {symbol}: {price}")

        except requests.exceptions.RequestException as e:
            logger.error(f"Не удалось получить данные для {symbol}: {e}")
            stock_prices.append({
                "акция": symbol,
                "цена": "Ошибка при получении данных"
            })

    return stock_prices


# Применяем декоратор
@report_to_file()
def analyze_transactions(transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Анализ транзакций и формирование отчета.

    Args:
        transactions (List[Dict[str, Any]]): Список транзакций для анализа.

    Returns:
        Dict[str, Any]: Словарь с результатами анализа, включая общие суммы расходов и доходов, а также категории.
    """
    logger.info("Начало анализа транзакций.")
    category_totals = defaultdict(float)
    total_expenses = 0
    total_income = 0
    amount_income = 0  # Для пополнений
    amount_cashback = 0  # Для бонусов и кэшбэка

    for transaction in transactions:
        category = transaction['Категория']
        amount = transaction['Сумма операции']

        if amount < 0:  # Расходы
            total_expenses += abs(amount)
            category_totals[category] += abs(amount)
        else:  # Поступления
            total_income += amount
            if category == "Пополнения":  # Пополнения
                amount_income += amount
            elif category == "Бонусы (включая кэшбэк)":  # Бонусы
                amount_cashback += amount

    # Сортируем категории по убыванию суммы
    sorted_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)

    # Формируем результат для расходов
    result_expenses = []
    for category, total in sorted_categories[:7]:
        result_expenses.append({
            'Категория': category,
            'Сумма': round(total)
        })

    # Добавляем категорию "Остальные"
    other_total = sum(total for _, total in sorted_categories[7:])
    if other_total > 0:
        result_expenses.append({
            'Категория': 'Остальные',
            'Сумма': round(other_total)
        })

    logger.info("Анализ транзакций завершен.")
    return {
        'Расходы': {
            'Общая сумма': round(total_expenses),
            'Основные': result_expenses
        },
        'Доходы': {
            'Общий доход': round(total_income),
            'Категории': [
                {
                    'Категория': 'Пополнения',
                    'Сумма': round(amount_income)
                },
                {
                    'Категория': 'Бонусы (включая кэшбэк)',
                    'Сумма': round(amount_cashback)
                }
            ]
        }
    }
