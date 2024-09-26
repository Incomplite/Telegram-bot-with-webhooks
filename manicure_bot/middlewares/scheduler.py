from aiogram import BaseMiddleware
from aiogram.types import Update

from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Планировщик
scheduler = AsyncIOScheduler()


class SchedulerMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Update, data: dict):
        # Запускаем планировщик, если он ещё не запущен
        if not scheduler.running:
            scheduler.start()
            print("Scheduler started")

        # Пробрасываем управление дальше
        return await handler(event, data)
