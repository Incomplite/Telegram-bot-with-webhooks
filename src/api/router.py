from datetime import date, datetime, timedelta

from fastapi import APIRouter, HTTPException
from fastapi.requests import Request
from fastapi.responses import JSONResponse

from src.api.schemas import AppointmentData, Schedule, ServiceData, ServiceResponse
from src.api.utils import archive_appointment
from src.bot.bot_instance import bot
from src.bot.handlers.reminder_router import schedule_reminder
from src.bot.keyboards import contact_button, main_keyboard
from src.config import settings
from src.database import Appointment, AvailableTimeSlot, Service, User
from src.database.db import get_db
from src.database.models import AppointmentStatus
from src.middlewares.scheduler import scheduler

router = APIRouter(prefix='/api', tags=['API'])


@router.post("/appointment", response_class=JSONResponse)
async def create_appointment(request: Request):
    # Получаем и валидируем JSON данные
    data = await request.json()
    validated_data = AppointmentData(**data)

    # Форматируем время
    formatted_time = validated_data.appointment_time.strftime("%H:%M")
    formatted_date = validated_data.appointment_date.strftime("%d.%m.%Y")

    with get_db() as db:
        user = db.query(User).filter(User.id == validated_data.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")

    # Формируем сообщение для пользователя
    message = (
        f"🎉 <b>{validated_data.name}, ваша запись успешно принята!</b>\n\n"
        "💬 <b>Информация о вашей записи:</b>\n"
        f"👤 <b>Имя клиента:</b> {validated_data.name}\n"
        f"💅 <b>Услуги:</b> {', '.join(validated_data.services)}\n"
        f"📅 <b>Дата записи:</b> {formatted_date}\n"
        f"⏰ <b>Время записи:</b> {formatted_time}\n"
        f"💰 <b>Общая стоимость:</b> {validated_data.total_price} руб.\n\n"
    )
    contact_message = (
        "Спасибо за Вашу запись! ✨\n"
        "За день до Вашего прихода, Вам будет отправлено подтверждение.\nНе забудьте ответить.🌼"
        "\nЕсли Вы захотите отменить запись раньше, сообщите мастеру об этом."
    )

    # Сообщение администратору
    admin_message = (
        "🔔 <b>Новая запись!</b>\n\n"
        "📄 <b>Детали заявки:</b>\n"
        f"👤 Имя клиента: {validated_data.name}\n"
        f"💅 Услуги: {', '.join(validated_data.services)}\n"  # Изменение: выводим все услуги
        f"📅 Дата: {formatted_date}\n"
        f"⏰ Время: {formatted_time}\n"
        f"💰 <b>Общая стоимость:</b> {validated_data.total_price} руб.\n\n"
        f"<b>Пользователь:</b> @{user.username}\n"
    )

    # Добавление заявки в базу данных
    with get_db() as db:
        appointment = Appointment(
            user_id=validated_data.user_id,
            name=validated_data.name,
            date=validated_data.appointment_date,
            time=validated_data.appointment_time,
            total_price=validated_data.total_price,
            status=AppointmentStatus.ACTIVE.value
        )
        db.add(appointment)
        db.commit()  # Сохраняем изменения

        # Добавление услуг в ассоциативную таблицу
        for service_name in validated_data.services:
            service = db.query(Service).filter(Service.name == service_name).first()
            if service:
                appointment.services.append(service)  # Добавляем услуги к записи

        db.commit()  # Сохраняем изменения с услугами

        change_time = datetime.combine(
            validated_data.appointment_date,
            validated_data.appointment_time
        ) + timedelta(hours=2)
        scheduler.add_job(archive_appointment, "date", run_date=change_time, args=[appointment.id])
        schedule_reminder(appointment)

    kb = main_keyboard(user_id=validated_data.user_id, first_name=validated_data.name)
    inline_kb = contact_button()
    # Отправка сообщений через бота
    await bot.send_message(chat_id=validated_data.user_id, text=message, reply_markup=kb)
    await bot.send_message(chat_id=validated_data.user_id, text=contact_message, reply_markup=inline_kb)
    await bot.send_message(chat_id=settings.ADMIN_USER_ID, text=admin_message)

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
    with get_db() as db:
        slot = db.query(AvailableTimeSlot).filter(AvailableTimeSlot.date == date).first()
        if slot:
            return {"slots": slot.get_time_slots()}
        return JSONResponse(status_code=404, content={"message": "Слоты не найдены"})


@router.get("/available-slots/{date}")
async def get_available_slots(date: date):
    with get_db() as db:
        slot = db.query(AvailableTimeSlot).filter(AvailableTimeSlot.date == date).first()
        # Отфильтровываем уже забронированные места
        booked_times = db.query(Appointment.time).filter(Appointment.date == date).all()
        booked_times = {t[0].strftime("%H:%M") for t in booked_times}
        # Удаляем забронированные слоты из списка доступных слотов
        if slot:
            available_slots = [time for time in slot.get_time_slots() if time not in booked_times]
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


@router.post("/services", response_model=ServiceResponse, status_code=201)
async def create_service(request: Request):
    data = await request.json()
    validated_data = ServiceData(**data)
    service = Service(
        name=validated_data.name,
        price=validated_data.price,
        duration=validated_data.duration,
        description=validated_data.description
    )

    with get_db() as db:
        db.add(service)
        db.commit()
        db.refresh(service)

    return service


@router.put("/services/{service_id}", response_model=ServiceResponse, status_code=200)
async def update_service(service_id: int, request: Request):
    data = await request.json()

    with get_db() as db:
        service = db.query(Service).filter(Service.id == service_id).first()
        if not service:
            raise HTTPException(status_code=404, detail="Service not found")

        service.name = data['name']
        service.price = data['price']
        service.duration = data['duration']
        service.description = data['description']

        db.commit()
        db.refresh(service)

    return service


@router.delete("/services/{service_id}")
async def delete_service(service_id: int):
    with get_db() as db:
        service = db.query(Service).filter(Service.id == service_id).first()
        if service:
            db.delete(service)
            db.commit()
            return JSONResponse(status_code=200, content={"message": "Услуга удалена"})
        return JSONResponse(status_code=404, content={"message": "Услуга не найдена"})
