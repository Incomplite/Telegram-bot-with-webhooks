from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from src.api.dao import UserDAO
from src.utils import greet_user

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    """
    Обрабатывает команду /start.
    """
    user = await UserDAO.find_one_or_none(id=message.from_user.id)

    if not user:
        user = UserDAO.add(
            id=message.from_user.id,
            name=message.from_user.first_name,
            username=message.from_user.username
        )

    await greet_user(message, is_new_user=not user)
