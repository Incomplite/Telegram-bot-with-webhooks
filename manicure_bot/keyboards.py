from aiogram import types

from manicure_bot.config import settings

def main_keyboard(user_id):
    if user_id == settings.master_user_id:
        kb = [
            [
                types.KeyboardButton(text="🌸Услуги"),
                types.KeyboardButton(text="📝Записаться"),
                types.KeyboardButton(text="📅Мои записи")
            ],
            [
                types.KeyboardButton(text="💅Примеры работ"),
                types.KeyboardButton(text="☎️Контакты")
            ],
            [
                types.KeyboardButton(text="💡Идеи для маникюра"),
                types.KeyboardButton(text="Доступные команды")
            ]
        ]
    else:
        kb = [
            [
                types.KeyboardButton(text="🌸Услуги"),
                types.KeyboardButton(text="📝Записаться"),
                types.KeyboardButton(text="📅Мои записи")
            ],
            [
                types.KeyboardButton(text="💅Примеры работ"),
                types.KeyboardButton(text="☎️Контакты")
            ],
            [
                types.KeyboardButton(text="💡Идеи дизайна ногтей")
            ]
        ]
    return types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Выберите, что вам подходит",
        one_time_keyboard=True
    )
