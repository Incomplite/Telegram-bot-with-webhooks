from datetime import datetime

from aiogram_calendar import SimpleCalendar

from manicure_bot.utils import is_sunday
from manicure_bot.database.db import get_db
from manicure_bot.utils import get_available_time_slots


class CustomSimpleCalendar(SimpleCalendar):
    async def process_day_select(self, data, query):
        """Checks selected date is in allowed range of dates"""
        date = datetime(int(data.year), int(data.month), int(data.day))
        if self.min_date and self.min_date > date:
            await query.answer(
                f'Дата должна быть позже {self.min_date.strftime("%d/%m/%Y")}',
                show_alert=self.show_alerts
            )
            return False, None
        elif self.max_date and self.max_date < date:
            await query.answer(
                f'Дата должна быть раньше {self.max_date.strftime("%d/%m/%Y")}',
                show_alert=self.show_alerts
            )
            return False, None
        # Проверка на воскресенье
        elif is_sunday(date):
            await query.answer(
                "Извините, запись на воскресенье недоступна. Пожалуйста, выберите другой день недели.",
                show_alert=True
            )
            return False, None
        # Проверка доступных временных слотов
        with get_db() as db:
            available_times = get_available_time_slots(date, db)
            if not available_times:
                await query.answer(
                    "На выбранную дату все времена заняты. Пожалуйста, выберите другой день.",
                    show_alert=True
                )
                return False, None
        await query.message.delete_reply_markup()  # removing inline keyboard
        return True, date
