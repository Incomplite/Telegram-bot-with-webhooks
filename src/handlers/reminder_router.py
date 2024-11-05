from datetime import datetime, timedelta

from aiogram import F, Router
from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery
)

from src.bot.bot_instance import bot
from src.config import settings
from src.database import Appointment
from src.database.db import get_db
from src.keyboards import main_keyboard
from src.middlewares.scheduler import scheduler
from src.models import AppointmentStatus

router = Router()

async def send_reminder(appointment_id, user_id, name, time):
    message = (
        f"Здравствуйте, {name}!\n\n"
        f"Напоминаем, что у вас запланирована запись завтра в {time}.\n"
        f"Вы придете?"
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Да", callback_data=f"confirm_{appointment_id}")],
        [InlineKeyboardButton(text="Нет", callback_data=f"cancel_{appointment_id}")]
    ])

    await bot.send_message(chat_id=user_id, text=message, reply_markup=keyboard)

# Функция для планирования напоминания
def schedule_reminder(appointment):
    reminder_time = datetime.combine(appointment.date, appointment.time) - timedelta(days=1)
    scheduler.add_job(send_reminder, 'date', run_date=reminder_time, args=[
        appointment.id,
        appointment.user_id,
        appointment.name,
        appointment.time.strftime("%H:%M")
    ])


@router.callback_query(F.data.startswith('confirm_') | F.data.startswith('cancel_'))
async def process_callback_button(callback_query: CallbackQuery):
    action, appointment_id = callback_query.data.split('_')
    appointment_id = int(appointment_id)

    with get_db() as db:
        appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()

        if appointment is None:
            return
        
        user_id = appointment.user_id
        appointment_time = appointment.time.strftime('%H:%M')
        client_name = appointment.name

        if action == 'confirm':
            appointment.status = AppointmentStatus.CONFIRMED.value
            client_message = "Спасибо за подтверждение! Ждем вас в назначенное время."
        elif action == 'cancel':
            db.delete(appointment)
            client_message = "Ваша запись отменена. Спасибо за уведомление."

        admin_message = (
            f"🔔 <b>{'Клиент подтвердил' if action == 'confirm' else 'Клиент отменил'} запись:</b>\n\n"
            f"👤 Имя клиента: {client_name}\n"
            f"👤 Профиль: @{callback_query.from_user.username}\n"
            f"⏰ Время: {appointment_time}\n"
        )

        db.commit()

    await bot.send_message(chat_id=user_id, text=client_message)
    await bot.send_message(chat_id=settings.ADMIN_USER_ID, text=admin_message)
    await callback_query.message.edit_reply_markup(reply_markup=None)
