import os
import json
from datetime import datetime, timedelta

from .db_utils import insert_stock_history

def save_stock_history(data, data_dir="Parser/data", base_filename="output", keep_days=7):
    """
    Сохраняет остатки товаров в файл с текущей датой.
    Удаляет файлы старше keep_days дней.
    """
    os.makedirs(data_dir, exist_ok=True)

    # Имя файла с датой
    today_str = datetime.now().strftime("%Y-%m-%d")
    filename = f"{base_filename}_{today_str}.json"
    file_path = os.path.join(data_dir, filename)

    # Сохраняем данные в файл
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    # Также сохраняем данные в SQLite
    insert_stock_history(data, today_str)

    # Удаляем старые файлы
    cutoff_date = datetime.now() - timedelta(days=keep_days)
    for file in os.listdir(data_dir):
        if file.startswith(base_filename) and file.endswith(".json"):
            date_part = file[len(base_filename) + 1:-5]
            try:
                file_date = datetime.strptime(date_part, "%Y-%m-%d")
                if file_date < cutoff_date:
                    os.remove(os.path.join(data_dir, file))
            except ValueError:
                continue
