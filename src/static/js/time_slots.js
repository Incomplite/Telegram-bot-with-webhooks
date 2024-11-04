// Функция для получения доступных слотов времени с сервера
async function getAvailableSlots(date) {
  try {
      const response = await fetch(`/api/all-slots/${date}`);
      if (!response.ok) {
          throw new Error('Network response was not ok');
      }
      const data = await response.json();
      return data.slots;
  } catch (error) {
      console.error('Error fetching available slots:', error);
      return [];
  }
}

// Функция для генерации временных слотов
async function generateTimeSlots() {
  const timeSlotsContainer = document.getElementById('timeSlots');
  const selectedDate = document.getElementById('scheduleDate').value;
  
  timeSlotsContainer.innerHTML = '';
  timeSlotsContainer.style.opacity = '0';
  
  // Получаем существующие слоты для выбранной даты
  const existingSlots = await getAvailableSlots(selectedDate);
  
  for (let hour = 9; hour <= 20; hour++) {
      for (let minute of ['00', '30']) {
          if (hour === 20 && minute === '30') continue;
          const timeSlot = document.createElement('div');
          const timeString = `${hour.toString().padStart(2, '0')}:${minute}`;
          
          timeSlot.className = 'time-slot';
          timeSlot.textContent = timeString;
          
          if (existingSlots.includes(timeString)) {
              timeSlot.classList.add('selected');
          }
          
          timeSlot.onclick = function() {
              this.classList.toggle('selected');
          };
          
          timeSlotsContainer.appendChild(timeSlot);
      }
  }

  requestAnimationFrame(() => {
      timeSlotsContainer.style.transition = 'opacity 0.3s ease-in';
      timeSlotsContainer.style.opacity = '1';
  });
}

// Функция сохранения расписания
async function saveSchedule() {
  const selectedDate = document.getElementById('scheduleDate').value;
  if (!selectedDate) {
      alert('Пожалуйста, выберите дату');
      return;
  }

  const selectedSlots = Array.from(document.querySelectorAll('.time-slot.selected'))
      .map(slot => slot.textContent);

  try {
      const response = await fetch('/api/schedule', {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json',
          },
          body: JSON.stringify({
              date: selectedDate,
              slots: selectedSlots
          })
      });

      if (!response.ok) {
          throw new Error('Failed to save schedule');
      }

      // Анимация подтверждения
      const saveButton = document.querySelector('button');
      saveButton.textContent = 'Сохранено!';
      saveButton.style.backgroundColor = '#4CAF50';
      setTimeout(() => {
          saveButton.textContent = 'Сохранить расписание';
          saveButton.style.backgroundColor = '';
      }, 1500);

      // Обновляем отображение сохраненного расписания
      await updateSavedScheduleDisplay();

  } catch (error) {
      console.error('Error saving schedule:', error);
      alert('Произошла ошибка при сохранении расписания');
  }
}

// Функция обновления отображения сохраненного расписания
async function updateSavedScheduleDisplay() {
  const container = document.getElementById('savedScheduleList');
  container.innerHTML = '';

  try {
      const response = await fetch('/api/schedules');
      if (!response.ok) {
          throw new Error('Failed to fetch schedules');
      }

      const schedules = await response.json();

      schedules.forEach(schedule => {
          const scheduleItem = document.createElement('div');
          scheduleItem.className = 'schedule-item';

          const formattedDate = new Date(schedule.date).toLocaleDateString('ru-RU', {
              year: 'numeric',
              month: 'long',
              day: 'numeric'
          });

          scheduleItem.innerHTML = `
              <div class="schedule-date">${formattedDate}</div>
              <div class="schedule-times">
                  ${schedule.slots.map(time => `<span class="schedule-time">${time}</span>`).join('')}
              </div>
          `;

          // Добавление обработчика события для выбора даты
          scheduleItem.addEventListener('click', () => {
            // Устанавливаем дату в поле выбора
            const selectedDate = new Date(schedule.date).toISOString().split('T')[0];
            document.getElementById('scheduleDate').value = selectedDate;
            // Генерируем слоты времени для выбранной даты
            generateTimeSlots();
            // Убираем класс active у всех элементов и добавляем только к выбранному
            document.querySelectorAll('.schedule-item').forEach(item => {
                item.classList.remove('active');
            });
            scheduleItem.classList.add('active');
          });

          container.appendChild(scheduleItem);
      });
  } catch (error) {
      console.error('Error fetching schedules:', error);
      container.innerHTML = '<p>Ошибка при загрузке расписания</p>';
  }
}

// Обработчик изменения даты
document.getElementById('scheduleDate').addEventListener('change', generateTimeSlots);

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', async () => {
  const today = new Date().toISOString().split('T')[0];
  document.getElementById('scheduleDate').value = today;
  document.getElementById('scheduleDate').min = today;
  await generateTimeSlots();
  await updateSavedScheduleDisplay();
});