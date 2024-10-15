from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from src.config import settings

bot = Bot(
    token=settings.BOT_TOKEN,
    default=DefaultBotProperties(
        parse_mode=ParseMode.HTML
    )
)
dp = Dispatcher()


async def start_bot():
    await bot.send_message(settings.ADMIN_USER_ID, 'Бот запущен🥳.')


async def stop_bot():
    await bot.send_message(settings.ADMIN_USER_ID, 'Бот остановлен😔.')
