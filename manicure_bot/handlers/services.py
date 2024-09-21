from aiogram import types, Router
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from manicure_bot.database.db import get_db
from manicure_bot.database import Service
from manicure_bot.bot_instance import bot

router = Router()


# Обработчик команды "Услуги"
@router.message(lambda message: message.text == "Услуги")
async def services_command(message: types.Message):
    with get_db() as db:
        services = db.query(Service).all()

        keyboard = InlineKeyboardBuilder()
        for service in services:
            button = InlineKeyboardButton(text=service.name, callback_data=f"service_{service.id}")
            keyboard.add(button)

        back_button = InlineKeyboardButton(text="Назад", callback_data="back_to_main")
        keyboard.add(back_button)

        keyboard.adjust(1)
    
        await message.answer("Перечень услуг:", reply_markup=keyboard.as_markup())


# Обработка нажатия кнопок
@router.callback_query(lambda callback_query: callback_query.data.startswith("service_"))
async def service_callback(callback_query: types.CallbackQuery):
    service_id = int(callback_query.data.split("_")[1])
    
    with get_db() as db:
        service = db.query(Service).get(service_id)
    
    if service:
        text = f"<b>{service.name}</b>\n\n{service.description}\n\nЦена: {service.price} руб."
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Вернуться к услугам", callback_data="back_to_services")]
        ])
        if service.image_url:
            await bot.send_photo(
                chat_id=callback_query.from_user.id,
                photo=service.image_url,
                caption=text,
                parse_mode="HTML",
                reply_markup=keyboard
            )
        else:
            await bot.send_message(
                chat_id=callback_query.from_user.id,
                text=text,
                parse_mode="HTML",
                reply_markup=keyboard
            )
    await callback_query.answer()

# Обработка нажатия кнопки "Вернуться к услугам"
@router.callback_query(lambda callback_query: callback_query.data == "back_to_services")
async def back_to_services(callback_query: types.CallbackQuery):
    await callback_query.message.edit_reply_markup(reply_markup=None)
    await services_command(callback_query.message)
    await callback_query.answer()

# Обработка нажатия кнопки "Назад"
@router.callback_query(lambda callback_query: callback_query.data == "back")
async def back_callback(callback_query: types.CallbackQuery):
    await callback_query.message.delete()
    await callback_query.answer()