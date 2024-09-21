from aiogram import types, Router
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from manicure_bot.database.db import get_db
from manicure_bot.database import Service
from manicure_bot.bot_instance import bot

router = Router()


# Обработчик команды "Услуги"
@router.message(lambda message: message.text == "Контакты")
async def send_contact_info(message: types.Message):
    contact_info = (
        "Ваш мастер маникюра Кристина\n"
        "Номер телефона: 89045045661\n"
        "Адрес: ул. Горсоветская, д.49/1"
    )
    await message.answer(contact_info)
    
    # Координаты местоположения
    latitude = 47.2420
    longitude = 39.7777
    await message.answer_location(latitude, longitude)
