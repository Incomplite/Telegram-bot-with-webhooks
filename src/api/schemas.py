from datetime import date, time
from typing import List

from pydantic import BaseModel, Field


# Модель для валидации данных
class AppointmentData(BaseModel):
    name: str = Field(..., min_length=2, max_length=50, description="Имя клиента")
    services: List[str] = Field(None, min_items=1, max_length=50, description="Услуги клиента")
    appointment_date: date = Field(..., description="Дата назначения")
    appointment_time: time = Field(..., description="Время назначения")
    user_id: int = Field(..., description="ID пользователя Telegram")
    total_price: int = Field(..., description="Общая стоимость услуг")


class Schedule(BaseModel):
    date: date
    slots: List[str]


class ServiceData(BaseModel):
    name: str
    price: int
    duration: int
    description: str


class ServiceResponse(BaseModel):
    id: int
    name: str
    price: int
    description: str
