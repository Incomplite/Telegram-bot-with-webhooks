document.getElementById('appointment-form').addEventListener('submit', function (e) {
    e.preventDefault();

    const name = document.getElementById('name').value;

    const selectedServices = Array.from(document.querySelectorAll('.service-checkbox:checked')).map(checkbox => checkbox.nextElementSibling.textContent);

    if (selectedServices.length === 0) {
        alert("Необходимо выбрать хотя бы одну услугу.");
        return;
    }

    const serviceText = selectedServices.map(service => service.toLowerCase()).join(', ');

    const date = document.getElementById('date').value;
    const timeInput = document.getElementById('time');
    const time = timeInput.value;

    if (timeInput.disabled) {
        alert("Нет доступных времен. Пожалуйста, выберите другую дату.");
        return;
    }

    if (!time) {
        alert("Необходимо выбрать время для записи.");
        return;
    }

    const formattedDate = new Date(date).toLocaleDateString('ru-RU', { year: 'numeric', month: 'long', day: 'numeric' });

    const confirmationMessage = `${name}, вы записаны на ${formattedDate} в ${time} на следующие услуги: ${serviceText}.\nВы подтверждаете запись?`;
    document.getElementById('confirmationMessage').innerHTML = confirmationMessage;
      const modal = document.getElementById('confirmationModal');
      modal.style.display = 'block';
      setTimeout(() => {
        modal.classList.add('show');
      }, 10);
});

document.getElementById('date').addEventListener('change', async function () {
    const date = this.value;

    try {
        const response = await fetch(`/api/available-slots/${date}`);
        const timeInput = document.getElementById('time');

        // Очистим поле времени
        timeInput.innerHTML = '';

        const data = await response.json();

        if (response.status === 404 || data.slots.length === 0) {
            const option = document.createElement('option');
            option.value = '';
            option.text = 'Нет доступных времен';
            timeInput.appendChild(option);
            timeInput.disabled = true;
        } else {
            data.slots.forEach(slot => {
                const option = document.createElement('option');
                option.value = slot;
                option.text = slot;
                timeInput.appendChild(option);
            });
            timeInput.disabled = false;
        }
    } catch (error) {
        console.error('Ошибка получения доступных времен:', error);
    }
});

document.getElementById('confirmForm').addEventListener('click', async function () {
    const name = document.getElementById('name').value.trim();

    // Получаем все выбранные услуги через чекбоксы для хранения
    const selectedServices = Array.from(document.querySelectorAll('.service-checkbox:checked')).map(checkbox => checkbox.nextElementSibling.textContent);

    const date = document.getElementById('date').value;
    const time = document.getElementById('time').value;
    const userId = document.getElementById('user_id').value;

    // Проверяем валидность полей
    if (name.length < 2 || name.length > 50) {
        alert("Имя должно быть от 2 до 50 символов.");
        return;
    }

    if (selectedServices.length === 0) {
        alert("Необходимо выбрать хотя бы одну услугу.");
        return;
    }

    // Создаем объект с данными
    const appointmentData = {
        name: name,
        services: selectedServices,
        appointment_date: date,
        appointment_time: time,
        user_id: userId
    };

    // Преобразуем объект в JSON строку
    const jsonData = JSON.stringify(appointmentData);

    // Отправляем POST запрос на /appointment
    try {
        const response = await fetch('/api/appointment', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: jsonData
        });
        const result = await response.json();
        console.log('Response from /form:', result);

        // Закрываем Telegram WebApp через 100 мс
        setTimeout(() => {
            window.Telegram.WebApp.close();
        }, 100);
    } catch (error) {
        console.error('Error sending POST request:', error);
    }
    
    const modal = document.getElementById('confirmationModal');
    modal.classList.remove('show');
    setTimeout(() => {
      modal.style.display = 'none';
    }, 100);
});

document.getElementById('editForm').addEventListener('click', function() {
    const modal = document.getElementById('confirmationModal');
    modal.classList.remove('show');
    setTimeout(() => {
      modal.style.display = 'none';
    }, 300);
});


// Добавляем текущую дату в поле даты
document.addEventListener('DOMContentLoaded', (event) => {
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('date').setAttribute('min', today);
});
