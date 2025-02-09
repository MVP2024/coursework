import json
import os
import pandas as pd

from datetime import datetime, timedelta

from src.morning_day_night import get_greeting
from src.reports import spending_by_category
from src.services import find_personal_transfers
from src.utils import load_data_from_excel, analyze_transactions, get_currency_rates, get_stock_price, \
    filter_transactions

# from src.utils import get_date_range

""" Вывод всех функций. """
if __name__ == "__main__":


    """Функция, которая определяет время в данный момент и возвращает приветствие"""
    name = 'Bobr'
    print(f'{get_greeting()}, {name}!')


    """Вызов функции для считывания файла формата xlsx."""
file_path = os.path.join(os.path.dirname(__file__), "..", "data", "operations.xlsx")  # Путь к файлу в директории data
# print(load_data_from_excel(file_path))

transactions = load_data_from_excel(file_path)

# Переводим в DataFrame
transactions_df = pd.DataFrame(transactions)


"""Вызов функции для вывода категорий по тратам"""
result = analyze_transactions(transactions)
print(json.dumps(result, ensure_ascii=False, indent=4))


"""Функция для вывода курса валют"""
# Укажите валюты, которые хотите вывести
target_currencies = ["EUR", "USD"]  # Замените на нужные валюты


# Вызываем функцию для получения курсов относительно базовой валюты
rates = get_currency_rates(base_currency="RUB", target_currencies=target_currencies)

# Выводим курсы для указанных валют
print(rates)


"""Функция для вывода акций"""
# Список акций
symbols = ["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"]
# Получаем данные о ценах акций
stock_prices = get_stock_price(symbols)
# Выводим результат
print(stock_prices)


# # Выводим результат
# for stock in stock_prices:
#     print(f"Акция: {stock['stock']}, Цена: {stock['price']}")


"""Функция для поиска переводов физическим лицам"""
result = find_personal_transfers(transactions)
print(result)


"""Для отладки"""
# print(transactions_df.head())  # Вывод первых нескольких строк DataFrame
# print(transactions_df.columns)  # Вывод названий столбцов
#
# # Вывод первых нескольких строк и названий столбцов
# print("Первые несколько строк DataFrame:")
# print(transactions_df.head())
#
# print("Названия столбцов:")
# print(transactions_df.columns)
#
# # Проверка типов данных в DataFrame
# print("Типы данных в DataFrame:")
# print(transactions_df.dtypes)


"""Функция для получения трат по заданной категории за последние три месяца"""
# Изменяем вызов функции, чтобы получить и DataFrame, и итоговую сумму
filtered_transactions_df, total_spending = spending_by_category(transactions_df, 'Топливо', "15.08.2018")
# print(filtered_transactions_df)
# print(total_spending)
print(f"Отфильтрованные транзакции по категории 'Топливо':"
      f"\n{filtered_transactions_df.to_string(index=False)}, \n"
      f"Итоговая сумма за указанный период: \n{total_spending}.")


"""Функция для получения данных по указанному диапазону дат"""
print(filter_transactions(transactions, "2020-10-10", "M"))