import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any

from src.decorators import report_to_file
from src.utils import load_data_from_excel, analyze_transactions, get_currency_rates, get_stock_price

@report_to_file()
def main(date_str: str, range_type: str = 'M') -> str:
    """
    Основная функция, которая фильтрует данные по диапазону дат, анализирует транзакции,
    получает курсы валют и цены акций.

    :param date_str: Строка с датой в формате 'YYYY-MM-DD'.
    :param range_type: Диапазон данных ('W', 'M', 'Y', 'ALL'). По умолчанию 'M'.
    :return: Строка с результатами анализа, курсов валют и цен акций, включая диапазон дат.
    :raises ValueError: Если передан недопустимый диапазон данных.
    :raises FileNotFoundError: Если файл с данными не найден.
    :raises Exception: Если возникают ошибки при загрузке данных или запросах к API.
    """
    try:
        # Преобразуем строку с датой в объект datetime
        date = datetime.strptime(date_str, "%Y-%m-%d")

        # Определяем начальную и конечную даты в зависимости от range_type
        if range_type == 'W':  # Неделя
            start_date = date - timedelta(days=date.weekday())  # Начало недели (понедельник)
            end_date = date
        elif range_type == 'M':  # Месяц
            start_date = date.replace(day=1)  # Первый день месяца
            end_date = date
        elif range_type == 'Y':  # Год
            start_date = date.replace(month=1, day=1)  # Первый день года
            end_date = date
        elif range_type == 'ALL':  # Все данные до указанной даты
            start_date = datetime.min  # Минимальная дата (1 января 1 года)
            end_date = date
        else:
            raise ValueError("Недопустимое значение range_type. Допустимые значения: 'W', 'M', 'Y', 'ALL'.")

        # Загружаем данные из Excel
        file_path = os.path.join(os.path.dirname(__file__), "..", "data", "operations.xlsx")
        transactions = load_data_from_excel(file_path)

        # Фильтруем данные по диапазону дат
        filtered_transactions = [
            transaction for transaction in transactions
            if start_date <= datetime.strptime(transaction["Дата операции"], "%d.%m.%Y %H:%M:%S") <= end_date
        ]

        # Анализ транзакций по категориям
        analysis_result = analyze_transactions(filtered_transactions)

        # Получение курсов валют
        api_key_currency = os.getenv('API_KEY_currency')
        base_currency = "RUB"
        target_currencies = ["USD", "EUR", "CNY"]  # Указываем только нужные валюты
        currency_rates = get_currency_rates(api_key_currency, base_currency, target_currencies)

        # Получение цен акций из S&P 500
        stock_symbols = ["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA", "GAZP"]  # Пример символов акций
        api_key_stock = os.getenv('API_KEY_stock_price')
        stock_prices = get_stock_price(stock_symbols, api_key_stock)

        # Формируем результат
        result = {
            'Диапазон дат': {
                'Начало': start_date.strftime("%Y-%m-%d"),
                'Конец': end_date.strftime("%Y-%m-%d")
            },
            'Результат анализа': analysis_result,
            'Курсы валют': currency_rates,
            'Биржевые цены': stock_prices
        }

        return json.dumps(result, indent=4, ensure_ascii=False)

    except FileNotFoundError as e:
        print(f"Ошибка: файл не найден. {e}")
        return "Ошибка: файл не найден."
    except ValueError as e:
        print(f"Ошибка: {e}")
        return f"Ошибка: {e}"
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        return "Произошла ошибка при выполнении функции."

# Запуск основной функции
if __name__ == "__main__":
    # Пример вызова функции
    filtered_transactions = main("2020-12-12", "M")
    print(filtered_transactions)
