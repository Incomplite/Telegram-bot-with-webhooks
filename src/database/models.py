import json
from enum import Enum

from sqlalchemy import Boolean, Column, Date, ForeignKey, Integer, String, Time
from sqlalchemy.orm import relationship

from src.database.base import Base


class AppointmentStatus(Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    CONFIRMED = "confirmed"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=True)
    username = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)

    appointments = relationship('Appointment', back_populates='user')


class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    duration = Column(String, nullable=False)
    price = Column(Integer, nullable=False)
    image_url = Column(String, nullable=True)
    is_price_from = Column(Boolean, default=False)

    appointments = relationship('Appointment', secondary='appointment_service_association', back_populates='services')


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey(User.id, name='fk_appointments_user_id'), index=True)
    name = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    time = Column(Time, nullable=False)
    total_price = Column(Integer, nullable=False)
    status = Column(String, default=AppointmentStatus.ACTIVE.value, nullable=False)

    user = relationship('User', back_populates='appointments')
    services = relationship('Service', secondary='appointment_service_association', back_populates='appointments')


class Photo(Base):
    __tablename__ = 'photos'

    id = Column(Integer, primary_key=True, index=True)
    photo_url = Column(String, nullable=False)


class AvailableTimeSlot(Base):
    __tablename__ = 'available_time_slots'

    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    time_slots = Column(String, nullable=False)  # JSON-строка для хранения списка

    def get_time_slots(self):
        # Декодируем JSON-строку в список
        return json.loads(self.time_slots)

    def set_time_slots(self, slots):
        # Кодируем список в JSON-строку
        self.time_slots = json.dumps(slots)


# Ассоциативная таблица для связи многие-ко-многим между Appointment и Service
class AppointmentServiceAssociation(Base):
    __tablename__ = 'appointment_service_association'

    appointment_id = Column(
        Integer,
        ForeignKey(Appointment.id, name='fk_appointment_service_association_appointment_id'),
        primary_key=True
    )
    service_id = Column(
        Integer,
        ForeignKey(Service.id, name='fk_appointment_service_association_service_id'),
        primary_key=True
    )
