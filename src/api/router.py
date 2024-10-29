from datetime import date

from fastapi import APIRouter, HTTPException
from fastapi.requests import Request
from fastapi.responses import JSONResponse

from src.api.schemas import AppointmentData, Schedule
from src.bot.bot_instance import bot
from src.config import settings
from src.database import Appointment, Service, AvailableTimeSlot
from src.database.db import get_db
from src.keyboards import main_keyboard, contact_button

router = APIRouter(prefix='/api', tags=['API'])


@router.post("/appointment", response_class=JSONResponse)
async def create_appointment(request: Request):
    # Получаем и валидируем JSON данные
    data = await request.json()
    validated_data = AppointmentData(**data)
    
    # Форматируем время
    formatted_time = validated_data.appointment_time.strftime("%H:%M")

    # Формируем сообщение для пользователя
    message = (
        f"🎉 <b>{validated_data.name}, ваша заявка успешно принята!</b>\n\n"
        "💬 <b>Информация о вашей записи:</b>\n"
        f"👤 <b>Имя клиента:</b> {validated_data.name}\n"
        f"💅 <b>Услуги:</b> {', '.join(validated_data.services)}\n"  # Изменение: выводим все услуги
        f"📅 <b>Дата записи:</b> {validated_data.appointment_date}\n"
        f"⏰ <b>Время записи:</b> {formatted_time}\n\n"
    )
    contact_message = (
        "Спасибо за то что выбрали нас! ✨ Мы ждём вас в назначенное время."
    )

    # Сообщение администратору
    admin_message = (
        "🔔 <b>Новая запись!</b>\n\n"
        "📄 <b>Детали заявки:</b>\n"
        f"👤 Имя клиента: {validated_data.name}\n"
        f"💅 Услуги: {', '.join(validated_data.services)}\n"  # Изменение: выводим все услуги
        f"📅 Дата: {validated_data.appointment_date}\n"
        f"⏰ Время: {formatted_time}\n"
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
    inline_kb = contact_button()
    # Отправка сообщений через бота
    await bot.send_message(chat_id=validated_data.user_id, text=message, reply_markup=kb)
    await bot.send_message(chat_id=validated_data.user_id, text=contact_message, reply_markup=inline_kb)
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
    

@router.get("/all-slots/{date}")
async def get_all_slots(date: date):
# Получение доступных слотов из БД для конкретной даты
    with get_db() as db:
        slot = db.query(AvailableTimeSlot).filter(AvailableTimeSlot.date == date).first()
        if slot:
            return {"slots": slot.get_time_slots()}
        return JSONResponse(status_code=404, content={"message": "Слоты не найдены"})


@router.get("/available-slots/{date}")
async def get_available_slots(date: date):
# Получение доступных слотов из БД для конкретной даты
    with get_db() as db:
        slot = db.query(AvailableTimeSlot).filter(AvailableTimeSlot.date == date).first()
        print(f"slot:{slot}")
        # Отфильтровываем уже забронированные места
        booked_times = db.query(Appointment.time).filter(Appointment.date == date).all()
        booked_times = {t[0].strftime("%H:%M") for t in booked_times}
        print(f"booked_times:{booked_times}")
        # Удаляем забронированные слоты из списка доступных слотов
        if slot:
            available_slots = [time for time in slot.get_time_slots() if time not in booked_times]
            print(f"available_slots:{available_slots}")
            return {"slots": available_slots}
        return JSONResponse(status_code=404, content={"message": "Слоты не найдены"})


@router.post("/schedule")
async def save_schedule(schedule: Schedule):
    with get_db() as db:
        existing_slots = db.query(AvailableTimeSlot).filter(AvailableTimeSlot.date == schedule.date).first()

        if not schedule.slots or len(schedule.slots) == 0:
            # Если слоты не выбраны, удаляем запись для данной даты
            if existing_slots:
                db.query(AvailableTimeSlot).filter(AvailableTimeSlot.date == schedule.date).delete()
                db.commit()

        # Если слоты выбраны, обновляем существующую запись
        if existing_slots:
            existing_slots.set_time_slots(schedule.slots)
        else:
            # Если записи не существует, создаем новую
            new_slot = AvailableTimeSlot(date=schedule.date)
            new_slot.set_time_slots(schedule.slots)
            db.add(new_slot)

        db.commit()
    
        return {"status": "success"}

@router.get("/schedules")
async def get_schedules():
    with get_db() as db:
        schedules = db.query(AvailableTimeSlot).all()
        response = {}
        for slot in schedules:
            response[slot.date] = slot.get_time_slots()
        
        return [{"date": date, "slots": times} for date, times in response.items()]
