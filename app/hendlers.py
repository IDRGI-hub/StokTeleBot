from aiogram import F, Router, types
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, FSInputFile

import json
import logging
import ast

import app.keyboards as kb
from Parser.Parser import scrape_data
from config import OUTPUT_FILE, CHAT_IDS
from Parser.excel_report import generate_excel_report

MAX_LENGTH = 4000

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.reply(f'Привет {message.from_user.full_name}, ChatId: {message.chat.id}', reply_markup=kb.main)
    
@router.message(F.text == 'Помощь')
async def cmd_help(message: Message):
    await message.reply(f'Мои возможности', reply_markup=kb.help)

@router.message(Command("get_stock"))
async def cmd_get_stock(message: Message):
    await message.answer("Собираю данные... ⏳")
    
    # Запуск парсинга
    results = await scrape_data()
    
    # Читаем JSON-файл с результатами
    with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Формируем сообщение
    response = "📊 **Остатки товаров:**\n\n"
    
    for product, stock in data.items():
        if isinstance(stock, dict):
            response += f"🔹 *{product}*\n"
            response += f"   🔸 Всего: {stock['total_stock']} шт.\n"
            response += f"   🔸 Кол-во складов: {stock['warehouses']}\n"
            if stock["details"]:
                for warehouse, qty in stock["details"].items():
                    response += f"   📍 {warehouse}: {qty} шт.\n"
            response += "\n"
        else:
            response += f"🔹 *{product}* - {stock}\n\n"
    
    # Отправляем частями
    MAX_LENGTH = 4000
    for i in range(0, len(response), MAX_LENGTH):
        chunk = response[i:i + MAX_LENGTH]
        await message.answer(chunk, parse_mode="Markdown")


@router.callback_query(F.data == "get_data")
async def cmd_get_data(callback: types.CallbackQuery):
    await callback.message.answer("⏳ Получаю текущие остатки...", parse_mode="Markdown")

    try:
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        response = "📊 *Текущие остатки товаров:*\n\n"

        for product_key, stock in data.items():
            try:
                product_info = ast.literal_eval(product_key)
                name = product_info.get("name", "Без названия")
            except Exception:
                name = str(product_key)

            if isinstance(stock, dict):
                response += f"🔹 *{name}*\n"
                response += f"   🔸 Кол-во складов: {stock['warehouses']}\n"
                if stock.get("details"):
                    for warehouse, qty in stock["details"].items():
                        response += f"   📍 {warehouse}: {qty} шт.\n"
                response += "\n"
            else:
                response += f"🔹 *{name}* - {stock}\n\n"

        MAX_LENGTH = 4000
        for i in range(0, len(response), MAX_LENGTH):
            chunk = response[i:i + MAX_LENGTH]
            await callback.message.answer(chunk, parse_mode="Markdown")

        logging.info(f"✅ Остатки отправлены по запросу пользователя {callback.from_user.id}")

    except Exception as e:
        logging.error(f"❌ Ошибка при получении данных: {e}")
        await callback.message.answer("❌ Произошла ошибка при получении остатков.", parse_mode="Markdown")

    # Обработчик callback-запроса для подписки
@router.callback_query(F.data == '/get_messages')
async def cmd_subscribe(callback: CallbackQuery):
    user_id = str(callback.from_user.id)  # Получаем ID пользователя
    
    # Проверяем, есть ли ID пользователя в списке
    if user_id not in CHAT_IDS:
        CHAT_IDS.append(user_id)  # Добавляем ID пользователя в список
        await callback.message.answer("Вы успешно подписались на рассылку! 📩")
    else:
        await callback.message.answer("Вы уже подписаны на рассылку. ✅")
    
    # Подтверждаем callback-запрос
    await callback.answer()

@router.callback_query(F.data == "compare_stock")
async def handle_compare_stock(callback: CallbackQuery):
    await callback.answer("Генерирую Excel-таблицу...")

    try:
        path = generate_excel_report()
        file = FSInputFile(path)
        await callback.message.answer_document(document=file, caption="🧾 Сравнительная таблица остатков")
    except Exception as e:
        await callback.message.answer(f"⚠️ Ошибка при генерации отчета: {e}")
