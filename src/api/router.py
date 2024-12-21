from datetime import date, datetime, timedelta

from fastapi import APIRouter, HTTPException
from fastapi.requests import Request
from fastapi.responses import JSONResponse

from src.api.dao import AppointmentDAO, AvailableTimeSlotDAO, ServiceDAO, UserDAO

from src.api.schemas import AppointmentData, Schedule, ServiceData
from src.api.utils import archive_appointment
from src.bot.bot_instance import bot
from src.bot.handlers.reminder_router import schedule_reminder
from src.bot.keyboards import contact_button, main_keyboard
from src.config import settings
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

    user = await UserDAO.find_one_or_none(id=validated_data.user_id)
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
    appointment = await AppointmentDAO.add(
        user_id=validated_data.user_id,
        name=validated_data.name,
        date=validated_data.appointment_date,
        time=validated_data.appointment_time,
        total_price=validated_data.total_price,
        status=AppointmentStatus.ACTIVE.value
    )

    # Добавление услуг к заявке
    for service_name in validated_data.services:
        service = await ServiceDAO.find_one_or_none(name=service_name)
        if service:
            await AppointmentDAO.add_service(appointment.id, service)

    change_time = datetime.combine(
        validated_data.appointment_date,
        validated_data.appointment_time
    ) + timedelta(hours=2)
    # + timedelta(hours=2)
    scheduler.add_job(archive_appointment, "date", run_date=change_time, args=[appointment.id])
    schedule_reminder(appointment)

    kb = main_keyboard(user_id=validated_data.user_id, first_name=validated_data.name)
    inline_kb = contact_button()
    # Отправка сообщений через бота
    await bot.send_message(chat_id=validated_data.user_id, text=message, reply_markup=kb)
    await bot.send_message(chat_id=validated_data.user_id, text=contact_message, reply_markup=inline_kb)
    await bot.send_message(chat_id=settings.MASTER_CHAT_ID, text=admin_message)

    # Возвращаем успешный ответ
    return {"message": "success!"}


@router.delete("/appointment/{appointment_id}")
async def delete_appointment(appointment_id: int):
    is_deleted = await AppointmentDAO.delete_with_services(appointment_id)
    if is_deleted:
        return JSONResponse(status_code=200, content={"message": "Запись удалена"})
    return JSONResponse(status_code=404, content={"message": "Запись не найдена"})


@router.get("/all-slots/{date}")
async def get_all_slots(date: date):
    slot = await AvailableTimeSlotDAO.find_one_or_none(date=date)
    if slot:
        return {"slots": slot.get_time_slots()}
    return JSONResponse(status_code=404, content={"message": "Слоты не найдены"})


@router.get("/available-slots/{date}")
async def get_available_slots(date: date):
    slot = await AvailableTimeSlotDAO.find_one_or_none(date=date)
    if slot:
        # Отфильтровываем уже забронированные места
        booked_times = await AppointmentDAO.find_all(date=date)
        booked_times = {time.time.strftime("%H:%M") for time in booked_times}
        available_slots = [time for time in slot.get_time_slots() if time not in booked_times]
        return {"slots": available_slots}
    return JSONResponse(status_code=404, content={"message": "Слоты не найдены"})


@router.post("/schedule")
async def save_schedule(schedule: Schedule):
    if not schedule.slots or len(schedule.slots) == 0:
        # Если слоты не выбраны, удаляем запись для данной даты
        await AvailableTimeSlotDAO.delete(date=schedule.date)
        return {"status": "deleted"}

    # Если слоты выбраны, добавляем или обновляем запись
    await AvailableTimeSlotDAO.add_or_update(schedule.date, schedule.slots)
    return {"status": "success"}


@router.get("/schedules")
async def get_schedules():
    schedules = await AvailableTimeSlotDAO.find_all()
    response = {}
    for slot in schedules:
        response[slot.date] = slot.get_time_slots()

    return [{"date": date, "slots": times} for date, times in response.items()]


@router.post("/services", status_code=201)
async def create_service(request: Request):
    data = await request.json()
    validated_data = ServiceData(**data)
    service = await ServiceDAO.add(
        name=validated_data.name,
        price=validated_data.price,
        duration=validated_data.duration,
        description=validated_data.description
    )

    if not service:
        raise HTTPException(status_code=400, detail="Failed to create service")

    return service


@router.put("/services/{service_id}", status_code=200)
async def update_service(service_id: int, request: Request):
    data = await request.json()

    # Найти существующую услугу
    service = await ServiceDAO.find_one_or_none(id=service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    # Обновить атрибуты
    for key, value in data.items():
        setattr(service, key, value)

    # Сохранить изменения
    result = await ServiceDAO.update(service_id, **data)  # Убедитесь, что передаете нужные данные
    if result:
        return await ServiceDAO.find_one_or_none(id=service_id)  # Возвращаем обновленную запись
    else:
        raise HTTPException(status_code=500, detail="Failed to update service")


@router.delete("/services/{service_id}")
async def delete_service(service_id: int):
    service = await ServiceDAO.delete(id=service_id)
    if service:
        return JSONResponse(status_code=200, content={"message": "Услуга удалена"})
    return JSONResponse(status_code=404, content={"message": "Услуга не найдена"})
