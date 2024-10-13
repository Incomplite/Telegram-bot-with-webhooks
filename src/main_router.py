from aiogram import Router

from src.handlers.user_router import user_router
from src.handlers.admin_router import admin_router

router = Router()

router.include_router(user_router)
router.include_router(admin_router)
