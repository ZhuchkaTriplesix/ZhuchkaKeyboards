from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)

main = [
    [KeyboardButton(text="Каталог")],
    [KeyboardButton(text="Настройки")]
]
main_kb = ReplyKeyboardMarkup(keyboard=main, resize_keyboard=True)