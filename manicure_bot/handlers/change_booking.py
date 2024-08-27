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


# Хранение данных о записях (в реальной реализации лучше использовать базу данных)
appointments = {}


@router.callback_query(lambda c: c.data.startswith("appointment_"))
async def handle_appointment_selection(callback_query: CallbackQuery, state: FSMContext):
    appointment_id = int(callback_query.data.split("_")[1])
    await state.update_data(selected_appointment_id=appointment_id)

    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="Изменить запись", callback_data="change_appointment"))
    builder.add(InlineKeyboardButton(text="Отменить запись", callback_data="cancel_appointment"))
    builder.add(InlineKeyboardButton(text="Назад", callback_data="back_to_main"))

    await callback_query.message.answer(
        "Что вы хотите сделать с этой записью?",
        reply_markup=builder.as_markup()
    )


@router.callback_query(lambda c: c.data == "back_to_main")
async def back_to_main(callback_query: CallbackQuery):
    await callback_query.message.answer(
        "Вы вернулись назад.",
        reply_markup=keyboard
    )


@router.callback_query(lambda c: c.data == "change_appointment")
async def change_appointment(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.answer(
        "Пожалуйста, выберите новую дату:",
        reply_markup=await SimpleCalendar(locale=await get_user_locale(callback_query.from_user)).start_calendar()
    )
    await callback_query.message.edit_reply_markup(reply_markup=None)


@router.callback_query(lambda c: c.data == "cancel_appointment")
async def cancel_appointment(callback_query: CallbackQuery, state: FSMContext):
    with get_db() as db:
        user_data = await state.get_data()
        appointment_id = user_data['selected_appointment_id']
        appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()

        if appointment:
            db.delete(appointment)
            db.commit()
            await callback_query.message.answer("Ваша запись была отменена.")
        else:
            await callback_query.message.answer("Не удалось найти запись.")
        
        await state.clear()

        await callback_query.message.edit_reply_markup(reply_markup=None)


@router.message(lambda message: message.text == "Доступные команды")
async def help_command(msg: types.Message):
    help_text = (
        "Вот список доступных команд:\n\n"
        "/view_all_appointments - Посмотреть все записи (доступно только администраторам)"
    )
    await msg.answer(help_text, reply_markup=keyboard)


# Обработчик для просмотра всех записей (только для администратора)
@router.message(Command("view_all_appointments"))
async def view_all_appointments(msg: types.Message):
    if msg.from_user.id == settings.master_user_id:
        with get_db() as db:
            appointments = db.query(Appointment).all()
            if appointments:
                response = "Все записи:\n"
                for appointment in appointments:
                    user = db.query(User).filter(User.user_id == appointment.user_id).first()
                    name = user.name
                    number = user.phone_number
                    date_str = appointment.date.strftime("%d/%m/%Y")
                    time_str = appointment.time.strftime("%H:%M")
                    response_text = (
                        f'Пользователь {user.user_id}:\n\nИмя: {name}\n'
                        f'Номер телефона: {number}\nЗапись: {date_str} в {time_str}\n'
                    )
                    response += response_text
                await msg.answer(response)
            else:
                await msg.answer("Нет активных записей.")
    else:
        await msg.answer("У вас нет доступа к этой команде.")
