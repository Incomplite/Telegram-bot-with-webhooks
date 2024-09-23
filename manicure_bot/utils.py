from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from sqlalchemy import func

from manicure_bot.database import Appointment

time_slots = ["09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00"]


def is_sunday(date):
    return date.weekday() == 6  # 6 - это воскресенье


def get_available_time_slots(date, db):
    date_only = date.date()
    booked_appointments = db.query(Appointment).filter(Appointment.date == date_only).all()
    booked_times = [appointment.time.strftime("%H:%M") for appointment in booked_appointments]
    available_times = [time for time in time_slots if time not in booked_times]
    return available_times
