from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from sqlalchemy import func

from manicure_bot.database import Appointment, Photo
from manicure_bot.database.db import get_db

time_slots = ["09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00"]


def is_sunday(date):
    return date.weekday() == 6  # 6 - это воскресенье


def get_available_time_slots(date, db):
    date_only = date.date()
    booked_appointments = db.query(Appointment).filter(Appointment.date == date_only).all()
    booked_times = [appointment.time.strftime("%H:%M") for appointment in booked_appointments]
    available_times = [time for time in time_slots if time not in booked_times]
    return available_times


# Функция для удаления записи
def delete_appointment_job(appointment_id: int):
    with get_db() as db:
        appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
        if appointment:
            db.delete(appointment)
            db.commit()
            print(f"Запись {appointment_id} была удалена.")
        else:
            print(f"Запись {appointment_id} не найдена.")


# Функция получения фотографий из базы данных
def get_photos():
    with get_db() as db:
        photos = db.query(Photo).all() 
    return photos

# Функция создания inline-клавиатуры для листания фото
def get_photo_keyboard(photo_index: int, total_photos: int):
    buttons = []
    
    # Кнопка "Назад", если это не первая фотография
    if photo_index > 0:
        buttons.append(InlineKeyboardButton('⬅️Назад', callback_data=f'prev_{photo_index - 1}'))
    
    # Кнопка "Вперед", если это не последняя фотография
    if photo_index < total_photos - 1:
        buttons.append(InlineKeyboardButton('Вперед➡️', callback_data=f'next_{photo_index + 1}'))
    
    # Возвращаем клавиатуру с кнопками
    return InlineKeyboardMarkup(row_width=2).add(*buttons)