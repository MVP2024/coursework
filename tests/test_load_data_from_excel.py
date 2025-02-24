from unittest.mock import patch

import pandas as pd
import pytest

from src.utils import load_data_from_excel


def test_load_data_from_excel_success():
    """Успешная загрузка данных из Excel-файла"""
    test_data = {"Категория": ["A", "B", "C"], "Сумма операции": [1, 2, 3], "Дополнительный_столбец": ["X", "Y", "Z"]}
    mock_dataframe = pd.DataFrame(test_data)

    with patch("os.path.exists", return_value=True), patch("pandas.read_excel", return_value=mock_dataframe):
        result = load_data_from_excel("test_file.xlsx")
        expected = [
            {"Категория": "A", "Сумма операции": 1, "Дополнительный_столбец": "X"},
            {"Категория": "B", "Сумма операции": 2, "Дополнительный_столбец": "Y"},
            {"Категория": "C", "Сумма операции": 3, "Дополнительный_столбец": "Z"},
        ]
        assert result == expected


def test_mock_load_data_from_excel(mock_load_data_from_excel):
    """Проверка корректности мокирования pd.read_excel"""
    assert mock_load_data_from_excel is not None


def test_load_data_from_excel_file_not_found():
    """Обработка ошибки при отсутствии файла"""
    with patch("os.path.exists", return_value=False):
        with pytest.raises(
            ValueError, match="Ошибка при сохранении результата: Файл не найден: non_existent_file.xlsx"
        ):
            load_data_from_excel("non_existent_file.xlsx")


def test_load_data_from_excel_empty_file():
    """Загрузка пустого Excel-файла"""
    mock_dataframe = pd.DataFrame()

    with patch("os.path.exists", return_value=True), patch("pandas.read_excel", return_value=mock_dataframe):
        result = load_data_from_excel("empty_file.xlsx")
        assert result == []


def test_load_data_from_excel_replace_nan():
    """Замена значений NaN на 0"""
    test_data = {"Категория": [None, "Транспорт", "Развлечения"], "Сумма операции": [100, None, 20]}
    mock_dataframe = pd.DataFrame(test_data)

    with patch("os.path.exists", return_value=True), patch("pandas.read_excel", return_value=mock_dataframe):
        result = load_data_from_excel("test_file.xlsx")
        expected = [
            {"Категория": "Без категории", "Сумма операции": 100},
            {"Категория": "Транспорт", "Сумма операции": 0},
            {"Категория": "Развлечения", "Сумма операции": 20},
        ]
        assert result == expected


def test_load_data_from_excel_permission_error():
    """Обработка ошибки доступа к файлу"""
    with patch("os.path.exists", return_value=True), patch("pandas.read_excel") as mock_read_excel:
        mock_read_excel.side_effect = PermissionError("Нет доступа к файлу")

        with pytest.raises(ValueError, match="Ошибка при сохранении результата: Нет доступа к файлу"):
            load_data_from_excel("protected_file.xlsx")


def test_load_data_from_excel_read_error():
    """Обработка общей ошибки чтения файла"""
    with patch("os.path.exists", return_value=True), patch("pandas.read_excel") as mock_read_excel:
        mock_read_excel.side_effect = Exception("Ошибка чтения файла")

        with pytest.raises(Exception, match="Ошибка чтения файла"):
            load_data_from_excel("some_file.xlsx")


def test_load_data_from_excel_invalid_file_extension():
    """Проверка обработки файлов с некорректным расширением"""
    with patch("os.path.exists", return_value=True):
        with pytest.raises(ValueError, match="Поддерживаются только файлы Excel"):
            load_data_from_excel("test_file.txt")


def test_load_data_from_excel_missing_required_columns():
    """Проверка обработки файла без обязательных столбцов"""
    mock_dataframe = pd.DataFrame({"Неправильный_столбец": [1, 2, 3]})

    with patch("os.path.exists", return_value=True), patch("pandas.read_excel", return_value=mock_dataframe):
        with pytest.raises(ValueError, match="Отсутствуют обязательные столбцы"):
            load_data_from_excel("test_file.xlsx")


def test_load_data_from_excel_default_category_for_nan():
    """Проверка замены NaN в столбце Категория"""
    test_data = {"Категория": [None, "Транспорт", "Развлечения"], "Сумма операции": [100, 50, 20]}
    mock_dataframe = pd.DataFrame(test_data)

    with patch("os.path.exists", return_value=True), patch("pandas.read_excel", return_value=mock_dataframe):
        result = load_data_from_excel("test_file.xlsx")

        assert result[0]["Категория"] == "Без категории"
        assert result[1]["Категория"] == "Транспорт"
        assert result[2]["Категория"] == "Развлечения"


def test_load_data_from_excel_columns_as_strings():
    """Проверка преобразования названий столбцов в строки"""
    test_data = {"Категория": ["Еда", "Транспорт"], "Сумма операции": [100, 50]}
    mock_dataframe = pd.DataFrame(test_data)

    with patch("os.path.exists", return_value=True), patch("pandas.read_excel", return_value=mock_dataframe):
        result = load_data_from_excel("test_file.xlsx")

        assert list(result[0].keys()) == ["Категория", "Сумма операции"]
        assert result[0]["Категория"] == "Еда"
        assert result[0]["Сумма операции"] == 100


def test_load_data_from_excel_with_extra_columns():
    """Проверка загрузки Excel-файла с дополнительными столбцами"""
    test_data = {
        "Категория": ["Еда", "Транспорт"],
        "Сумма операции": [100, 50],
        "Дополнительный_столбец1": ["X", "Y"],
        "Дополнительный_столбец2": [10, 20],
    }
    mock_dataframe = pd.DataFrame(test_data)

    with patch("os.path.exists", return_value=True), patch("pandas.read_excel", return_value=mock_dataframe):
        result = load_data_from_excel("test_file.xlsx")

        assert len(result) == 2
        assert all("Дополнительный_столбец1" in transaction for transaction in result)
        assert all("Дополнительный_столбец2" in transaction for transaction in result)
