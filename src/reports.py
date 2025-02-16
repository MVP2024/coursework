from datetime import datetime, timedelta
from typing import Optional, Tuple

import pandas as pd

from src.decorators import report_to_file


# Применяем декоратор
@report_to_file()
def spending_by_category(
    transactions: pd.DataFrame, category: str, date: Optional[str] = None
) -> Tuple[pd.DataFrame, float]:
    # Проверка типа данных для transactions
    if not isinstance(transactions, pd.DataFrame):
        raise ValueError("transactions должно быть DataFrame.")

    # Установка даты: если не указана, используем текущую дату
    if date is None:
        current_date = datetime.now()
    else:
        # Преобразуем строку в объект datetime
        current_date = datetime.strptime(date, "%d.%m.%Y")

    # Вычисляем дату три месяца назад
    three_months_ago = current_date - timedelta(days=90)

    # Фильтрация транзакций по категории и дате
    filtered_transactions = transactions[
        (transactions["Категория"] == category)
        & (pd.to_datetime(transactions["Дата операции"], dayfirst=True) >= three_months_ago)
        & (pd.to_datetime(transactions["Дата операции"], dayfirst=True) <= current_date)
    ].copy()  # Создаем явную копию DataFrame

    # Подсчет общей суммы расходов по категории
    total_spending = round(abs(filtered_transactions["Сумма операции"].sum()), 2)

    return filtered_transactions, total_spending
