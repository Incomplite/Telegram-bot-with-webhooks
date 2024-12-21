from aiogram import BaseMiddleware
from aiogram.types import Update

from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler

import pytz

from src.config import settings
from src.utils import delete_old_schedule_entries

MOSCOW_TZ = pytz.timezone("Europe/Moscow")

scheduler = AsyncIOScheduler(timezone=MOSCOW_TZ)


class SchedulerMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Update, data: dict):
        # Пробрасываем управление дальше
        return await handler(event, data)


scheduler.add_job(delete_old_schedule_entries, "cron", hour=0)
