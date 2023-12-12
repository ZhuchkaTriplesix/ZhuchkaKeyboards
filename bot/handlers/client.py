from aiogram import F
from aiogram.types import Message, CallbackQuery
from aiogram import Router
from bot.keyboard import main_kb

router = Router()
json_data = "user_list.json"

@router.message(F.text == "/start")
async def start(message: Message):
    await message.answer("Добрый день", reply_markup=main_kb)
