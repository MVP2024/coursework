from typing import Optional, Tuple
import pandas as pd
from datetime import datetime, timedelta
from src.decorators import report_to_file

# Применяем декоратор
@report_to_file()
def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> Tuple[pd.DataFrame, float]:
    """
    Анализирует расходы по заданной категории за последние три месяца.

    :param transactions: DataFrame, содержащий транзакции с колонками 'Категория' и 'Дата операции'.
    :param category: Строка, представляющая категорию расходов для анализа.
    :param date: Строка в формате 'дд.мм.гггг', представляющая конечную дату анализа.
                 Если не указана, используется текущая дата.
    :return: Кортеж, содержащий:
             - DataFrame с отфильтрованными транзакциями по категории и дате.
             - Общая сумма расходов по категории, округленная до двух знаков после запятой.
    :raises ValueError: Если transactions не является DataFrame или если дата имеет неверный формат.
    """
    # Проверка типа данных для transactions
    if not isinstance(transactions, pd.DataFrame):
        raise ValueError("transactions должно быть DataFrame.")

    # Установка даты: если не указана, используем текущую дату
    if date is None:
        date = datetime.now()
    else:
        # Преобразуем строку в объект datetime
        date = datetime.strptime(date, '%d.%m.%Y')

    # Вычисляем дату три месяца назад
    three_months_ago = date - timedelta(days=90)

    # Фильтрация транзакций по категории и дате
    filtered_transactions = transactions[
        (transactions['Категория'] == category) &
        (pd.to_datetime(transactions['Дата операции'], dayfirst=True) >= three_months_ago) &
        (pd.to_datetime(transactions['Дата операции'], dayfirst=True) <= date)
    ].copy()  # Создаем явную копию DataFrame
    # для предотвращения потенциальных проблем с изменением данных в оригинальном DataFrame.

    # Подсчет общей суммы расходов по категории
    total_spending = round(abs(filtered_transactions['Сумма операции'].sum()), 2)

    return filtered_transactions, total_spending
