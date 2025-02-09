import json
import re


def find_personal_transfers(transactions):
    """
    Функция для поиска переводов физическим лицам в списке транзакций.

    :param transactions: Список транзакций.
    :return: JSON со всеми транзакциями, относящимися к переводам физическим лицам.
    """
    personal_transfers = []
    pattern = re.compile(r'^[А-ЯЁ][а-яё]+\s[А-ЯЁ]\.$')  # Регулярное выражение для поиска имени и первой буквы фамилии

    for transaction in transactions:
        if transaction['Категория'] == 'Переводы' and pattern.search(transaction['Описание']):
            personal_transfers.append(transaction)

    return json.dumps(personal_transfers, ensure_ascii=False, indent=4)
