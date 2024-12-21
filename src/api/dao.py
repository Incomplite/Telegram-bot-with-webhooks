import json
import logging
from datetime import date

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload

from src.dao.base import BaseDAO
from src.database import User, Service, Appointment, Photo, AvailableTimeSlot
from src.database.db import async_session_maker
from src.database.models import AppointmentStatus

logger = logging.getLogger(__name__)


class UserDAO(BaseDAO):
    model = User


class ServiceDAO(BaseDAO):
    model = Service


class AppointmentDAO(BaseDAO):
    model = Appointment

    @classmethod
    async def get_appointments(cls, user_id: int = None):
        async with async_session_maker() as session:
            filters = []
            if user_id is not None:
                filters.append(cls.model.user_id == user_id)

            active_appointments = await session.execute(
                select(cls.model).filter(
                    *filters,
                    cls.model.status.in_([AppointmentStatus.ACTIVE.value, AppointmentStatus.CONFIRMED.value])
                ).options(joinedload(cls.model.services))
            )
            archived_appointments = await session.execute(
                select(cls.model).filter(
                    *filters,
                    cls.model.status == AppointmentStatus.ARCHIVED.value
                ).options(joinedload(cls.model.services))
            )
            return active_appointments.unique().scalars().all(), archived_appointments.unique().scalars().all()

    @classmethod
    async def add_service(cls, appointment_id: int, service: Service):
        """Добавляет услугу к записи"""
        async with async_session_maker() as session:
            try:
                # Загружаем запись вместе с услугами
                stmt = select(cls.model).options(
                    joinedload(cls.model.services)
                ).where(cls.model.id == appointment_id)
                result = await session.execute(stmt)
                appointment = result.unique().scalar_one_or_none()
                
                if appointment:
                    # Получаем service из текущей сессии
                    service = await session.merge(service)
                    if service not in appointment.services:
                        appointment.services.append(service)
                        await session.commit()
                        return True
                    return True
                return False
            except SQLAlchemyError:
                await session.rollback()
                return False

    @classmethod
    async def delete_with_services(cls, appointment_id: int):
        """Удаляет запись вместе со всеми связанными услугами"""
        async with async_session_maker() as session:
            try:
                # Загружаем запись вместе с услугами
                stmt = select(cls.model).options(
                    joinedload(cls.model.services)
                ).where(cls.model.id == appointment_id)
                result = await session.execute(stmt)
                appointment = result.unique().scalar_one_or_none()

                if appointment:
                    # Очищаем связи с услугами
                    appointment.services = []
                    # Удаляем саму запись
                    await session.delete(appointment)
                    await session.commit()
                    return True
                return False
            except SQLAlchemyError:
                await session.rollback()
                return False


class PhotoDAO(BaseDAO):
    model = Photo


class AvailableTimeSlotDAO(BaseDAO):
    model = AvailableTimeSlot

    @classmethod
    async def add_or_update(cls, date: date, slots: list[str]):
        existing_slot = await cls.find_one_or_none(date=date)
        time_slots = json.dumps(slots)

        if existing_slot:
            # Обновляем существующую запись
            await cls.update(existing_slot.id, time_slots=time_slots)
        else:
            # Добавляем новую запись
            await cls.add(date=date, time_slots=time_slots)
