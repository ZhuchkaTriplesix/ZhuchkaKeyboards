from aiogram import F
from aiogram.types import Message, CallbackQuery
from aiogram import Router
import database.functions
import bot.keyboards

router = Router()


@router.message(F.text == "/start")
async def start(message: Message):
    user = database.functions.TelegramUsersCrud.add_user(message.from_user.id, message.from_user.username)
    await message.answer("privet", reply_markup=bot.keyboards.start_kb)


@router.message(F.text == "⌨️PRODUCTS⌨️")
async def products(message: Message):
    await message.answer("Выберите категорию:", reply_markup=bot.keyboards.products_kb)


@router.message(F.text == "🛠SERVICES🛠")
async def services(message: Message):
    await message.answer("Выберите категорию", reply_markup=bot.keyboards.service_kb)


@router.callback_query(F.data == "65% Keyboards")
async def keyboards_65(callback: CallbackQuery):
    await callback.message.edit_reply_markup(callback.inline_message_id, bot.keyboards.kb65_kb)


@router.callback_query(F.data == "Back_prod")
async def back(callback: CallbackQuery):
    await callback.message.edit_reply_markup(callback.inline_message_id, bot.keyboards.products_kb)
