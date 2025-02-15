from datetime import timedelta


def get_date_range(start_date, end_date):
    """Возвращает список дат в диапазоне от start_date до end_date."""
    delta = end_date - start_date
    return [start_date + timedelta(days=i) for i in range(delta.days + 1)]
