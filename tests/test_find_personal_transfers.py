import pytest
import json

from src.services import find_personal_transfers


def test_find_personal_transfers_success():
	transactions = [
		{
			"Категория": "Переводы",
			"Описание": "Иванов И.И.",
			"Сумма": 1000
		},
		{
			"Категория": "Переводы",
			"Описание": "Петров П.П.",
			"Сумма": 2000
		},
		{
			"Категория": "Другое",
			"Описание": "Магазин",
			"Сумма": 500
		}
	]

	result = json.loads(find_personal_transfers(transactions))
	assert len(result) == 0
	assert all(transaction["Описание"] in ["Иванов И.И.", "Петров П.П."] for transaction in result)


def test_find_personal_transfers_no_matches():
	transactions = [
		{
			"Категория": "Другое",
			"Описание": "Магазин",
			"Сумма": 500
		},
		{
			"Категория": "Перевод",
			"Описание": "Неверный формат",
			"Сумма": 1000
		}
	]

	result = json.loads(find_personal_transfers(transactions))
	assert len(result) == 0


def test_find_personal_transfers_invalid_name_format():
	transactions = [
		{
			"Категория": "Переводы",
			"Описание": "иванов И.И.",
			"Сумма": 1000
		},
		{
			"Категория": "Переводы",
			"Описание": "ПЕТРОВ П.П.",
			"Сумма": 2000
		}
	]

	result = json.loads(find_personal_transfers(transactions))
	assert len(result) == 0
