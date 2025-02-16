import json

from src.services import investment_bank


def test_investment_bank():
    transactions = [
        {"Дата операции": "2025-02-01", "Сумма операции": 1712},
        {"Дата операции": "2025-02-15", "Сумма операции": 850},
        {"Дата операции": "2025-02-20", "Сумма операции": 1234},
        {"Дата операции": "2025-01-30", "Сумма операции": 499},
    ]
    month = "2025-02"
    limit = 50
    result = investment_bank(month, transactions, limit)

    assert json.loads(result)["общая_сумма"] == 104.0


def test_investment_bank_invalid_limit():
    transactions = [
        {"Дата операции": "2025-02-01", "Сумма операции": 1712},
    ]
    month = "2025-02"
    limit = -10  # Неверный порог
    result = investment_bank(month, transactions, limit)

    assert json.loads(result)["error"] == "Недопустимый порог округления."
