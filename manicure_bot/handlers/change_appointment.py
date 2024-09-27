from aiogram import types, Router
from aiogram.types import CallbackQuery, InlineKeyboardButton
from aiogram_calendar import SimpleCalendar, get_user_locale
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext

from manicure_bot.keyboards import main_keyboard
from manicure_bot.database import Appointment, User
from manicure_bot.database.db import get_db

router = Router()


@router.message(lambda message: message.text == "📅Мои записи")
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


@router.callback_query(lambda c: c.data.startswith("appointment_"))
async def handle_appointment_selection(callback_query: CallbackQuery, state: FSMContext):
    appointment_id = int(callback_query.data.split("_")[1])
    await state.update_data(selected_appointment_id=appointment_id)

    with get_db() as db:
        appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
        user = db.query(User).filter(User.user_id == appointment.user_id).first()
        if appointment:
            date_str = appointment.date.strftime("%d/%m/%Y")
            time_str = appointment.time.strftime("%H:%M")
            service_names = ", ".join([service.name for service in appointment.services])
            service_prices = sum([service.price for service in appointment.services])
            name = user.name
            phone_number = user.phone_number
        
            appointment_message = (
                f"Ваша запись:\n\nУслуга: {service_names}\nДата: {date_str}\n"
                f"Время: {time_str}\nИмя: {name}\nТелефон: {phone_number}\nЦена: {service_prices} руб.\n\n"
                "Что вы хотите сделать с этой записью?"
            )

    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="Изменить запись", callback_data="change_appointment"))
    builder.add(InlineKeyboardButton(text="Отменить запись", callback_data="cancel_appointment"))
    builder.add(InlineKeyboardButton(text="Назад", callback_data="back_to_appointments"))

    await callback_query.message.delete()
    await callback_query.message.answer(
        appointment_message,
        reply_markup=builder.as_markup()
    )


@router.callback_query(lambda c: c.data == "back_to_appointments")
async def back_to_appointments(callback_query: CallbackQuery, state: FSMContext):
    with get_db() as db:
        user_id = callback_query.from_user.id
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
            await callback_query.message.edit_reply_markup(reply_markup=None)
            await callback_query.message.answer(f'Ваши запиcи:', reply_markup=builder.as_markup())
        else:
            await callback_query.message.answer("У вас нет активных записей.")


@router.callback_query(lambda c: c.data == "back_to_main")
async def back_to_main(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    await callback_query.message.delete()
    await callback_query.message.answer(
        "Вы вернулись назад.",
        reply_markup=main_keyboard(user_id)
    )


@router.callback_query(lambda c: c.data == "change_appointment")
async def change_appointment(callback_query: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    if "selected_appointment_id" in user_data:
        appointment_id = user_data['selected_appointment_id']
        with get_db() as db:
            appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
            if appointment:
                service_ids = [service.id for service in appointment.services]
                await state.update_data(selected_services=service_ids)
    
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
    await msg.answer(help_text, reply_markup=main_keyboard(msg.from_user.id))
