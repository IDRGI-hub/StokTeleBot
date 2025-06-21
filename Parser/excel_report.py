import os
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment
from openpyxl.utils import get_column_letter

from .db_utils import fetch_stock_range

def generate_excel_report(output_file="weekly_report.xlsx"):
    """Generate weekly Excel report from SQLite data."""
    stock_data = fetch_stock_range()
    date_labels = sorted({d for prod in stock_data.values() for d in prod.keys()})

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

    # Сохраняем рядом с базой данных
    output_dir = os.path.dirname(__file__)
    output_path = os.path.join(output_dir, output_file)
    wb.save(output_path)
    return output_path
