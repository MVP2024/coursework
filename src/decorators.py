import json
import os
import logging
from datetime import datetime
import functools

# Настройка логирования
logging.basicConfig(level=logging.INFO)

def report_to_file(filename=None):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Определяем директорию для сохранения
            output_directory = os.path.join(os.path.dirname(__file__), 'decorator_output')
            os.makedirs(output_directory, exist_ok=True)  # Создаем директорию, если она не существует

            # Генерация имени файла, если оно не указано
            if filename is None:
                current_date = datetime.now().strftime("%Y-%m-%d")
                function_name = func.__name__
                generated_filename = f"{current_date}_{function_name}.json"
            else:
                generated_filename = filename

            # Полный путь к файлу
            file_path = os.path.join(output_directory, generated_filename)

            # Вызов функции и получение результата
            result = func(*args, **kwargs)

            # Запись результата в JSON-файл
            try:
                # Преобразуем результат в формат, который можно сериализовать
                if isinstance(result, tuple):
                    result_to_save = (result[0].to_dict(orient='records'), result[1])  # Преобразуем DataFrame в список словарей
                else:
                    result_to_save = result

                with open(file_path, 'w', encoding='utf-8') as file:
                    json.dump(result_to_save, file, ensure_ascii=False, indent=4)
                logging.info(f"Результат функции '{func.__name__}' сохранен в файл: {file_path}")
            except (TypeError, ValueError) as e:
                logging.error(f"Ошибка при записи результата в файл: {e}")

            return result
        return wrapper
    return decorator
