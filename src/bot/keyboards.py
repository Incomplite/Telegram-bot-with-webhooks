from urllib.parse import quote  # Импортируем для кодирования URL

from aiogram.types import (
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    WebAppInfo
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.config import settings


def main_keyboard(user_id: int, first_name: str) -> ReplyKeyboardMarkup:
    url_appointments = f"{settings.BASE_SITE}/appointments?user_id={user_id}"
    url_add_appointment = f'{settings.BASE_SITE}/form?user_id={user_id}&first_name={quote(first_name)}'
    url_services = f"{settings.BASE_SITE}/services?user_id={user_id}"
    keyboard = [
        [
            KeyboardButton(text="📝Записаться", web_app=WebAppInfo(url=url_add_appointment)),
            KeyboardButton(text="📅Мои записи", web_app=WebAppInfo(url=url_appointments))
        ],
        [
            KeyboardButton(text="🌸Прайс-лист", web_app=WebAppInfo(url=url_services)),
            KeyboardButton(text="💅Примеры работ")
        ],
        [
            KeyboardButton(text="💡Идеи дизайна маникюра", web_app=WebAppInfo(url="https://pin.it/36Pvqck0n"))
        ],
        [
            KeyboardButton(text="☎️Контакты")
        ]
    ]

    if user_id == settings.MASTER_USER_ID:
        keyboard.append([
            KeyboardButton(text="🔑Админ панель")
        ])

    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


def admin_keyboard(user_id: int) -> InlineKeyboardMarkup:
    url_appointments = f"{settings.BASE_SITE}/admin/appointments?admin_id={user_id}"
    url_time_slots = f"{settings.BASE_SITE}/admin/set-time-slots?admin_id={user_id}"
    url_services = f"{settings.BASE_SITE}/admin/services?admin_id={user_id}"
    kb = InlineKeyboardBuilder()
    kb.button(text="📝Посмотреть все записи", web_app=WebAppInfo(url=url_appointments))
    kb.button(text="📅Составить расписание", web_app=WebAppInfo(url=url_time_slots))
    kb.button(text="🌸Прайс-лист", web_app=WebAppInfo(url=url_services))
    kb.adjust(1)
    return kb.as_markup()


def contact_button() -> InlineKeyboardMarkup:
    inline_kb = InlineKeyboardBuilder()
    inline_kb.button(text="☎️Посмотреть контакты", callback_data="contact_info")
    return inline_kb.as_markup()
