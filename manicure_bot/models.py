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

    appointments = relationship('Appointment', back_populates='service')


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey(User.id, name='fk_appointments_user_id'), index=True)
    service_id = Column(Integer, ForeignKey(Service.id, name='fk_appointments_service_id'), index=True)
    date = Column(Date)
    time = Column(Time)

    user = relationship('User', back_populates='appointments')
    service = relationship('Service', back_populates='appointments')
