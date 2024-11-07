from aiogram import F, Router, types

from src.bot.keyboards import main_keyboard
from src.utils import get_photos

router = Router()


@router.message(F.text == "💅Примеры работ")
async def show_photo(message: types.Message):
    photos = get_photos()
    media = [types.InputMediaPhoto(media=photo.photo_url) for photo in photos]
    await message.answer("Вот фото нескольких работ:")
    await message.answer_media_group(media, reply_markup=main_keyboard(
        user_id=message.from_user.id,
        first_name=message.from_user.first_name)
    )
