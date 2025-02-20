import pytest
from unittest.mock import patch
from src.morning_day_night import get_greeting


@pytest.mark.parametrize("mock_hour, expected_greeting", [
	(6, "Доброе утро"),  # Утро (5:00 - 11:59)
	(11, "Доброе утро"),
	(12, "Добрый день"),  # День (12:00 - 17:59)
	(16, "Добрый день"),
	(17, "Добрый день"),
	(18, "Добрый вечер"),  # Вечер (18:00 - 22:59)
	(20, "Добрый вечер"),
	(22, "Добрый вечер"),
	(23, "Доброй ночи"),  # Ночь (23:00 - 4:59)
	(0, "Доброй ночи"),
	(4, "Доброй ночи")
])
def test_get_greeting_different_times(mock_hour, expected_greeting):
	"""
	Тест проверяет корректность приветствия
	для различных временных диапазонов.
	"""
	with patch('src.morning_day_night.datetime') as mock_datetime:
		mock_datetime.now.return_value.time.return_value.hour = mock_hour
		assert get_greeting() == expected_greeting


def test_get_greeting_edge_cases():
	"""
	Тест проверяет граничные значения времени.
	"""
	test_cases = [
		(5, "Доброе утро"),  # Нижняя граница утра
		(11, "Доброе утро"),  # Верхняя граница утра
		(12, "Добрый день"),  # Нижняя граница дня
		(17, "Добрый день"),  # Верхняя граница дня
		(18, "Добрый вечер"),  # Нижняя граница вечера
		(22, "Добрый вечер"),  # Верхняя граница вечера
		(23, "Доброй ночи"),  # Нижняя граница ночи
		(4, "Доброй ночи")  # Верхняя граница ночи
	]

	for hour, expected in test_cases:
		with patch('src.morning_day_night.datetime') as mock_datetime:
			mock_datetime.now.return_value.time.return_value.hour = hour
			assert get_greeting() == expected


def test_get_greeting_type():
	"""
	Проверяет, что возвращается строка.
	"""
	greeting = get_greeting()
	assert isinstance(greeting, str)
	assert len(greeting) > 0


def test_get_greeting_consistent_output():
	"""
	Проверяет, что функция возвращает один из четырех вариантов приветствия.
	"""
	valid_greetings = [
		"Доброе утро",
		"Добрый день",
		"Добрый вечер",
		"Доброй ночи"
	]

	with patch('src.morning_day_night.datetime') as mock_datetime:
		for hour in range(24):
			mock_datetime.now.return_value.time.return_value.hour = hour
			greeting = get_greeting()
			assert greeting in valid_greetings
