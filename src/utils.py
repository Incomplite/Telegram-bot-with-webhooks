from datetime import datetime, timedelta

from aiogram.types import Message

from src.bot.keyboards import main_keyboard
from src.database import AvailableTimeSlot, Photo
from src.database.db import get_db


def get_photos():
    with get_db() as db:
        photos = db.query(Photo).all()
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
    print(f"Запуск задачи на удаление записей старше {threshold_date}")
    with get_db() as db:
        db.query(AvailableTimeSlot).filter(AvailableTimeSlot.date < threshold_date).delete()
        db.commit()
    print("Старые записи успешно удалены.")
