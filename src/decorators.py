import json
import os
import logging
from datetime import datetime
import functools
from typing import Callable, Any, Optional

# Настройка логирования
logging.basicConfig(level=logging.INFO)


def report_to_file(filename: Optional[str] = None) -> Callable:
    """Декоратор для сохранения результата функции в JSON-файл.

    Args:
        filename (Optional[str]): Имя файла для сохранения результата.
                                  Если не указано, будет сгенерировано автоматически.

    Returns:
        Callable: Обернутая функция, которая сохраняет результат в файл.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
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

            try:
                # Вызов функции и получение результата
                result = func(*args, **kwargs)

                # Запись результата в JSON-файл
                if isinstance(result, tuple):
                    # Преобразуем DataFrame в список словарей
                    result_to_save = (result[0].to_dict(orient='records'), result[1])
                else:
                    result_to_save = result

                with open(file_path, 'w', encoding='utf-8') as file:
                    json.dump(result_to_save, file, ensure_ascii=False, indent=4)
                logging.info(f"Результат функции '{func.__name__}' сохранен в файл: {file_path}")

            except (TypeError, ValueError) as e:
                logging.error(f"Ошибка при записи результата в файл: {e}")
                raise  # Передаем исключение дальше

            return result
        return wrapper
    return decorator
