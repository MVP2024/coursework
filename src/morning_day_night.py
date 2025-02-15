import logging
import os
from datetime import datetime, timedelta

from src.decorators import report_to_file
from src.utils import load_data_from_excel, analyze_transactions


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
