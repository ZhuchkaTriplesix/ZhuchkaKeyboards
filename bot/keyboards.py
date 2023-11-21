from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)

start = [
    [KeyboardButton(text="⌨️PRODUCTS⌨️"),
     KeyboardButton(text="🛠SERVICES🛠")]
]
start_kb = ReplyKeyboardMarkup(keyboard=start, resize_keyboard=True)
products = [
    [InlineKeyboardButton(text="65% Keyboards", callback_data="65% Keyboards")],
    [InlineKeyboardButton(text="TKL Keyboards", callback_data="TKL Keyboards")]
]
products_kb = InlineKeyboardMarkup(inline_keyboard=products)
services = [
    [InlineKeyboardButton(text="Lubing switches", callback_data="Lubing switches")]
]
service_kb = InlineKeyboardMarkup(inline_keyboard=services)
kb65 = [
    [InlineKeyboardButton(text="ZK board", callback_data="ZK board")]
]
kb65_kb = InlineKeyboardMarkup(inline_keyboard=kb65)
