import os
import json
from datetime import datetime
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment
from openpyxl.utils import get_column_letter

def generate_excel_report(data_dir="Parser/data", base_filename="output", output_file="weekly_report.xlsx"):
    files = sorted([
        f for f in os.listdir(data_dir)
        if f.startswith(base_filename) and f.endswith(".json")
    ])

    # Собираем даты
    date_labels = []
    stock_data = {}

    for file in files:
        date_str = file[len(base_filename) + 1:-5]
        date_labels.append(date_str)

        with open(os.path.join(data_dir, file), "r", encoding="utf-8") as f:
            json_data = json.load(f)

        for article, item in json_data.items():
            if article not in stock_data:
                stock_data[article] = {
                    "name": f"Название {article}",
                    "warehouses": {}
                }

            if isinstance(item, dict):
                for wh, qty in item.get("details", {}).items():
                    stock_data[article]["warehouses"].setdefault(wh, {})[date_str] = qty

    # Создание Excel
    wb = Workbook()
    ws = wb.active
    ws.title = "Остатки за неделю"

    # Заголовок
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=3 + len(date_labels))
    title_cell = ws.cell(row=1, column=1, value="Таблица отображения остатков за последние 7 дней")
    title_cell.font = Font(bold=True, size=14)
    title_cell.alignment = Alignment(horizontal="center")

    # Шапка
    headers = ["Артикул товара", "Название товара", "Склады"] + date_labels
    for col, header in enumerate(headers, start=1):
        cell = ws.cell(row=2, column=col, value=header)
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal="center")

    # Данные
    row = 3
    for article, info in stock_data.items():
        total_by_date = {date: 0 for date in date_labels}

        # Считаем сумму остатков по всем складам на каждую дату
        for wh, day_qty in info["warehouses"].items():
            for date in date_labels:
                total_by_date[date] += day_qty.get(date, 0)

        # Записываем строку в Excel
        ws.cell(row=row, column=1, value=article)
        ws.cell(row=row, column=2, value=info["name"])
        ws.cell(row=row, column=3, value="Всего по всем складам")
        for i, date in enumerate(date_labels):
            ws.cell(row=row, column=4 + i, value=total_by_date[date])

        row += 1

    # Автоширина
    for col in ws.columns:
        max_length = max(len(str(cell.value or "")) for cell in col)
        col_letter = get_column_letter(col[0].column)
        ws.column_dimensions[col_letter].width = max(12, max_length + 2)

    # Сохраняем
    output_path = os.path.join(data_dir, output_file)
    wb.save(output_path)
    return output_path
