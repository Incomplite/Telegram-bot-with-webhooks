from aiogram import BaseMiddleware
from aiogram.types import Update

from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from src.config import settings
from src.utils import delete_old_schedule_entries

jobstores = {
    'default': SQLAlchemyJobStore(url=settings.DATABASE_URL)
}

scheduler = AsyncIOScheduler(jobstores=jobstores)


class SchedulerMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Update, data: dict):
        # Пробрасываем управление дальше
        return await handler(event, data)


scheduler.add_job(delete_old_schedule_entries, "cron", hour=0)
