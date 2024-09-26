from aiogram import Router

from manicure_bot.handlers.appointment import router as booking_router
from manicure_bot.handlers.change_appointment import router as change_booking_router
from manicure_bot.handlers.admin_commands import router as admin_router
from manicure_bot.handlers.services import router as services_router
from manicure_bot.handlers.contact import router as contact_router

router = Router()

router.include_router(booking_router)
router.include_router(change_booking_router)
router.include_router(admin_router)
router.include_router(services_router)
router.include_router(contact_router)
