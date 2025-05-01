import os
import json
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
                stock_data[article] = {}

            if isinstance(item, dict):
                for wh, qty in item.get("details", {}).items():
                    stock_data[article].setdefault(date_str, 0)
                    stock_data[article][date_str] += qty

    # Создание Excel
    wb = Workbook()
    ws = wb.active
    ws.title = "Остатки за неделю"

    # Заголовок
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=1 + len(date_labels))
    title_cell = ws.cell(row=1, column=1, value="Остатки по артикулу за последние 7 дней")
    title_cell.font = Font(bold=True, size=14)
    title_cell.alignment = Alignment(horizontal="center")

    # Шапка
    headers = ["Артикул"] + date_labels
    for col, header in enumerate(headers, start=1):
        cell = ws.cell(row=2, column=col, value=header)
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal="center")

    # Данные
    row = 3
    for article, day_data in stock_data.items():
        ws.cell(row=row, column=1, value=article)
        for i, date in enumerate(date_labels):
            qty = day_data.get(date, 0)
            ws.cell(row=row, column=2 + i, value=qty)
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
