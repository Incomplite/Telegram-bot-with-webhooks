from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from src.database import User
from src.database.db import get_db
from src.utils import greet_user

router = Router()


@router.message(CommandStart())
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
