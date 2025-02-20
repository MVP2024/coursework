import functools
import json
import os
from datetime import datetime
from typing import Any, Callable, Optional

from src.logger import setup_logger

# Создаем логгер для этого модуля
logger = setup_logger(__name__)


def report_to_file(filename: Optional[str] = None) -> Callable:
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            output_directory = os.path.join(os.path.dirname(__file__), "decorator_output")
            os.makedirs(output_directory, exist_ok=True)

            if filename is None:
                current_date = datetime.now().strftime("%Y-%m-%d")
                function_name = func.__name__
                generated_filename = f"{current_date}_{function_name}.json"
            else:
                generated_filename = filename

            file_path = os.path.join(output_directory, generated_filename)

            try:
                result = func(*args, **kwargs)

                # Проверяем, является ли результат кортежем с DataFrame
                if isinstance(result, tuple) and len(result) == 2:
                    # Преобразуем DataFrame в список словарей
                    result = (result[0].to_dict(orient='records'), result[1])

                with open(file_path, "w", encoding="utf-8") as file:
                    json.dump(result, file, ensure_ascii=False, indent=4)

                return result

            except Exception as e:
                # Логируем оригинальное исключение
                logger.error(f"Ошибка при выполнении функции: {e}")
                # Перебрасываем исключение с префиксом для совместимости с тестами
                raise ValueError(f"Ошибка при сохранении результата: {e}")

        return wrapper

    return decorator
