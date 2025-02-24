import pytest

from src.utils import analyze_transactions


@pytest.mark.parametrize(
    "input_data, expected",
    [
        (
            [],
            {
                "Расходы": {"Общая сумма": 0, "Основные": []},
                "Доходы": {
                    "Общий доход": 0,
                    "Категории": [
                        {"Категория": "Пополнения", "Сумма": 0},
                        {"Категория": "Бонусы (включая кэшбэк)", "Сумма": 0},
                    ],
                },
            },
        ),
        # Другие параметризованные тесты остаются без изменений
    ],
)
def test_analyze_transactions(input_data, expected):
    result = analyze_transactions(input_data)
    assert result == expected


def test_analyze_transactions_mixed(transactions_data):
    result = analyze_transactions(transactions_data)
    expected = {
        "Расходы": {
            "Общая сумма": 150,
            "Основные": [
                {"Категория": "Еда", "Сумма": 100},
                {"Категория": "Транспорт", "Сумма": 50},
            ],
        },
        "Доходы": {
            "Общий доход": 1250,
            "Категории": [
                {"Категория": "Пополнения", "Сумма": 0},
                {"Категория": "Бонусы (включая кэшбэк)", "Сумма": 50},
            ],
        },
    }
    assert result == expected


# Тесты с разными типами
def test_analyze_transactions_with_mixed_data():
    transactions = [
        {"Категория": "Еда", "Сумма операции": -100},
        {"Категория": "Транспорт", "Сумма операции": "-50"},
        {"Категория": "Зарплата", "Сумма операции": 1000},
        {"Категория": "Бонусы (включая кэшбэк)", "Сумма операции": 50},
        {"Категория": "Инвестиции", "Сумма операции": None},
    ]

    result = analyze_transactions(transactions)

    assert result["Расходы"]["Общая сумма"] == 150
    assert result["Доходы"]["Общий доход"] == 1050
    assert any(cat["Категория"] == "Еда" for cat in result["Расходы"]["Основные"])


# тесты с разными типами обработки
def test_analyze_transactions_edge_cases():
    transactions = [
        {"Категория": "Еда", "Сумма операции": 0},
        {"Сумма операции": -100},
        {"Категория": "Транспорт"},
        {"Категория": "Инвестиции", "Сумма операции": "invalid"},
    ]

    result = analyze_transactions(transactions)

    assert result["Расходы"]["Общая сумма"] == 0
    assert result["Расходы"]["Основные"] == []


def test_analyze_transactions_large_amounts():
    """Проверка обработки транзакций с очень большими суммами"""
    transactions = [
        {"Категория": "Крупная покупка", "Сумма операции": -1000000},
        {"Категория": "Большой доход", "Сумма операции": 5000000},
    ]

    result = analyze_transactions(transactions)

    assert result["Расходы"]["Общая сумма"] == 1000000
    assert result["Доходы"]["Общий доход"] == 5000000


def test_analyze_transactions_negative_income():
    """Проверка обработки транзакций с отрицательным доходом"""
    transactions = [{"Категория": "Возврат", "Сумма операции": -500}, {"Категория": "Штраф", "Сумма операции": -200}]

    result = analyze_transactions(transactions)

    assert result["Расходы"]["Общая сумма"] == 700
    assert result["Доходы"]["Общий доход"] == 0


def test_analyze_transactions_mixed_data_types():
    """Проверка обработки транзакций со смешанными типами данных"""
    transactions = [
        {"Категория": "Еда", "Сумма операции": "-100"},
        {"Категория": "Зарплата", "Сумма операции": 1000.0},
        {"Категория": "Бонусы", "Сумма операции": "50"},
    ]

    result = analyze_transactions(transactions)

    assert result["Расходы"]["Общая сумма"] == 100
    assert result["Доходы"]["Общий доход"] == 1050


def test_analyze_transactions_missing_category_or_amount():
    transactions = [
        {"Сумма операции": 100},  # Нет категории
        {"Категория": "Еда"},  # Нет суммы
        {"Категория": "Зарплата", "Сумма операции": 1000},
    ]

    result = analyze_transactions(transactions)

    assert result["Доходы"]["Общий доход"] == 1000
    assert result["Расходы"]["Общая сумма"] == 0


def test_analyze_transactions_invalid_amount_format():
    transactions = [
        {"Категория": "Еда", "Сумма операции": "invalid"},
        {"Категория": "Зарплата", "Сумма операции": [100]},
        {"Категория": "Транспорт", "Сумма операции": 500},
    ]

    result = analyze_transactions(transactions)

    assert result["Доходы"]["Общий доход"] == 500
    assert result["Расходы"]["Общая сумма"] == 0


def test_analyze_transactions_many_categories():
    transactions = [
        {"Категория": "Категория1", "Сумма операции": -100},
        {"Категория": "Категория2", "Сумма операции": -200},
        {"Категория": "Категория3", "Сумма операции": -300},
        {"Категория": "Категория4", "Сумма операции": -400},
        {"Категория": "Категория5", "Сумма операции": -500},
        {"Категория": "Категория6", "Сумма операции": -600},
        {"Категория": "Категория7", "Сумма операции": -700},
        {"Категория": "Категория8", "Сумма операции": -800},
        {"Категория": "Категория9", "Сумма операции": -900},
    ]

    result = analyze_transactions(transactions)

    # Проверяем количество основных категорий
    assert len(result["Расходы"]["Основные"]) == 8  # 7 категорий + "Остальные"

    # Проверяем первые 7 категорий по убыванию
    expected_categories = [
        "Категория9",
        "Категория8",
        "Категория7",
        "Категория6",
        "Категория5",
        "Категория4",
        "Категория3",
    ]
    for i, category_data in enumerate(result["Расходы"]["Основные"][:7]):
        assert category_data["Категория"] == expected_categories[i]

    # Проверяем категорию "Остальные"
    assert result["Расходы"]["Основные"][-1]["Категория"] == "Остальные"
    assert result["Расходы"]["Основные"][-1]["Сумма"] == 300  # 100 + 200

    # Проверяем общую сумму расходов
    assert result["Расходы"]["Общая сумма"] == 4500.0


def test_analyze_transactions_type_conversion_errors():
    transactions = [
        {"Категория": "Зарплата", "Сумма операции": "abc"},  # Строка, которую нельзя преобразовать в число
        {"Категория": "Транспорт", "Сумма операции": None},  # None
        {"Категория": "Еда", "Сумма операции": [100]},  # Список
        {"Категория": "Развлечения", "Сумма операции": {"amount": 50}},  # Словарь
        {"Категория": "Спорт", "Сумма операции": object()},  # Объект
    ]

    result = analyze_transactions(transactions)

    assert result["Расходы"]["Общая сумма"] == 0
    assert result["Доходы"]["Общий доход"] == 0
    assert result["Расходы"]["Основные"] == []
