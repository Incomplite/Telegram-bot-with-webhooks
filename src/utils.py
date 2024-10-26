from aiogram.types import Message

from src.database import Appointment, Photo
from src.database.db import get_db
from src.keyboards import main_keyboard

time_slots = ["09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00"]


def is_sunday(date):
    return date.weekday() == 6  # 6 - это воскресенье


def get_available_time_slots(date, db):
    date_only = date.date()
    booked_appointments = db.query(Appointment).filter(Appointment.date == date_only).all()
    booked_times = [appointment.time.strftime("%H:%M") for appointment in booked_appointments]
    available_times = [time for time in time_slots if time not in booked_times]
    return available_times


# Функция получения фотографий из базы данных
def get_photos():
    with get_db() as db:
        photos = db.query(Photo).all()
    return photos


async def greet_user(message: Message, is_new_user: bool) -> None:
    """
    Приветствует пользователя и отправляет соответствующее сообщение.
    """
    greeting = "Добро пожаловать" if is_new_user else "С возвращением"
    status = "Вы успешно зарегистрированы!" if is_new_user else "Рады видеть вас снова!"
    await message.answer(
        f"{greeting}, <b>{message.from_user.full_name}</b>! {status}\n"
        "Чем я могу помочь вам сегодня?",
        reply_markup=main_keyboard(user_id=message.from_user.id, first_name=message.from_user.first_name)
    )
