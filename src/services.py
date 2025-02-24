import json
import re
from typing import Any, Dict, List

from src.decorators import report_to_file
from src.logger import setup_logger

# Настройка логгера для модуля services
logger = setup_logger(__name__)


@report_to_file()
def find_personal_transfers(transactions):
    """
    Функция для поиска переводов физическим лицам в списке транзакций.

    :param transactions: Список транзакций.
    :return: JSON со всеми транзакциями, относящимися к переводам физическим лицам.
    """
    personal_transfers = []
    pattern = re.compile(r"^[А-ЯЁ][а-яё]+\s[А-ЯЁ]\.$")  # Регулярное выражение для поиска имени и первой буквы фамилии

    logger.info("Начинаем поиск переводов физическим лицам.")

    for transaction in transactions:
        if transaction["Категория"] == "Переводы" and pattern.search(transaction["Описание"]):
            personal_transfers.append(transaction)
            logger.debug(f"Найдена транзакция: {transaction}")

    logger.info(f"Поиск завершен. Найдено {len(personal_transfers)} переводов физическим лицам.")
    return json.dumps(personal_transfers, ensure_ascii=False, indent=4)


@report_to_file()
def investment_bank(month: str, transactions: List[Dict[str, Any]], limit: int) -> str:
    """
    Рассчитывает сумму, отложенную в «Инвесткопилку» за указанный месяц и возвращает результат в формате JSON.

    :param month: Месяц в формате 'YYYY-MM'.
    :param transactions: Список транзакций, где каждая транзакция представлена в виде словаря.
    :param limit: Порог округления (положительное целое число).
    :return: JSON-строка с общей суммой, отложенной в «Инвесткопилку», и деталями транзакций.
    """
    # Проверка на допустимость порога округления
    if limit <= 0:
        logger.error("Порог округления должен быть положительным целым числом.")
        return json.dumps({"error": "Недопустимый порог округления."})

    total_savings = 0.0  # Инициализация переменной для хранения общей суммы сбережений
    rounded_expenses = []  # Список для хранения деталей округленных транзакций

    for transaction in transactions:
        transaction_date = transaction["Дата операции"]  # Получаем дату транзакции
        transaction_amount = transaction["Сумма операции"]  # Получаем сумму транзакции

        # Проверяем, попадает ли транзакция в указанный месяц
        if transaction_date.startswith(month):
            # Округляем сумму транзакции до ближайшего значения, кратного limit
            rounded_value = ((transaction_amount // limit) + 1) * limit
            savings = rounded_value - transaction_amount  # Вычисляем сбережения от округления
            total_savings += savings  # Добавляем к общей сумме сбережений

            # Добавляем детали округленной транзакции в список
            rounded_expenses.append(
                {
                    "Дата операции": transaction_date,
                    "Сумма транзакции": transaction_amount,
                    "Округленная сумма": rounded_value,
                    "Сбережения": savings,
                }
            )

    # Логируем общую сумму сбережений
    logger.info(f"Общая сумма, отложенная в «Инвесткопилку» за {month}: {total_savings} ₽.")

    # Возвращаем результат в формате JSON с русскими ключами
    return json.dumps(
        {"общая_сумма": total_savings, "округленные_транзакции": rounded_expenses}, ensure_ascii=False, indent=4
    )
