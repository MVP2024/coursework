import json
from datetime import datetime, timedelta
from typing import Optional

import pandas as pd

from src.decorators import report_to_file
from src.logger import setup_logger

# Настройка логгера для модуля reports
logger = setup_logger(__name__)


@report_to_file()
def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> str:
    """
    Рассчитывает траты по определенной категории за последние 3 месяца.

    Args:
        transactions (pd.DataFrame): DataFrame с транзакциями.
        category (str): Категория для фильтрации транзакций.
        date (Optional[str], optional): Дата для расчета, по умолчанию текущая дата.

    Returns:
        str: JSON-строка с транзакциями и общей суммой расходов.

    Raises:
        ValueError: Если transactions не является DataFrame.
    """
    # Проверка типа данных для transactions
    if not isinstance(transactions, pd.DataFrame):
        logger.error(f"Получен некорректный тип данных: {type(transactions)}")
        raise ValueError("transactions должно быть DataFrame.")

    # Установка даты: если не указана, используем текущую дату
    if date is None:
        current_date = datetime.now()
        logger.info("Используется текущая системная дата")
    else:
        # Преобразуем строку в объект datetime
        current_date = datetime.strptime(date, "%d.%m.%Y")
        logger.info(f"Используется указанная дата: {current_date}")

    # Вычисляем дату три месяца назад
    three_months_ago = current_date - timedelta(days=90)
    logger.debug(f"Период расчета: с {three_months_ago} по {current_date}")

    # Фильтрация транзакций по категории и дате
    filtered_transactions = transactions[
        (transactions["Категория"] == category)
        & (pd.to_datetime(transactions["Дата операции"], dayfirst=True) >= three_months_ago)
        & (pd.to_datetime(transactions["Дата операции"], dayfirst=True) <= current_date)
    ].copy()  # Создаем явную копию DataFrame

    # Подсчет общей суммы расходов по категории
    total_spending = round(abs(filtered_transactions["Сумма операции"].sum()), 2)
    logger.info(f"Общая сумма расходов по категории '{category}': {total_spending}")

    # Преобразуем DataFrame в список словарей
    transactions_list = filtered_transactions.to_dict(orient="records")
    logger.debug(f"Найдено транзакций: {len(transactions_list)}")

    # Возвращаем JSON-строку
    return json.dumps(
        {"transactions": transactions_list, "total_spending": total_spending}, ensure_ascii=False, indent=4
    )
