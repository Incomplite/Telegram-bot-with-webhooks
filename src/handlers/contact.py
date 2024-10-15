from aiogram import F, Router, types
from aiogram.utils.markdown import hide_link

from src.keyboards import main_keyboard

router = Router()


# Обработчик команды "Услуги"
@router.message(F.text == "☎️Контакты")
async def send_contact_info(message: types.Message):
    contact_info = (
        f"{hide_link('https://yandex.ru/maps/39/rostov-na-donu/house/gorsovetskaya_ulitsa_49s1/Z0AYcQBnQUcEQFptfX51c39nZw')}"
        "Ваш мастер маникюра: Кристина\n\n"
        "Телефон: 89045045661\n\n"
        "Telegram: @Uniccornn\n\n"
        "Адрес: ул. Горсоветская, д.49/1"

    )
    await message.answer(contact_info, reply_markup=main_keyboard(
        user_id=message.from_user.id,
        first_name=message.from_user.first_name)
    )
