import re
from datetime import datetime

from aiogram import types, F, Router
from aiogram.types import CallbackQuery, InlineKeyboardButton
from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback, get_user_locale
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext

from manicure_bot.utils import keyboard
from manicure_bot.bot_instance import bot
from manicure_bot.config import settings
from manicure_bot.database import User, Appointment
from manicure_bot.database.db import get_db
from manicure_bot.handlers.states import Registration

router = Router()

# Define time slots (assuming each appointment takes 1 hour)
time_slots = ["09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00"]


@router.message(lambda message: message.text == "Записаться")
async def book_appointment(msg: types.Message):
    await msg.answer("Пожалуйста, выберите дату:", reply_markup=await SimpleCalendar(locale=await get_user_locale(msg.from_user)).start_calendar())


# simple calendar usage - filtering callbacks of calendar format
@router.callback_query(SimpleCalendarCallback.filter())
async def process_simple_calendar(callback_query: CallbackQuery, callback_data: CallbackData, state: FSMContext):
    with get_db() as db:
        builder = InlineKeyboardBuilder()
        for time in time_slots:
            builder.add(types.InlineKeyboardButton(
                text=time,
                callback_data=f"time_{time}"
            ))
        builder.adjust(4)

        calendar = SimpleCalendar(
            locale=await get_user_locale(callback_query.from_user), show_alerts=True
        )
        calendar.set_dates_range(datetime(2024, 8, 25), datetime(2024, 9, 25))
        selected, date = await calendar.process_selection(callback_query, callback_data)
        if selected:
            await state.update_data(selected_date=date)

            user_data = await state.get_data()
            if "selected_appointment_id" in user_data:
                appointment_id = user_data['selected_appointment_id']
                appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
                if appointment:
                    appointment.date = date
                    db.commit()

            await callback_query.message.answer(
                f'Вы выбрали {date.strftime("%d/%m/%Y")}. Пожалуйста, выберите удобное для Вас время:',
                reply_markup=builder.as_markup()
            )


@router.callback_query(lambda c: c.data.startswith("time_"))
async def select_time(callback_query: CallbackQuery, state: FSMContext):
    with get_db() as db:
        time_str = callback_query.data.split("_")[1]
        time_obj = datetime.strptime(time_str, "%H:%M").time()

        user_data = await state.get_data()

        user_id = callback_query.from_user.id
        user = db.query(User).filter(User.user_id == user_id).first()
        await state.update_data(selected_time=time_obj)

        if "selected_appointment_id" in user_data:
            appointment_id = user_data['selected_appointment_id']
            appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
            if appointment:
                await state.update_data(name=user.name, phone_number=user.phone_number, selected_time=time_obj)
                await confirm_appointment_with_user_data(callback_query.message, state, user)
        else:
            if user:
                await state.update_data(name=user.name, phone_number=user.phone_number, selected_time=time_obj)
                await confirm_appointment_with_user_data(callback_query.message, state, user)
            else:
                await request_user_info(callback_query.message, state)

        await callback_query.message.edit_reply_markup(reply_markup=None)


async def confirm_appointment_with_user_data(msg: types.Message, state: FSMContext, user: User):
    user_data = await state.get_data()
    date_str = user_data['selected_date'].strftime("%d/%m/%Y")
    time_str = user_data['selected_time'].strftime("%H:%M")
    phone_number = user.phone_number
    name = user.name

    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="Подтвердить запись", callback_data="confirm_appointment"))
    builder.add(InlineKeyboardButton(text="Изменить данные", callback_data="change_data"))

    answer_message = (
        f"Проверьте ваши данные:\n\nДата: {date_str}\nВремя: {time_str}\nИмя: {name}\nТелефон: {phone_number}"
        "\n\nЕсли все верно, нажмите 'Подтвердить запись'.\nЕсли нужно изменить данные, нажмите 'Изменить данные'."
    )

    await msg.answer(
        answer_message,
        reply_markup=builder.as_markup()
    )
    await state.set_state(Registration.waiting_for_confirmation)


@router.callback_query(lambda c: c.data == "change_data")
async def change_data(callback_query: CallbackQuery, state: FSMContext):
    await request_user_info(callback_query.message, state)
    await callback_query.message.edit_reply_markup(reply_markup=None)


@router.callback_query(lambda c: c.data == "confirm_appointment")
async def confirm_appointment(callback_query: CallbackQuery, state: FSMContext):
    with get_db() as db:
        user_data = await state.get_data()
        user_id = callback_query.from_user.id

        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            user = User(user_id=user_id, name=user_data['name'], phone_number=user_data['phone_number'])
            db.add(user)
        else:
            user.name = user_data['name']
            user.phone_number = user_data['phone_number']

        if "selected_appointment_id" in user_data:
            appointment_id = user_data["selected_appointment_id"]
            appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
            if appointment:
                appointment.date = user_data['selected_date']
                appointment.time = user_data['selected_time']
                action_message = "Ваша запись была успешно изменена"
        else:
            appointment = Appointment(user_id=user_id, date=user_data['selected_date'], time=user_data['selected_time'])
            db.add(appointment)
            action_message = "Ваша запись на маникюр подтверждена"

        db.commit()

        date_str = appointment.date.strftime("%d/%m/%Y")
        time_str = appointment.time.strftime("%H:%M")
        await callback_query.message.answer(f'{action_message}: {date_str} в {time_str}.', reply_markup=keyboard)

        master_message = f'Новая запись на маникюр: {date_str} в {time_str}. Клиент: {user.name}, телефон: {user.phone_number}.'
        await bot.send_message(chat_id=settings.master_chat_id, text=master_message)
        await state.clear()

        await callback_query.message.edit_reply_markup(reply_markup=None)


# View and cancel the appointment
@router.message(lambda message: message.text == "Мои записи")
async def view_appointment(msg: types.Message):
    with get_db() as db:
        user_id = msg.from_user.id
        appointments = db.query(Appointment).filter(Appointment.user_id == user_id).all()
        if appointments:
            builder = InlineKeyboardBuilder()
            for appointment in appointments:
                date_str = appointment.date.strftime("%d/%m/%Y")
                time_str = appointment.time.strftime("%H:%M")
                builder.add(
                    InlineKeyboardButton(
                        text=f"{date_str} в {time_str}",
                        callback_data=f"appointment_{appointment.id}"
                    )
                )
            builder.add(InlineKeyboardButton(text="Назад", callback_data="back_to_main"))
            builder.adjust(1)
            await msg.answer(f'Ваши запиcи:', reply_markup=builder.as_markup())
        else:
            await msg.answer("У вас нет активных записей.")


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

    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="Подтвердить запись", callback_data="confirm_appointment"))
    builder.add(InlineKeyboardButton(text="Изменить данные", callback_data="change_data"))

    answer_message = (
        f"Проверьте ваши данные:\n\nДата: {date_str}\nВремя: {time_str}\nИмя: {name}\nТелефон: {phone_number}"
        "\n\nЕсли все верно, нажмите 'Подтвердить запись'.\nЕсли нужно изменить данные, нажмите 'Изменить данные'."
    )

    await msg.answer(
        answer_message,
        reply_markup=builder.as_markup()
    )
    await state.set_state(Registration.waiting_for_confirmation)
