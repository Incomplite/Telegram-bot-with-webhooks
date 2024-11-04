from src.database import Appointment
from src.database.db import get_db
from src.models import AppointmentStatus


async def archive_appointment(appointment_id: int):
    with get_db() as db:
        appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
        if appointment:
            appointment.status = AppointmentStatus.ARCHIVED.value
            db.commit()
            print("Запись перенесена в архив")
        print("Запись не найдена")
