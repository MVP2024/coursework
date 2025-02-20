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


def test_investment_bank_empty_transactions():
    month = "2025-02"
    transactions = []
    limit = 50
    result = investment_bank(month, transactions, limit)
    assert json.loads(result) == {"общая_сумма": 0.0, "округленные_транзакции": []}


def test_investment_bank_different_months():
    transactions = [
        {"Дата операции": "2025-01-15", "Сумма операции": 1000},
        {"Дата операции": "2025-02-15", "Сумма операции": 500},
        {"Дата операции": "2025-03-15", "Сумма операции": 750},
    ]
    month = "2025-02"
    limit = 50
    result = investment_bank(month, transactions, limit)
    data = json.loads(result)
    assert data["общая_сумма"] == 50.0


def test_investment_bank_transaction_less_than_limit():
    transactions = [{"Дата операции": "2025-02-15", "Сумма операции": 30}]
    month = "2025-02"
    limit = 50
    result = investment_bank(month, transactions, limit)
    data = json.loads(result)
    assert data["общая_сумма"] == 20.0
