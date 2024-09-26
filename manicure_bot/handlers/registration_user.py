import re

from aiogram import types, F, Router
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext

from manicure_bot.handlers.states import Registration
from manicure_bot.database.db import get_db
from manicure_bot.database import Service

router = Router()

async def request_user_info(msg: types.Message, state: FSMContext):
    await msg.answer("Пожалуйста, отправьте ваш номер телефона в формате +7XXXXXXXXXX.")
    await state.set_state(Registration.waiting_for_phone)


@router.message(Registration.waiting_for_phone, F.text)
async def handle_contact_text(msg: types.Message, state: FSMContext):
    text = msg.text.strip()

    if re.match(r'^(\+7|8)\d{10}$', text):
        await state.update_data(phone_number=text)
        await msg.answer("Спасибо! Теперь введите ваше имя, как к вам обращаться.", reply_markup=types.ReplyKeyboardRemove())
        await state.set_state(Registration.waiting_for_name)
        await msg.delete()
    else:
        await msg.answer("Неверный формат номера телефона. Пожалуйста, введите номер в формате +7XXXXXXXXXX.")


@router.message(Registration.waiting_for_name, F.text)
async def handle_name(msg: types.Message, state: FSMContext):
    name = msg.text.strip()
    await state.update_data(name=name)

    user_data = await state.get_data()
    date_str = user_data['selected_date'].strftime("%d/%m/%Y")
    time_str = user_data['selected_time'].strftime("%H:%M")
    phone_number = user_data['phone_number']
    name = user_data['name']

    with get_db() as db:
        service = db.query(Service).get(user_data['selected_service_id'])
        service_name = service.name
        service_price = service.price

    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="Подтвердить запись", callback_data="confirm_appointment"))
    builder.add(InlineKeyboardButton(text="Изменить данные", callback_data="change_data"))

    answer_message = (
        f"Проверьте ваши данные:\n\nУслуга: {service_name}\nДата: {date_str}\nВремя: {time_str}\nИмя: {name}\nТелефон: {phone_number}\nЦена: {service_price} руб."
        "\n\nЕсли все верно, нажмите 'Подтвердить запись'.\nЕсли нужно изменить данные, нажмите 'Изменить данные'."
    )

    await msg.answer(
        answer_message,
        reply_markup=builder.as_markup()
    )
    await state.set_state(Registration.waiting_for_confirmation)
