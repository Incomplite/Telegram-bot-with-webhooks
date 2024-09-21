from aiogram import types, Router
from aiogram.filters import Command

from manicure_bot.config import settings
from manicure_bot.database import User, Appointment, Service
from manicure_bot.database.db import get_db

router = Router()

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
                    service = db.query(Service).filter(Service.id == appointment.service_id).first()
                    name = user.name
                    number = user.phone_number
                    date_str = appointment.date.strftime("%d/%m/%Y")
                    time_str = appointment.time.strftime("%H:%M")
                    service_name = service.name if service else "Неизвестная услуга"
                    response_text = (
                        f'Пользователь {user.user_id}:\n\nИмя: {name}\n'
                        f'Номер телефона: {number}\nУслуга: {service_name}\n'
                        f'Запись: {date_str} в {time_str}\n'
                    )
                    response += response_text
                await msg.answer(response)
            else:
                await msg.answer("Нет активных записей.")
    else:
        await msg.answer("У вас нет доступа к этой команде.")
