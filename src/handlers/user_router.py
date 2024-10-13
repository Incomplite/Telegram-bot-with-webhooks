from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message

from src.utils import greet_user

from src.database import User
from src.database.db import get_db

user_router = Router()


@user_router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    """
    Обрабатывает команду /start.
    """
    with get_db() as db:
        user = db.query(User).filter(User.id == message.from_user.id).first()

        if not user:
            db.add(User(
                id=message.from_user.id,
                name=message.from_user.first_name,
                username=message.from_user.username
            ))
            db.commit()

    await greet_user(message, is_new_user=not user)


@user_router.message(F.text == '🔙 Назад')
async def cmd_back_home(message: Message) -> None:
    """
    Обрабатывает нажатие кнопки "Назад".
    """
    await greet_user(message, is_new_user=False)
