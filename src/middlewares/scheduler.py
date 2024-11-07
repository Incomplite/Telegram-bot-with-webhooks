from aiogram import BaseMiddleware
from aiogram.types import Update

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from src.utils import delete_old_schedule_entries

scheduler = AsyncIOScheduler()


class SchedulerMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Update, data: dict):
        # Пробрасываем управление дальше
        return await handler(event, data)


scheduler.add_job(delete_old_schedule_entries, "cron", hour=0)
