from typing import Optional

import pandas as pd
import json
from datetime import datetime, timedelta

from src.decorators import report_to_file


# Применяем декоратор
@report_to_file()
def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> pd.DataFrame:
    if not isinstance(transactions, pd.DataFrame):
        raise ValueError("transactions должно быть DataFrame.")
    if date is None:
        date = datetime.now()
    else:
        date = datetime.strptime(date, '%d.%m.%Y')  # Преобразуем строку в datetime

    three_months_ago = date - timedelta(days=90)

    # Фильтрация транзакций по категории и дате
    filtered_transactions = transactions[
        (transactions['Категория'] == category) &
        (pd.to_datetime(transactions['Дата операции'], dayfirst=True) >= three_months_ago) &
        (pd.to_datetime(transactions['Дата операции'], dayfirst=True) <= date)
    ].copy()  # Создаем явную копию DataFrame

    # Подсчет общей суммы расходов по категории
    total_spending = round(abs(filtered_transactions['Сумма операции'].sum()), 2)


    return filtered_transactions, total_spending
