from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

main = ReplyKeyboardMarkup(
    keyboard=[
    [KeyboardButton(text='Помощь')],
], resize_keyboard=True)

help = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Получить актуальные данные ✅', callback_data='/get_data')],
        [InlineKeyboardButton(text='Получить данные из таблицы 🔴', callback_data='/get_table')],
        [InlineKeyboardButton(text='Подписаться на рассылку📩', callback_data='/get_messages')],
    ]
)    