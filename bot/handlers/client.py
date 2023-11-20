from aiogram import F
from aiogram.types import Message, CallbackQuery
from aiogram import Router
import bot.models
import bot.keyboards

router = Router()


@router.message(F.text == "/start")
async def start(message: Message):
    user = bot.models.UsersCrud.add_user(message.from_user.id, message.from_user.username)
    await message.answer("privet", reply_markup=bot.keyboards.start_kb)


@router.message(F.text == "⌨️PRODUCTS⌨️")
async def products(message: Message):
    await message.answer("Выберите категорию:", reply_markup=bot.keyboards.products_kb)
