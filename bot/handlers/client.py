from aiogram import F
from aiogram.types import Message, CallbackQuery
from aiogram import Router
from bot.keyboard import main_kb, katalog_kb

router = Router()
json_data = "user_list.json"


@router.message(F.text == "/start")
async def start(message: Message):
    await message.answer("Добрый день", reply_markup=main_kb)


@router.message(F.text == "Каталог")
async def katalog(message: Message):
    await message.answer("Каталог", reply_markup=katalog_kb)
