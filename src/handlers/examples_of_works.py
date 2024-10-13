from aiogram import Router, types

from src.utils import get_photos
from src.keyboards import main_keyboard

router = Router()


@router.message(lambda message: message.text == "💅Примеры работ")
async def show_photo(message: types.Message):
    photos = get_photos()
    media = [types.InputMediaPhoto(media=photo.photo_url) for photo in photos]
    await message.answer_media_group(media, reply_markup=main_keyboard(message.from_user.id))
