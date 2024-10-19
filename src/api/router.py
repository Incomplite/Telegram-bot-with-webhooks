from fastapi import APIRouter, Depends
from fastapi.requests import Request
from fastapi.responses import JSONResponse

from sqlalchemy.orm import Session

from src.api.schemas import AppointmentData
from src.bot.bot_instance import bot
from src.config import settings
from src.database import Appointment, Service
from src.database.db import get_db
from src.keyboards import main_keyboard

router = APIRouter(prefix='/api', tags=['API'])


@router.post("/appointment", response_class=JSONResponse)
async def create_appointment(request: Request):
    # Получаем и валидируем JSON данные
    data = await request.json()
    validated_data = AppointmentData(**data)

    service_names = validated_data.services  # Услуги уже в виде списка

    # Формируем сообщение для пользователя
    message = (
        f"🎉 <b>{validated_data.name}, ваша заявка успешно принята!</b>\n\n"
        "💬 <b>Информация о вашей записи:</b>\n"
        f"👤 <b>Имя клиента:</b> {validated_data.name}\n"
        f"💇 <b>Услуги:</b> {', '.join(service_names)}\n"  # Изменение: выводим все услуги
        f"📅 <b>Дата записи:</b> {validated_data.appointment_date}\n"
        f"⏰ <b>Время записи:</b> {validated_data.appointment_time}\n\n"
        "Спасибо за то что выбрали нас! ✨ Мы ждём вас в назначенное время."
    )

    # Сообщение администратору
    admin_message = (
        "🔔 <b>Новая запись!</b>\n\n"
        "📄 <b>Детали заявки:</b>\n"
        f"👤 Имя клиента: {validated_data.name}\n"
        f"💇 Услуги: {', '.join(service_names)}\n"  # Изменение: выводим все услуги
        f"📅 Дата: {validated_data.appointment_date}\n"
        f"⏰ Время: {validated_data.appointment_time}\n"
    )

    # Добавление заявки в базу данных
    with get_db() as db:
        appointment = Appointment(
            user_id=validated_data.user_id,
            name=validated_data.name,
            date=validated_data.appointment_date,
            time=validated_data.appointment_time
        )
        db.add(appointment)  # Добавляем запись о записи
        db.commit()  # Сохраняем изменения

        # Добавление услуг в ассоциативную таблицу
        for service_name in validated_data.services:
            service = db.query(Service).filter(Service.name == service_name).first()
            if service:
                appointment.services.append(service)  # Добавляем услуги к записи

        db.commit()  # Сохраняем изменения с услугами

    kb = main_keyboard(user_id=validated_data.user_id, first_name=validated_data.name)
    # Отправка сообщений через бота
    await bot.send_message(chat_id=validated_data.user_id, text=message, reply_markup=kb)
    await bot.send_message(chat_id=settings.ADMIN_USER_ID, text=admin_message, reply_markup=kb)

    # Возвращаем успешный ответ
    return {"message": "success!"}

@router.delete("/appointment/{appointment_id}")
async def delete_appointment(appointment_id: int):
    with get_db() as db:
        appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
        if appointment:
            db.delete(appointment)
            db.commit()
            return JSONResponse(status_code=200, content={"message": "Запись удалена"})
        return JSONResponse(status_code=404, content={"message": "Запись не найдена"})
