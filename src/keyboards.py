from urllib.parse import quote  # Импортируем для кодирования URL

from aiogram.types import (
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    WebAppInfo
)
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from src.config import settings


def main_keyboard(user_id: int, first_name: str) -> ReplyKeyboardMarkup:
    url_appointments = f"{settings.BASE_SITE}/appointments?user_id={user_id}"
    url_add_appointment = f'{settings.BASE_SITE}/form?user_id={user_id}&first_name={quote(first_name)}'
    keyboard = [
        [
            KeyboardButton(text="🌸Услуги"),
            KeyboardButton(text="📝Записаться", web_app=WebAppInfo(url=url_add_appointment)),
            KeyboardButton(text="📅Мои записи", web_app=WebAppInfo(url=url_appointments))
        ],
        [
            KeyboardButton(text="💅Примеры работ"),
            KeyboardButton(text="☎️Контакты")
        ],
        [
            KeyboardButton(text="💡Идеи дизайна ногтей")
        ]
    ]

    if user_id == settings.ADMIN_USER_ID:
        keyboard.append([
            KeyboardButton(text="🔑Админ панель")
        ])

    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


def back_keyboard() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="🔙Назад")
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)


def admin_keyboard(user_id: int) -> InlineKeyboardMarkup:
    url_appointments = f"{settings.BASE_SITE}/admin/appointments?admin_id={user_id}"
    url_time_slots = f"{settings.BASE_SITE}/admin/set-time-slots?admin_id={user_id}"
    kb = InlineKeyboardBuilder()
    kb.button(text="🏠На главную", callback_data="back_home")
    kb.button(text="📝Посмотреть все записи", web_app=WebAppInfo(url=url_appointments))
    kb.button(text="Составить расписание", web_app=WebAppInfo(url=url_time_slots))
    kb.adjust(1)
    return kb.as_markup()


def app_keyboard(user_id: int, first_name: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    url_add_application = f'{settings.BASE_SITE}/form?user_id={user_id}&first_name={first_name}'
    kb.button(text="📝Оставить заявку", web_app=WebAppInfo(url=url_add_application))
    kb.adjust(1)
    return kb.as_markup()


def contact_button() -> InlineKeyboardMarkup:
    inline_kb = InlineKeyboardBuilder()
    inline_kb.button(text="☎️Посмотреть контакты", callback_data="contact_info")
    return inline_kb.as_markup()
