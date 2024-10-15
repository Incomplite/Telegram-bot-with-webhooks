from aiogram import Router

from src.handlers.admin_router import admin_router
from src.handlers.contact import router as contact_router
from src.handlers.examples_of_works import router as examples_of_works_router
from src.handlers.services import router as services_router
from src.handlers.user_router import user_router

router = Router()

router.include_router(user_router)
router.include_router(admin_router)
router.include_router(contact_router)
router.include_router(examples_of_works_router)
router.include_router(services_router)
