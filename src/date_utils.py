from datetime import timedelta, datetime
from typing import List, Dict, Any

from src.utils import logger


def get_date_range(start_date, end_date):
    """Возвращает список дат в диапазоне от start_date до end_date."""
    delta = end_date - start_date
    return [start_date + timedelta(days=i) for i in range(delta.days + 1)]

def filter_transactions(transactions: List[Dict[str, Any]], date: str, range_type: str) -> List[Dict[str, Any]]:
    logger.info("Начало фильтрации транзакций.")
    filtered_transactions = []
    date = datetime.strptime(date, "%Y-%m-%d")

    # Определяем начальную и конечную даты в зависимости от типа диапазона
    if range_type == 'M':
        start_date = date.replace(day=1)  # Первое число месяца
        end_date = date  # Указанная дата
    elif range_type == 'Y':
        start_date = date.replace(month=1, day=1)  # Первое число года
        end_date = date  # Указанная дата
    else:
        start_date = date  # Для других типов диапазона
        end_date = date  # Указанная дата

    # Фильтруем данные по диапазону дат
    filtered_transactions = [
        transaction for transaction in transactions
        if start_date <= datetime.strptime(transaction["Дата операции"], "%d.%m.%Y %H:%M:%S") < end_date + timedelta(
            days=1)
    ]

    logger.info(f"Фильтрация завершена. Найдено {len(filtered_transactions)} транзакций.")
    return filtered_transactions
