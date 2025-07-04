import os
import json
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment

# Импортируем ARTICLES из config.py
from config import ARTICLES

def generate_excel_report(data_dir="Parser/data", base_filename="output", output_file="weekly_report.xlsx"):
    # Список файлов с данными
    files = sorted([
        f for f in os.listdir(data_dir)
        if f.startswith(base_filename) and f.endswith(".json")
    ])

    date_labels = []
    stock_data = {}

    # Собираем данные по датам
    for file in files:
        date_str = file[len(base_filename) + 1:-5]
        date_labels.append(date_str)

        with open(os.path.join(data_dir, file), "r", encoding="utf-8") as f:
            json_data = json.load(f)

        for article_id, item in json_data.items():
            if article_id not in stock_data:
                stock_data[article_id] = {}

            if isinstance(item, dict):
                total = item.get("total_stock", 0)
                stock_data[article_id][date_str] = total
            else:
                stock_data[article_id][date_str] = 0  # Если нет данных — 0

    # Создаем Excel
    wb = Workbook()
    ws = wb.active
    ws.title = "Stock Report"

    header_font = Font(bold=True)
    category_font = Font(bold=True, size=12)
    center_alignment = Alignment(horizontal="center", vertical="center")

    # Заголовок
    headers = ["Артикул", "Название", "Категория"] + date_labels
    ws.append(headers)
    for col_num in range(1, len(headers) + 1):
        ws.cell(row=1, column=col_num).font = header_font
        ws.cell(row=1, column=col_num).alignment = center_alignment

    row_idx = 2

    # Группируем артикулы по категориям
    categories = {}
    for article, info in ARTICLES.items():
        cat = info.get("category", "Прочее")
        categories.setdefault(cat, []).append(str(article))  # ключи в JSON — строки

    for cat_name in sorted(categories.keys()):
        # Вставляем заголовок категории
        ws.append([cat_name])
        ws.cell(row=row_idx, column=1).font = category_font
        row_idx += 1

        for article_id in categories[cat_name]:
            info = ARTICLES.get(int(article_id), {})
            name = info.get("name", "")
            row = [article_id, name, cat_name]

            for date in date_labels:
                qty = stock_data.get(article_id, {}).get(date, 0)
                row.append(qty)

            ws.append(row)
            row_idx += 1

        # Пустая строка после категории
        ws.append([])
        row_idx += 1

    # Сохраняем
    output_path = os.path.join(data_dir, output_file)
    wb.save(output_path)
    return output_path
