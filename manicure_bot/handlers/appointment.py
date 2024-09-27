from datetime import datetime, timedelta

from aiogram import types, Router
from aiogram.types import CallbackQuery, InlineKeyboardButton
from aiogram_calendar import SimpleCalendarCallback, get_user_locale
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext

from manicure_bot.keyboards import main_keyboard
from manicure_bot.bot_instance import bot
from manicure_bot.config import settings
from manicure_bot.database import User, Appointment, Service
from manicure_bot.database.db import get_db
from manicure_bot.handlers.states import Registration
from manicure_bot.handlers.registration_user import request_user_info
from manicure_bot.handlers.registration_user import router as registration_router
from manicure_bot.utils import delete_appointment_job
from manicure_bot.custom_calendar import CustomSimpleCalendar
from manicure_bot.utils import get_available_time_slots
from manicure_bot.middlewares.scheduler import scheduler

router = Router()

router.include_router(registration_router)


@router.message(lambda message: message.text == "📝Записаться")
async def book_appointment(msg: types.Message):
    with get_db() as db:
        services = db.query(Service).all()

        keyboard = InlineKeyboardBuilder()
        for service in services:
            button = InlineKeyboardButton(text=service.name, callback_data=f"toggle_service_{service.id}")
            keyboard.add(button)
        
        confirm_button = InlineKeyboardButton(text="✅Подтвердить", callback_data="confirm_services")
        back_button = InlineKeyboardButton(text="Назад", callback_data="back_to_main")
        keyboard.add(confirm_button, back_button)

        keyboard.adjust(1)
        await msg.answer("Выберите услуги для записи:", reply_markup=keyboard.as_markup())


# Обработчик для выбора/отмены услуги
@router.callback_query(lambda callback_query: callback_query.data.startswith("toggle_service_"))
async def toggle_service(callback_query: types.CallbackQuery, state: FSMContext):
    service_id = int(callback_query.data.split("_")[2])
    user_data = await state.get_data()
    selected_services = user_data.get("selected_services", [])

    if service_id in selected_services:
        selected_services.remove(service_id)
    else:
        selected_services.append(service_id)

    await state.update_data(selected_services=selected_services)

    # Обновляем клавиатуру с учетом выбранных услуг
    with get_db() as db:
        services = db.query(Service).all()
        keyboard = InlineKeyboardBuilder()
        for service in services:
            if service.id in selected_services:
                button_text = f"✅{service.name}"
            else:
                button_text = service.name
            button = InlineKeyboardButton(text=button_text, callback_data=f"toggle_service_{service.id}")
            keyboard.add(button)

        confirm_button = InlineKeyboardButton(text="✅Подтвердить", callback_data="confirm_services")
        back_button = InlineKeyboardButton(text="Назад", callback_data="back_to_main")
        keyboard.add(confirm_button, back_button)

        keyboard.adjust(1)

        await callback_query.message.edit_reply_markup(reply_markup=keyboard.as_markup())
    await callback_query.answer("Услуга обновлена")


# Обработчик для подтверждения выбора услуг
@router.callback_query(lambda callback_query: callback_query.data.startswith("confirm_services"))
async def confirm_services(callback_query: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    selected_services = user_data.get("selected_services", [])

    if not selected_services:
        await callback_query.answer("Вы не выбрали ни одной услуги", show_alert=True)
        return

    await callback_query.message.edit_reply_markup(reply_markup=None)
    await callback_query.message.answer("Пожалуйста, выберите дату:", reply_markup=await CustomSimpleCalendar(locale=await get_user_locale(callback_query.from_user)).start_calendar())


@router.callback_query(SimpleCalendarCallback.filter())
async def process_simple_calendar(callback_query: CallbackQuery, callback_data: CallbackData, state: FSMContext):
    with get_db() as db:
        today = datetime.now()
        start_date = today + timedelta(days=1)  # послезавтра
        end_date = start_date + timedelta(days=30)  # на месяц вперед

        calendar = CustomSimpleCalendar(
            locale=await get_user_locale(callback_query.from_user), show_alerts=True
        )
        calendar.set_dates_range(start_date, end_date)

        selected, date = await calendar.process_selection(callback_query, callback_data)
        if selected:
            available_times = get_available_time_slots(date, db)
            
            builder = InlineKeyboardBuilder()
            for time in available_times:
                builder.add(types.InlineKeyboardButton(
                    text=time, 
                    callback_data=f"time_{time}"
                ))
            builder.adjust(4)

            await state.update_data(selected_date=date)

            await callback_query.message.answer(
                f'Вы выбрали {date.strftime("%d/%m/%Y")}. Пожалуйста, выберите удобное для Вас время:',
                reply_markup=builder.as_markup()
            )

            user_data = await state.get_data()
            if "selected_appointment_id" in user_data:
                appointment_id = user_data['selected_appointment_id']
                appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
                if appointment:
                    appointment.date = date
                    db.commit()


@router.callback_query(lambda c: c.data.startswith("time_"))
async def select_time(callback_query: CallbackQuery, state: FSMContext):
    with get_db() as db:
        time_str = callback_query.data.split("_")[1]
        time_obj = datetime.strptime(time_str, "%H:%M").time()

        user_data = await state.get_data()

        user_id = callback_query.from_user.id
        user = db.query(User).filter(User.user_id == user_id).first()
        await state.update_data(selected_time=time_obj)

        if "selected_appointment_id" in user_data:
            appointment_id = user_data['selected_appointment_id']
            appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
            if appointment:
                await state.update_data(name=user.name, phone_number=user.phone_number, selected_time=time_obj)
                await confirm_appointment_with_user_data(callback_query.message, state, user)
        else:
            if user:
                await state.update_data(name=user.name, phone_number=user.phone_number, selected_time=time_obj)
                await confirm_appointment_with_user_data(callback_query.message, state, user)
            else:
                await request_user_info(callback_query.message, state)

        await callback_query.message.edit_reply_markup(reply_markup=None)


async def confirm_appointment_with_user_data(msg: types.Message, state: FSMContext, user: User):
    user_data = await state.get_data()
    date_str = user_data['selected_date'].strftime("%d/%m/%Y")
    time_str = user_data['selected_time'].strftime("%H:%M")
    phone_number = user.phone_number
    name = user.name

    with get_db() as db:
        services = db.query(Service).filter(Service.id.in_(user_data['selected_services'])).all()
        service_names = ", ".join([service.name for service in services])
        service_prices = sum([service.price for service in services])

    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="✅Подтвердить запись", callback_data="confirm_appointment"))
    builder.add(InlineKeyboardButton(text="Изменить данные", callback_data="change_data"))

    answer_message = (
        f"Проверьте ваши данные:\n\nУслуга: {service_names}\nДата: {date_str}\nВремя: {time_str}\nИмя: {name}\nТелефон: {phone_number}\nЦена: {service_prices} руб."
        "\n\nЕсли все верно, нажмите 'Подтвердить запись'.\nЕсли нужно изменить данные, нажмите 'Изменить данные'."
    )

    await msg.answer(
        answer_message,
        reply_markup=builder.as_markup()
    )
    await state.set_state(Registration.waiting_for_confirmation)


@router.callback_query(lambda c: c.data == "change_data")
async def change_data(callback_query: CallbackQuery, state: FSMContext):
    await request_user_info(callback_query.message, state)
    await callback_query.message.edit_reply_markup(reply_markup=None)


@router.callback_query(lambda c: c.data == "confirm_appointment")
async def confirm_appointment(callback_query: CallbackQuery, state: FSMContext):
    with get_db() as db:
        user_data = await state.get_data()
        user_id = callback_query.from_user.id

        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            user = User(user_id=user_id, name=user_data['name'], phone_number=user_data['phone_number'])
            db.add(user)
        else:
            user.name = user_data['name']
            user.phone_number = user_data['phone_number']

        selected_services_ids = user_data['selected_services']
        selected_services = db.query(Service).filter(Service.id.in_(selected_services_ids)).all()

        if "selected_appointment_id" in user_data:
            appointment_id = user_data["selected_appointment_id"]
            appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
            if appointment:
                appointment.date = user_data['selected_date']
                appointment.time = user_data['selected_time']
                appointment.services = selected_services
                action_message = "Ваша запись была успешно изменена"
        else:
            appointment = Appointment(
                user_id=user_id,
                date=user_data['selected_date'],
                time=user_data['selected_time'],
                services=selected_services
            )
            db.add(appointment)
            action_message = "Ваша запись на маникюр подтверждена"

        db.commit()

        # Добавляем задачу на удаление записи через 0.5 минуты (Нужно изменить)
        # appointment_id = appointment.id
        # deletion_time = datetime.now() + timedelta(minutes=0.5)
        # scheduler.add_job(delete_appointment_job, "date", run_date=deletion_time, args=[appointment_id])

        date_str = appointment.date.strftime("%d/%m/%Y")
        time_str = appointment.time.strftime("%H:%M")
        await callback_query.message.answer(f'{action_message}: {date_str} в {time_str}.', reply_markup=main_keyboard(user_id))
        await callback_query.message.answer("Спасибо, что выбрали Нас!")

        # master_message = f'Новая запись на маникюр: {date_str} в {time_str}. Клиент: {user.name}, телефон: {user.phone_number}.'
        # await bot.send_message(chat_id=settings.master_chat_id, text=master_message)
        await state.clear()

    await callback_query.message.edit_reply_markup(reply_markup=None)
