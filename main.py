import asyncio
import logging
import aiocron
import json
import ast

from aiogram import Bot, Dispatcher

from config import TOKEN, CHAT_IDS, OUTPUT_FILE
from app.hendlers import router
from Parser.Parser import scrape_data
from Parser.Save_utils import save_stock_history

bot = Bot(TOKEN)
dp = Dispatcher()

async def send_daily_stock():
    logging.info("⏳ Запуск автоматического сбора данных...")

    for chat_id in CHAT_IDS:
        await bot.send_message(chat_id=chat_id, text="⏳ Запуск автоматического сбора данных...", parse_mode="Markdown")
        logging.info(f"✅ Сообщение о начале сбора отправлено в чат {chat_id}")

    results = await scrape_data()

    # 💾 Сохраняем результаты в JSON-файл с датой
    save_stock_history(results)

    with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    response = "📊 *Остатки товаров за сегодня:*\n\n"

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
    for chat_id in CHAT_IDS:
        for i in range(0, len(response), MAX_LENGTH):
            chunk = response[i:i + MAX_LENGTH]
            await bot.send_message(chat_id=chat_id, text=chunk, parse_mode="Markdown")
        logging.info(f"✅ Данные отправлены в чат {chat_id}")

async def main():
    logging.info("🤖 Бот запущен!")
    
    # Запуск планировщика задачи в фоне
    aiocron.crontab("50 23 * * *", func=send_daily_stock),
    dp.include_router(router)
    
    # Запускаем бота
    await dp.start_polling(bot, polling_timeout = 5)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bye!")
