from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery

import json
import logging

import app.keyboards as kb
from Parser.Parser import scrape_data
from config import OUTPUT_FILE

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
    
    await message.answer(response, parse_mode="Markdown")

@router.callback_query(F.data == '/get_data')
async def cmd_get_data(callback: CallbackQuery):
    await callback.message.answer("Собираю данные... ⏳")
    
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
    
    await callback.message.answer(response, parse_mode="Markdown")


