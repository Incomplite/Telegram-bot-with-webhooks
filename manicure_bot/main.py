import asyncio
import logging

from aiogram import Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage

from manicure_bot.handlers.booking import router as booking_router
from manicure_bot.handlers.change_booking import router as change_booking_router
from manicure_bot.handlers.admin_commands import router as admin_router

from manicure_bot.utils import keyboard

from manicure_bot.bot_instance import bot

logging.basicConfig(level=logging.INFO)

dp = Dispatcher(storage=MemoryStorage())


@dp.message(Command("start"))
async def start(msg: types.Message):
    welcome_text = (
        "Добро пожаловать в бот для записи на маникюр!\n\n"
        "💅 Здесь вы можете легко и быстро записаться на маникюр.\n\n"
    )
    await msg.answer(welcome_text, reply_markup=keyboard)


# Запуск процесса поллинга новых апдейтов
async def main():
    dp.include_router(booking_router)
    dp.include_router(change_booking_router)
    dp.include_router(admin_router)
    bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

if __name__ == '__main__':
    asyncio.run(main())
