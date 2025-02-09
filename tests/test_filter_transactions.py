import pytest
from datetime import datetime
from src.utils import filter_transactions

@pytest.mark.parametrize("date, range_type, expected_count", [
    ("2025-01-01", "M", 3),  # Январь 2025
    ("2025-01-15", "Y", 5),  # 2025 год
    ("2025-02-01", "D", 0),  # 1 февраля 2025
    ("2025-01-10", "M", 3),  # Только одна транзакция
    ("2025-02-10", "M", 2),  # Нет транзакций в феврале
])
def test_filter_transactions(sample_transactions, date, range_type, expected_count):
    result = filter_transactions(sample_transactions, date, range_type)
    assert len(result) == expected_count

def test_filter_transactions_invalid_date(sample_transactions):
    with pytest.raises(ValueError):
        filter_transactions(sample_transactions, "invalid-date", "M")
