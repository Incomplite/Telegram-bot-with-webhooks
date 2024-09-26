from aiogram import types, Router
from aiogram.utils.markdown import hide_link

from manicure_bot.keyboards import main_keyboard
router = Router()


# Обработчик команды "Услуги"
@router.message(lambda message: message.text == "☎️Контакты")
async def send_contact_info(message: types.Message):
    contact_info = (
        f"{hide_link('https://yandex.ru/maps/39/rostov-na-donu/house/gorsovetskaya_ulitsa_49s1/Z0AYcQBnQUcEQFptfX51c39nZw')}"
        "Ваш мастер маникюра: Кристина\n\n"
        "Телефон: 89045045661\n\n"
        "Telegram: @Uniccornn\n\n"
        "Адрес: ул. Горсоветская, д.49/1"
        
    )
    await message.answer(contact_info, reply_markup=main_keyboard(message.from_user.id))
