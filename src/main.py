import logging

from contextlib import asynccontextmanager

from aiogram.types import Update

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles

from src.bot.bot_instance import bot, dp, start_bot, stop_bot
from src.config import settings
from src.main_router import router as main_router
from src.pages.router import router as router_pages
from src.api.router import router as router_api

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Код, выполняющийся при запуске приложения
    logging.info("Starting bot setup...")
    dp.include_router(main_router)
    await start_bot()
    webhook_url = settings.get_webhook_url()  # Получаем URL вебхука
    await bot.set_webhook(
        url=webhook_url,
        allowed_updates=dp.resolve_used_update_types(),
        drop_pending_updates=True
    )
    logging.info(f"Webhook set to {webhook_url}")
    yield  # Приложение работает
    # Код, выполняющийся при завершении работы приложения
    logging.info("Shutting down bot...")
    await bot.delete_webhook()
    await stop_bot()
    logging.info("Webhook deleted")

# Инициализация FastAPI с методом жизненного цикла
app = FastAPI(lifespan=lifespan)

app.mount('/static', StaticFiles(directory='src/static'), 'static')


# Маршрут для обработки вебхуков
@app.post("/webhook")
async def webhook(request: Request) -> None:
    logging.info("Received webhook request")
    update = Update.model_validate(await request.json(), context={"bot": bot})
    # Обрабатываем обновление через диспетчер (dp) и передаем в бот
    await dp.feed_update(bot, update)
    logging.info("Update processed")

app.include_router(router_pages)
app.include_router(router_api)