from datetime import datetime


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


# def filter_transactions(transactions: List[Dict[str, Any]], date_str: str, range_type: str) -> List[Dict[str, Any]]:
#     """
#     Фильтрует транзакции по заданному диапазону дат.
#
#     Параметры:
#         transactions (List[Dict[str, Any]]): Список транзакций, где каждая транзакция представлена в виде словаря.
#         date_str (str): Дата в формате 'YYYY-MM-DD', до которой будут фильтроваться транзакции.
#         range_type (str): Тип диапазона для фильтрации. Допустимые значения:
#             - 'W': неделя (от понедельника до указанной даты)
#             - 'M': месяц (от 1 числа месяца до указанной даты)
#             - 'Y': год (от 1 января года до указанной даты)
#             - 'ALL': все транзакции до указанной даты
#
#     Возвращает:
#         List[Dict[str, Any]]: Список отфильтрованных транзакций, соответствующих заданному диапазону дат.
#     """
#     logger.info("Преобразуем строку с датой в объект datetime.")
#     date = datetime.strptime(date_str, "%Y-%m-%d")
#
#     logger.info("Определяем начальную и конечную даты в зависимости от range_type.")
#     if range_type == "W":
#         # Начальная дата - первый день недели (понедельник)
#         start_date = date - timedelta(days=date.weekday())
#         end_date = date  # Конечная дата - указанная дата
#     elif range_type == "M":
#         # Начальная дата - первое число месяца
#         start_date = date.replace(day=1)
#         end_date = date  # Конечная дата - указанная дата
#     elif range_type == "Y":
#         # Начальная дата - первое число года
#         start_date = date.replace(month=1, day=1)
#         end_date = date  # Конечная дата - указанная дата
#     elif range_type == "ALL":
#         # Начальная дата - минимально возможная дата
#         start_date = datetime.min
#         end_date = date  # Конечная дата - указанная дата
#     else:
#         raise ValueError("Недопустимое значение range_type. Допустимые значения: 'W', 'M', 'Y', 'ALL'.")
#
#     # Фильтруем данные по диапазону дат
#     filtered_transactions = [
#         transaction
#         for transaction in transactions
#         if start_date <= datetime.strptime(transaction["Дата операции"], "%d.%m.%Y %H:%M:%S") <= end_date
#     ]
#
#     logger.info(f"Фильтрация завершена. Найдено {len(filtered_transactions)} транзакций.")
#
#     return filtered_transactions
#
#
# def get_date_range(start_date, end_date):
#     """Возвращает список дат в диапазоне от start_date до end_date."""
#     delta = end_date - start_date
#     return [start_date + timedelta(days=i) for i in range(delta.days + 1)]
