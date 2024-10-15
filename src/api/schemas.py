from datetime import date, time
from typing import List

from pydantic import BaseModel, Field


# Модель для валидации данных
class AppointmentData(BaseModel):
    name: str = Field(..., min_length=2, max_length=50, description="Имя клиента")
    services: List[str] = Field(..., min_items=1, min_length=2, max_length=50, description="Услуги клиента")
    appointment_date: date = Field(..., description="Дата назначения")
    appointment_time: time = Field(..., description="Время назначения")
    user_id: int = Field(..., description="ID пользователя Telegram")
