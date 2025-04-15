import asyncio
import logging
import aiocron
import json

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
        await bot.send_message(chat_id=chat_id, text= "⏳ Запуск автоматического сбора данных...", parse_mode="Markdown")
        logging.info(f"✅ Данные отправлены в чат {chat_id}")

    results = await scrape_data()

    with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    response = "📊 **Остатки товаров за сегодня:**\n\n"

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

    for chat_id in CHAT_IDS:
        await bot.send_message(chat_id=chat_id, text=response, parse_mode="Markdown")
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

# Сохраняем историю остатков товаров в файл
results = await scrape_data()
save_stock_history(results)