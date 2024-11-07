from aiogram import Router

from src.bot.handlers.admin_router import router as admin_router
from src.bot.handlers.contact_router import router as contact_router
from src.bot.handlers.examples_of_works_router import router as examples_of_works_router
from src.bot.handlers.reminder_router import router as reminder_router
from src.bot.handlers.user_router import router as user_router

router = Router()

router.include_router(user_router)
router.include_router(admin_router)
router.include_router(contact_router)
router.include_router(examples_of_works_router)
router.include_router(reminder_router)
