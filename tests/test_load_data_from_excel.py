import pytest
from src.utils import load_data_from_excel


def test_load_data_from_excel_success(mock_load_data_from_excel, sample_excel_data):
    # Настраиваем мок, чтобы он возвращал пример данных
    mock_load_data_from_excel.return_value = sample_excel_data

    # Вызываем функцию
    result = load_data_from_excel('fake_path.xlsx')

    # Проверяем, что результат соответствует ожидаемому
    expected_result = sample_excel_data.to_dict(orient='records')
    assert result == expected_result
    mock_load_data_from_excel.assert_called_once_with('fake_path.xlsx', na_filter=True)

def test_load_data_from_excel_file_not_found(mock_load_data_from_excel):
    # Настраиваем мок, чтобы он вызывал исключение при попытке чтения файла
    mock_load_data_from_excel.side_effect = FileNotFoundError("Файл не найден")

    # Вызываем функцию и проверяем, что она возвращает пустой список
    result = load_data_from_excel('fake_path.xlsx')
    assert result == []
    mock_load_data_from_excel.assert_called_once_with('fake_path.xlsx', na_filter=True)

def test_load_data_from_excel_other_exception(mock_load_data_from_excel):
    # Настраиваем мок, чтобы он вызывал общее исключение
    mock_load_data_from_excel.side_effect = Exception("Ошибка чтения")

    # Вызываем функцию и проверяем, что она возвращает пустой список
    result = load_data_from_excel('fake_path.xlsx')
    assert result == []
    mock_load_data_from_excel.assert_called_once_with('fake_path.xlsx', na_filter=True)