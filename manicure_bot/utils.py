from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from manicure_bot.database import Appointment


def is_sunday(date):
    return date.weekday() == 6  # 6 - это воскресенье


# Функция для получения занятых временных слотов на конкретную дату
def get_booked_times(db, date):
    booked_appointments = db.query(Appointment).filter(Appointment.date == date).all()
    return {appointment.time.strftime("%H:%M") for appointment in booked_appointments}


# Функция для создания клавиатуры с доступными временными слотами
def build_time_slots_keyboard(available_time_slots):
    builder = InlineKeyboardBuilder()
    for time in available_time_slots:
        builder.add(InlineKeyboardButton(
            text=time,
            callback_data=f"time_{time}"
        ))
    builder.adjust(4)
    return builder