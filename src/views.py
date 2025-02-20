import json
import os
from datetime import datetime, timedelta

from src.logger import setup_logger
from src.utils import analyze_transactions, get_currency_rates, get_stock_price, load_data_from_excel

# Настройка логгера
logger = setup_logger(__name__)


def events(date_str: str, range_type: str = "M") -> str:
    """
    Основная функция для анализа транзакций, получения курсов валют и биржевых цен.
    :param date_str: Дата в формате "YYYY-MM-DD".
    :param range_type: Тип диапазона: 'W' (неделя), 'M' (месяц), 'Y' (год), 'ALL' (все данные).
    :return: JSON-строка с результатами анализа.
    """
    try:
        logger.info("Преобразуем строку с датой в объект datetime.")
        date = datetime.strptime(date_str, "%Y-%m-%d")

        logger.info("Определяем начальную и конечную даты в зависимости от range_type.")
        if range_type == "W":
            start_date = date - timedelta(days=date.weekday())
            end_date = date
        elif range_type == "M":
            start_date = date.replace(day=1)
            end_date = date
        elif range_type == "Y":
            start_date = date.replace(month=1, day=1)
            end_date = date
        elif range_type == "ALL":
            start_date = datetime.min
            end_date = date
        else:
            raise ValueError("Недопустимое значение range_type. Допустимые значения: 'W', 'M', 'Y', 'ALL'.")

        logger.info("Загружаем данные из Excel.")
        file_path = os.path.join(os.path.dirname(__file__), "..", "data", "operations.xlsx")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Файл не найден: {file_path}")

        transactions = load_data_from_excel(file_path)

        if not transactions:
            raise ValueError("Список транзакций пуст.")

        required_keys = ["Дата операции", "Сумма операции"]
        for transaction in transactions:
            if not all(key in transaction for key in required_keys):
                raise ValueError(f"Транзакция должна содержать ключи: {required_keys}")

        logger.info("Фильтруем данные по диапазону дат.")
        filtered_transactions = [
            transaction
            for transaction in transactions
            if start_date <= datetime.strptime(transaction["Дата операции"], "%d.%m.%Y %H:%M:%S") <= end_date
        ]

        logger.info("Анализируем транзакции по категориям.")
        analysis_result = analyze_transactions(filtered_transactions)

        logger.info("Получаем курсы валют.")
        api_key_currency = os.getenv("API_KEY_currency")
        if not api_key_currency:
            raise ValueError("API_KEY для получения курсов валют не установлен.")
        base_currency = "RUB"
        target_currencies = ["USD", "EUR", "CNY"]
        currency_rates = get_currency_rates(api_key_currency, base_currency, target_currencies)

        logger.info("Получаем цены акций из S&P 500.")
        stock_symbols = ["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA", "GAZP"]
        api_key_stock = os.getenv("API_KEY_stock_price")
        if not api_key_stock:
            raise ValueError("API_KEY для получения цен акций не установлен.")
        stock_prices = get_stock_price(stock_symbols, api_key_stock)

        logger.info("Формируем результат.")
        result = {
            "Диапазон дат": {"Начало": start_date.strftime("%Y-%m-%d"), "Конец": end_date.strftime("%Y-%m-%d")},
            "Результат анализа": analysis_result,
            "Курсы валют": currency_rates,
            "Биржевые цены": stock_prices,
        }

        # Сохраняем только необходимые данные в user_settings.json
        settings_to_save = {"Курсы валют": currency_rates, "Биржевые цены": stock_prices}

        logger.info("Записываем результат выполнения функции в user_settings.json.")
        settings_file_path = os.path.join(os.path.dirname(__file__), "..", "user_settings.json")
        settings = {}

        try:
            with open(settings_file_path, "r", encoding="utf-8") as settings_file:
                settings = json.load(settings_file)
        except (FileNotFoundError, json.JSONDecodeError):
            settings = {}

        settings["result"] = settings_to_save  # Сохраняем только нужные данные

        with open(settings_file_path, "w", encoding="utf-8") as settings_file:
            json.dump(settings, settings_file, indent=4, ensure_ascii=False)

        logger.info("Результат функции успешно сохранен.")
        return json.dumps(result, ensure_ascii=False, indent=4)  # Возвращаем результат в формате JSON

    except Exception as e:
        logger.error(f"Ошибка в функции main: {e}")
        raise  # Прерываем выполнение функции и передаем исключение выше


# Запуск основной функции
# pragma: no cover
if __name__ == "__main__":
    filtered_transactions = events("2020-12-20", "M")
    print(filtered_transactions)
