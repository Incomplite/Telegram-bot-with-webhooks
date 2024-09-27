from sqlalchemy import Column, Integer, String, Date, Time, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from manicure_bot.database.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, unique=True, index=True)
    name = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)

    appointments = relationship('Appointment', back_populates='user')


class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    price = Column(Integer, nullable=False)
    image_url = Column(String, nullable=True)
    is_price_from = Column(Boolean, default=False)

    appointments = relationship('Appointment', secondary='appointment_service_association', back_populates='services')


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey(User.id, name='fk_appointments_user_id'), index=True)
    date = Column(Date)
    time = Column(Time)

    user = relationship('User', back_populates='appointments')
    services = relationship('Service', secondary='appointment_service_association', back_populates='appointments')


class Photo(Base):
    __tablename__ = 'photos'

    id = Column(Integer, primary_key=True, index=True)
    photo_url = Column(String, nullable=False)


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
