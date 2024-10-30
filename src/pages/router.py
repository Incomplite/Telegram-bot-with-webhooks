from fastapi import APIRouter
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from sqlalchemy.orm import joinedload

from src.config import settings
from src.database import Appointment, Service, User
from src.database.db import get_db

router = APIRouter(prefix='', tags=['Фронтенд'])
templates = Jinja2Templates(directory='src/templates')


@router.get("/", response_class=HTMLResponse)
async def get_home_page(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "title": "Маникюр бот"}
    )


@router.get("/form", response_class=HTMLResponse)
async def get_service_form(request: Request, user_id: int = None, first_name: str = None):
    with get_db() as db:
        services = db.query(Service).all()
    data_page = {"request": request,
                 "user_id": user_id,
                 "first_name": first_name,
                 "title": "Запись на маникюр - Бот",
                 "services": services}
    return templates.TemplateResponse("form.html", data_page)


@router.get("/appointments", response_class=HTMLResponse)
async def get_user_appointments(request: Request, user_id: int = None):
    data_page = {"request": request, "access": False, 'title_h1': "Мои записи"}
    with get_db() as db:
        user_check = db.query(User).filter(User.id == user_id).first()
        services = db.query(Service).all()
        data_page['services'] = services

        if user_id is None or user_check is None:
            data_page['message'] = 'Пользователь не указан или не найден в базе данных'
            return templates.TemplateResponse("appointments.html", data_page)
        else:
            appointments = db.query(Appointment).filter(Appointment.user_id == user_id).all()
            data_page['access'] = True
            if len(appointments):
                data_page['appointments'] = appointments
                return templates.TemplateResponse("appointments.html", data_page)
            else:
                data_page['message'] = 'У вас нет записей!'
                return templates.TemplateResponse("appointments.html", data_page)


@router.get("/admin/appointments", response_class=HTMLResponse)
async def get_admin_panel(request: Request, admin_id: int = None):
    data_page = {"request": request, "access": False, 'title_h1': "Панель администратора"}
    if admin_id is None or admin_id != settings.ADMIN_USER_ID:
        data_page['message'] = 'У вас нет прав для получения информации о записях!'
        return templates.TemplateResponse("appointments.html", data_page)
    else:
        data_page['access'] = True
        with get_db() as db:
            appointments = db.query(Appointment).options(joinedload(Appointment.services)).all()
            services = db.query(Service).all()
        data_page['appointments'] = appointments
        data_page['services'] = services
        return templates.TemplateResponse("appointments.html", data_page)
    

# Отображение страницы администратора
@router.get("/admin/set-time-slots", response_class=HTMLResponse)
async def get_admin_interface(request: Request, admin_id: int = None):
    data_page = {"request": request, "access": False,"title": "Управление доступными временами"}
    if admin_id is None or admin_id != settings.ADMIN_USER_ID:
        data_page['message'] = 'У вас нет прав!'
        return templates.TemplateResponse("time_slots.html", data_page)
    else:
        data_page['access'] = True
        return templates.TemplateResponse("time_slots.html", data_page)


@router.get("/services", response_class=HTMLResponse)
async def get_services(request: Request, user_id: int = None):
    data_page = {"request": request, "access": True, "title": "Прайс-лист"}
    with get_db() as db:
        services = db.query(Service).all()
    data_page['services'] = services
    return templates.TemplateResponse("services.html", data_page)



@router.get("/admin/services", response_class=HTMLResponse)
async def get_admin_services(request: Request, admin_id: int = None):
    data_page = {"request": request, "access": False, "title": "Администрирование прайс-листа"}
    with get_db() as db:
        services = db.query(Service).all()
    data_page['services'] = services
    if admin_id is None or admin_id != settings.ADMIN_USER_ID:
        data_page['message'] = 'У вас нет прав!'
        return templates.TemplateResponse("services.html", data_page)
    else:
        data_page['access'] = True
        return templates.TemplateResponse("services.html", data_page)
