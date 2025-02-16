import logging
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any

from src.decorators import report_to_file
from src.utils import load_data_from_excel, analyze_transactions, logger



def get_greeting() -> str:
    """
    Определяет текущее время суток и возвращает подходящее приветствие.

    Возвращаемое значение:
        str: Приветствие, основанное на текущем времени суток.
             Возможные значения:
             - "Доброе утро" (с 5:00 до 11:59)
             - "Добрый день" (с 12:00 до 17:59)
             - "Добрый вечер" (с 18:00 до 22:59)
             - "Доброй ночи" (с 23:00 до 4:59)

    Примечания:
        Функция использует текущее время системы для определения времени суток.
    """
    current_time = datetime.now().time()  # Получаем текущее время
    hour = current_time.hour  # Извлекаем часы

    if 5 <= hour < 12:
        return "Доброе утро"
    elif 12 <= hour < 18:
        return "Добрый день"
    elif 18 <= hour < 23:
        return "Добрый вечер"
    else:
        return "Доброй ночи"


"""Функция для будущей фильтрации транзакция по диапазону дат"""
def filter_transactions(transactions: List[Dict[str, Any]], date: str, range_type: str) -> List[Dict[str, Any]]:
    logger.info("Начало фильтрации транзакций.")
    filtered_transactions = []
    date = datetime.strptime(date, "%Y-%m-%d")

    # Определяем начальную и конечную даты в зависимости от типа диапазона
    if range_type == 'M':
        start_date = date.replace(day=1)
        end_date = (start_date + timedelta(days=31)).replace(day=1) - timedelta(days=1)
    elif range_type == 'Y':
        start_date = date.replace(month=1, day=1)
        end_date = date.replace(month=12, day=31)
    else:
        start_date = date
        end_date = date

    # Фильтруем данные по диапазону дат
    filtered_transactions = [
        transaction for transaction in transactions
        if start_date <= datetime.strptime(transaction["Дата операции"], "%d.%m.%Y %H:%M:%S") <= end_date
    ]

    logger.info(f"Фильтрация завершена. Найдено {len(filtered_transactions)} транзакций.")
    return filtered_transactions
