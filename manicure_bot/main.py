import asyncio
import logging

from aiogram import Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.fsm.storage.memory import MemoryStorage

from manicure_bot.keyboards import main_keyboard
from manicure_bot.bot_instance import bot
from manicure_bot.middlewares.scheduler import SchedulerMiddleware
from manicure_bot.main_router import router as main_router

logging.basicConfig(level=logging.INFO)

dp = Dispatcher(storage=MemoryStorage())


@dp.message(CommandStart())
async def start(msg: types.Message):
    welcome_text = (
        "🌸Добро пожаловать в бот для записи на маникюр!\n\n"
        "💅 Здесь вы можете легко и быстро записаться на маникюр.\n\n"
    )
    await msg.answer(welcome_text, reply_markup=main_keyboard(msg.from_user.id))


# Запуск процесса поллинга новых апдейтов
async def main():
    dp.include_router(main_router)
    dp.update.outer_middleware(SchedulerMiddleware())
    bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

if __name__ == '__main__':
    asyncio.run(main())
