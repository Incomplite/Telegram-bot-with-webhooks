import re
from datetime import datetime, time

from aiogram import types, F, Router
from aiogram.types import CallbackQuery, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback, get_user_locale
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from manicure_bot.utils import keyboard

from manicure_bot.bot_instance import bot

from manicure_bot.config import settings

from manicure_bot.database import User, Appointment

from manicure_bot.database.db import get_db

router = Router()

class Registration(StatesGroup):
    waiting_for_phone = State()
    waiting_for_name = State()
    waiting_for_confirmation = State()


@router.message(Command("id"))
async def message_handler(msg: types.Message):
    await msg.answer(f"Твой ID: {msg.from_user.id}")

# Define time slots (assuming each appointment takes 1 hour)
time_slots = ["09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00"]


@router.message(lambda message: message.text == "Записаться на маникюр")
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
            await callback_query.message.answer(
                f'Вы выбрали {date.strftime("%d/%m/%Y")}. Пожалуйста, выберите удобное для Вас время:',
                reply_markup=builder.as_markup()
            )
            user_id = callback_query.from_user.id
            appointment = Appointment(user_id=user_id, date=date)
            db.add(appointment)
            db.commit()


@router.callback_query(lambda c: c.data.startswith("time_"))
async def select_time(callback_query: CallbackQuery):
    with get_db() as db:
        time_str = callback_query.data.split("_")[1]
        user_id = callback_query.from_user.id

        # Преобразуем строку времени в объект time
        time_obj = datetime.strptime(time_str, "%H:%M").time()

        appointment = db.query(Appointment).filter(Appointment.user_id == user_id).first()
        appointment.time = time_obj
        db.commit()

        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(
            text="Подтвердить запись",
            callback_data="confirm_appointment")
        )

        await callback_query.message.answer(
            f"Вы будете записаны на {appointment.date.strftime('%d/%m/%Y')} в {time_str}. Подтвердите запись.",
            reply_markup=builder.as_markup()
        )


# Confirmation of the appointment
@router.callback_query(lambda c: c.data == "confirm_appointment")
async def confirm_appointment(callback_query: CallbackQuery, state: FSMContext):
    with get_db() as db:
        user_id = callback_query.from_user.id
        user = db.query(User).filter(User.user_id == user_id).first()

        if not user:
            user = User(user_id=user_id)
            db.add(user)
            db.commit()

        # Проверяем, заполнены ли номер телефона и имя
        if not user.phone_number or not user.name:
            await callback_query.message.answer("Пожалуйста, завершите ввод ваших данных перед подтверждением.")
            await request_user_info(callback_query.message, state)
        else:
            appointment = db.query(Appointment).filter(Appointment.user_id == user_id).first()
            date_str = appointment.date.strftime("%d/%m/%Y")
            time_str = appointment.time.strftime("%H:%M")
            await callback_query.message.answer(f'Ваша запись на маникюр подтверждена: {date_str} в {time_str}.', reply_markup=keyboard)

            master_message = f'Новая запись на маникюр: {date_str} в {time_str}. Клиент: {user.name}, телефон: {user.phone_number}.'
            await bot.send_message(chat_id=settings.master_chat_id, text=master_message)


# View and cancel the appointment
@router.message(Command("my_appointment"))
async def view_appointment(msg: types.Message):
    with get_db() as db:
        user_id = msg.from_user.id
        appointment = db.query(Appointment).filter(Appointment.user_id == user_id).first()
        if appointment:
            date_str = appointment.date.strftime("%d/%m/%Y")
            time_str = appointment.time.strftime("%H:%M")
            await msg.answer(f'Ваша запись: {date_str} в {time_str}. Вы можете изменить её или отменить командой /change или /cancel.')
        else:
            await msg.answer("У вас нет активных записей.")


async def request_user_info(msg: types.Message, state: FSMContext):
    with get_db() as db:
        user_id = msg.from_user.id
        
        # Проверка наличия пользователя в базе данных
        user = db.query(User).filter(User.user_id == user_id).first()
        
        if not user:
            # Создаем пользователя в базе данных, если его там нет
            user = User(user_id=user_id)
            db.add(user)
            db.commit()
            db.refresh(user)

        if not user.phone_number or not user.name:
            # Запрашиваем номер телефона
            await msg.answer("Пожалуйста, отправьте ваш номер телефона в формате +7XXXXXXXXXX.")
            await state.set_state(Registration.waiting_for_phone)
        else:
            await msg.answer("Ваши данные уже заполнены.")


@router.message(Registration.waiting_for_phone, F.text)
async def handle_contact_text(msg: types.Message, state: FSMContext):
    with get_db() as db:
        user_id = msg.from_user.id
        text = msg.text.strip()

        # Проверка, является ли текст номером телефона
        if re.match(r'^\+7\d{10}$', text):
        # Обновляем информацию о пользователе
            user = db.query(User).filter(User.user_id == user_id).first()
            if user:
                user.phone_number = text
                db.commit()

                # Теперь запрашиваем имя пользователя
                await msg.answer("Спасибо! Теперь введите ваше имя, как к вам обращаться.", reply_markup=types.ReplyKeyboardRemove())
                await state.set_state(Registration.waiting_for_name)
            else:
                await msg.answer("Что-то пошло не так. Попробуйте еще раз.")
        else:
            await msg.answer("Неверный формат номера телефона. Пожалуйста, введите номер в формате +7XXXXXXXXXX.")


@router.message(Registration.waiting_for_name, F.text)
async def handle_name(msg: types.Message, state: FSMContext):
    with get_db() as db:
        user_id = msg.from_user.id
        name = msg.text.strip()

        # Обновляем информацию о пользователе
        user = db.query(User).filter(User.user_id == user_id).first()
        if user and not user.name:
            user.name = name
            db.commit()

            # Подтверждаем запись
            await confirm_appointment(msg, state)
            await state.clear()
        else:
            await msg.answer("Что-то пошло не так. Попробуйте еще раз.")
