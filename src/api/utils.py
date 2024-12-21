from src.api.dao import AppointmentDAO
from src.database.models import AppointmentStatus


async def archive_appointment(appointment_id: int):
    appointment = await AppointmentDAO.update(appointment_id, status=AppointmentStatus.ARCHIVED.value)
    if appointment:
        print("Запись перенесена в архив")
    else:
        print("Запись не найдена")
