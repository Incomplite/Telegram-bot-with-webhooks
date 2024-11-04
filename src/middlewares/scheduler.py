from aiogram import BaseMiddleware
from aiogram.types import Update

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.schedulers.background import BackgroundScheduler

# Планировщик
scheduler = AsyncIOScheduler()


class SchedulerMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Update, data: dict):
        # Пробрасываем управление дальше
        return await handler(event, data)
