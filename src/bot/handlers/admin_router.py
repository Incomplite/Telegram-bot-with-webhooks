from aiogram import F, Router
from aiogram.types import Message

from src.bot.keyboards import admin_keyboard
from src.config import settings

router = Router()


@router.message(F.text == '🔑Админ панель', F.from_user.id.in_([settings.ADMIN_USER_ID]))
async def admin_panel(message: Message):
    await message.answer(
        f"Здравствуйте, <b>{message.from_user.full_name}</b>!\n\n"
        "Добро пожаловать в панель администратора. Здесь вы можете:\n"
        "• Просматривать и управлять всеми текущими записями\n"
        "• Составлять расписание\n"
        "• Просматривать и редактировать услуги\n\n"
        "Для доступа к полному функционалу, пожалуйста, перейдите по ссылке ниже.",
        reply_markup=admin_keyboard(user_id=message.from_user.id)
    )
