from aiogram.types import ReplyKeyboardMarkup, WebAppInfo, InlineKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from urllib.parse import quote  # Импортируем для кодирования URL

from src.config import settings


def main_keyboard(user_id: int, first_name: str) -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    url_appointments = f"{settings.BASE_SITE}/appointments?user_id={user_id}"
    url_add_appointment = f'{settings.BASE_SITE}/form?user_id={user_id}&first_name={quote(first_name)}'
    kb.button(text="🌐 Мои заявки", web_app=WebAppInfo(url=url_appointments))
    kb.button(text="📝 Оставить заявку", web_app=WebAppInfo(url=url_add_appointment))
    kb.button(text="ℹ️ О нас")
    if user_id == settings.ADMIN_USER_ID:
        kb.button(text="🔑 Админ панель")
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)


def back_keyboard() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="🔙 Назад")
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)


def admin_keyboard(user_id: int) -> InlineKeyboardMarkup:
    url_appointments = f"{settings.BASE_SITE}/admin?admin_id={user_id}"
    kb = InlineKeyboardBuilder()
    kb.button(text="🏠 На главную", callback_data="back_home")
    kb.button(text="📝 Смотреть заявки", web_app=WebAppInfo(url=url_appointments))
    kb.adjust(1)
    return kb.as_markup()


def app_keyboard(user_id: int, first_name: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    url_add_application = f'{settings.BASE_SITE}/form?user_id={user_id}&first_name={first_name}'
    kb.button(text="📝 Оставить заявку", web_app=WebAppInfo(url=url_add_application))
    kb.adjust(1)
    return kb.as_markup()
