import pytest
import pandas as pd
from src.utils import load_data_from_excel


# Тест: Успешная загрузка данных из Excel
def test_load_data_from_excel_success(tmpdir):
    # Создаем временный Excel-файл
    file_path = tmpdir.join("test_data.xlsx")
    data = {
        "A": [1, 2, 3],  # Простое название столбца
        "B": ["X", "Y", "Z"]  # Простое название столбца
    }
    df = pd.DataFrame(data)
    df.to_excel(file_path, index=False)

    # Вызываем функцию и проверяем результат
    result = load_data_from_excel(file_path)
    expected = [
        {"A": 1, "B": "X"},
        {"A": 2, "B": "Y"},
        {"A": 3, "B": "Z"}
    ]
    assert result == expected


# Тест: Файл не найден
def test_load_data_from_excel_file_not_found():
    # Пытаемся загрузить несуществующий файл
    with pytest.raises(FileNotFoundError):
        load_data_from_excel("non_existent_file.xlsx")


# Тест: Замена NaN на 0
def test_load_data_from_excel_replace_nan(tmpdir):
    # Создаем временный Excel-файл с NaN
    file_path = tmpdir.join("test_data.xlsx")
    data = {
        "A": [1, None, 3],  # Простое название столбца
        "B": ["X", "Y", "Z"]  # Простое название столбца
    }
    df = pd.DataFrame(data)
    df.to_excel(file_path, index=False)

    # Вызываем функцию и проверяем, что NaN заменены на 0
    result = load_data_from_excel(file_path)
    expected = [
        {"A": 1, "B": "X"},
        {"A": 0, "B": "Y"},
        {"A": 3, "B": "Z"}
    ]
    assert result == expected
