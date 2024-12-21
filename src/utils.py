from datetime import datetime, timedelta

from aiogram.types import Message

from src.api.dao import PhotoDAO, AvailableTimeSlotDAO
from src.bot.keyboards import main_keyboard


async def get_photos():
    photos = await PhotoDAO.find_all()
    return photos


async def greet_user(message: Message, is_new_user: bool) -> None:
    """
    Приветствует пользователя и отправляет соответствующее сообщение.
    """
    greeting = "Добро пожаловать" if is_new_user else "С возвращением"
    status = "\nХотели ли бы Вы совершить свою первую запись?🌼" if is_new_user else "\nРад видеть Вас снова!"
    message_text = f"{greeting}, <b>{message.from_user.full_name}</b>! {status}"
    if not is_new_user:
        message_text += "\nЧем я могу Вам помочь?🌼"
    await message.answer(
        message_text,
        reply_markup=main_keyboard(user_id=message.from_user.id, first_name=message.from_user.first_name)
    )


async def delete_old_schedule_entries():
    threshold_date = datetime.now().date() + timedelta(days=1)
    await AvailableTimeSlotDAO.delete(date__lt=threshold_date)
