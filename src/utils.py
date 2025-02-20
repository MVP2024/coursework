import os
from collections import defaultdict
from typing import Any, Dict, Hashable, List, Optional

import pandas as pd
import requests
from dotenv import load_dotenv

from src.decorators import report_to_file
from src.logger import setup_logger

# Настройка логгера для модуля utils
logger = setup_logger(__name__)

# Загружаем переменные окружения из файла .env
load_dotenv()


@report_to_file()
def load_data_from_excel(file_path: str) -> List[Dict[Hashable, Any]]:
    """
    Загрузка данных из Excel и преобразование в список словарей.

    Args:
        file_path (str): Путь к файлу Excel.

    Returns:
        List[Dict[str, Any]]: Список словарей, представляющих данные из Excel.

    Raises:
        FileNotFoundError: Если файл не найден.
        PermissionError: Если нет доступа к файлу.
        ValueError: Если файл пустой или имеет некорректный формат.
    """
    logger.info(f"Загрузка данных из Excel: {file_path}")

    # Проверка существования файла
    if not os.path.exists(file_path):
        logger.error(f"Файл не найден: {file_path}")
        raise FileNotFoundError(f"Файл не найден: {file_path}")

    # Проверка расширения файла
    if not file_path.lower().endswith((".xls", ".xlsx", ".xlsm", ".xlsb")):
        logger.error(f"Некорректный формат файла: {file_path}")
        raise ValueError("Поддерживаются только файлы Excel")

    try:
        df = pd.read_excel(file_path, na_filter=True)
        logger.info("Данные успешно загружены.")
    except PermissionError as e:
        logger.error(f"Ошибка доступа к файлу: {e}")
        raise
    except Exception as e:
        logger.error(f"Ошибка при загрузке данных из Excel: {e}")
        raise

    # Если файл пустой, возвращаем пустой список
    if df.empty:
        logger.warning("Файл пуст.")
        return []

    # Проверка наличия обязательных столбцов
    required_columns = ["Категория", "Сумма операции"]
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        logger.error(f"Отсутствуют обязательные столбцы: {missing_columns}")
        raise ValueError(f"Отсутствуют обязательные столбцы: {missing_columns}")

    # Заменяем NaN на 0 или пустые значения
    df.fillna(value={"Категория": "Без категории", "Сумма операции": 0}, inplace=True)

    # Преобразуем названия столбцов в строки
    df.columns = df.columns.astype(str)

    # Возвращаем список словарей
    return df.to_dict(orient="records")


# Применяем декоратор
@report_to_file()
def get_currency_rates(
    api_key_currency: Optional[str] = None, base_currency: str = "RUB", target_currencies: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """
    Расширенное получение курсов валют с улучшенной обработкой ошибок.
    """
    logger.info("Начало получения курсов валют.")

    # Расширенная логика получения API-ключа
    api_key_currency = api_key_currency or os.getenv("API_KEY_currency") or os.getenv("CURRENCY_API_KEY")

    if not api_key_currency:
        logger.error("Не найден API-ключ для получения курсов валют.")
        raise ValueError("API-ключ для курсов валют не установлен.")

    # URL с поддержкой различных API
    url_templates = [
        f"https://v6.exchangerate-api.com/v6/{api_key_currency}/latest/{base_currency}",
        f"https://openexchangerates.org/api/latest.json?app_id={api_key_currency}",
    ]

    for url in url_templates:
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            data = response.json()

            # Гибкое извлечение курсов
            rates = data.get("conversion_rates", {}) or data.get("rates", {})

            if not rates:
                logger.warning("Не удалось извлечь курсы валют.")
                continue

            # Формирование списка курсов
            if target_currencies:
                currency_rates = [
                    {"валюта": currency, "ставка": round(1 / rates.get(currency, 1), 2)}
                    for currency in target_currencies
                    if currency in rates
                ]
            else:
                currency_rates = [
                    {"валюта": currency, "ставка": round(1 / rate, 2)} for currency, rate in rates.items() if rate > 0
                ]

            return currency_rates

        except (requests.RequestException, ValueError, KeyError) as e:
            logger.warning(f"Ошибка при получении курсов с {url}: {e}")
            continue

    logger.error("Не удалось получить курсы валют ни от одного источника.")
    raise ValueError("Не удалось получить курсы валют.")


# Применяем декоратор
@report_to_file()
def get_stock_price(symbols: List[str], api_key_stock: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Получает текущие цены акций для указанных символов.

    Args:
        symbols (List[str]): Список символов акций для получения цен.
        api_key_stock (Optional[str], optional): API-ключ для сервиса получения цен акций.
            Если не указан, будет использован ключ из переменных окружения.

    Returns:
        List[Dict[str, Any]]: Список словарей с ценами акций, где каждый словарь содержит:
            - "акция": символ акции
            - "цена": текущая цена или сообщение об ошибке

    Raises:
        ValueError: Если API-ключ не установлен.

    Описание:
        - Использует сервис Alpha Vantage для получения котировок
        - Обрабатывает возможные ошибки при получении данных
        - Возвращает цену или сообщение о недоступности данных
    """
    logger.info("Получение цен акций.")

    # Если API-ключ не передан, пытаемся загрузить его из переменных окружения
    if api_key_stock is None or api_key_stock == "":
        api_key_stock = os.getenv("API_KEY_stock_price")

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

            # Добавляем данные в список с обработкой некорректных цен
            try:
                price_value = float(price) if price != "N/A" else "Данные недоступны"
            except ValueError:
                price_value = "Данные недоступны"

            stock_prices.append({"акция": symbol, "цена": price_value})
            logger.info(f"Цена для {symbol}: {price}")

        except requests.exceptions.RequestException as e:
            logger.error(f"Не удалось получить данные для {symbol}: {e}")
            stock_prices.append({"акция": symbol, "цена": "Ошибка при получении данных"})

    return stock_prices


# Применяем декоратор
@report_to_file()
def analyze_transactions(transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Анализирует список транзакций и формирует сводную информацию о доходах и расходах.

    Args:
        transactions (List[Dict[str, Any]]): Список транзакций для анализа.

    Returns:
        Dict[str, Any]: Словарь с информацией о расходах и доходах, содержащий:
            - "Расходы": общая сумма и список основных категорий расходов
            - "Доходы": общий доход и категории доходов

    Описание:
        - Обрабатывает транзакции, игнорируя некорректные или неполные записи
        - Группирует расходы по категориям
        - Выделяет до 7 основных категорий расходов
        - Объединяет остальные категории в "Остальные"
        - Разделяет доходы на "Пополнения" и "Бонусы"
    """
    logger.info("Начало анализа транзакций.")
    category_totals: defaultdict[str, float] = defaultdict(float)
    total_expenses: float = 0.0
    total_income: float = 0.0
    amount_income: float = 0.0
    amount_cashback: float = 0.0

    for transaction in transactions:
        category = transaction.get("Категория")
        amount = transaction.get("Сумма операции")

        if category is None or amount is None:
            logger.warning("Пропущена транзакция из-за отсутствия категории или суммы.")
            continue

        # Преобразование строкового значения в число с дополнительной проверкой
        try:
            # Если amount - строка, пытаемся преобразовать в число
            if isinstance(amount, str):
                # Проверяем, можно ли преобразовать строку в число
                amount = float(amount) if amount.replace("-", "").replace(".", "").isdigit() else None

            # Если после преобразования amount остался None, пропускаем транзакцию
            if amount is None:
                logger.warning(f"Некорректный формат суммы для категории {category}")
                continue

        except (ValueError, TypeError):
            logger.warning(f"Некорректный формат суммы для категории {category}: {amount}")
            continue

        if isinstance(amount, (int, float)):
            if amount < 0:  # Расходы
                total_expenses += abs(amount)
                category_totals[category] += abs(amount)
            else:  # Поступления
                total_income += amount
                if category == "Пополнения":
                    amount_income += amount
                elif category == "Бонусы (включая кэшбэк)":
                    amount_cashback += amount
        else:
            logger.warning(f"Некорректный тип суммы для категории {category}: {amount}")

    # Сортируем категории по убыванию суммы
    sorted_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)

    # Формируем результат для расходов
    result_expenses = []
    for category, total in sorted_categories[:7]:
        result_expenses.append({"Категория": category, "Сумма": round(total)})

    # Добавляем категорию "Остальные"
    other_total = sum(total for _, total in sorted_categories[7:])
    if other_total > 0:
        result_expenses.append({"Категория": "Остальные", "Сумма": round(other_total)})

    logger.info("Анализ транзакций завершен.")
    return {
        "Расходы": {"Общая сумма": round(total_expenses, 2), "Основные": result_expenses},
        "Доходы": {
            "Общий доход": round(total_income, 2),
            "Категории": [
                {"Категория": "Пополнения", "Сумма": round(amount_income, 2)},
                {"Категория": "Бонусы (включая кэшбэк)", "Сумма": round(amount_cashback, 2)},
            ],
        },
    }
