from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)

main = [
    [KeyboardButton(text="Каталог")],
    [KeyboardButton(text="Настройки")]
]
main_kb = ReplyKeyboardMarkup(keyboard=main, resize_keyboard=True)
katalog = [
    [InlineKeyboardButton(text="Клавиатуры", callback_data="Keyboards")],
    [InlineKeyboardButton(text="Услуги", callback_data="Services")]
]
katalog_kb = InlineKeyboardMarkup(inline_keyboard=katalog)
