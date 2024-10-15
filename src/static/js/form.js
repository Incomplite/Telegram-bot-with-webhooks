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
    const time = document.getElementById('time').value;

    const formattedDate = new Date(date).toLocaleDateString('ru-RU', { year: 'numeric', month: 'long', day: 'numeric' });

    const confirmationMessage = `${name}, вы записаны на ${formattedDate} в ${time} на следующие услуги: ${serviceText}.`;
    document.getElementById('confirmationMessage').innerHTML = confirmationMessage;
      const modal = document.getElementById('confirmationModal');
      modal.style.display = 'block';
      setTimeout(() => {
        modal.classList.add('show');
      }, 10);
});

document.getElementById('closeModal').addEventListener('click', async function () {
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
        services: selectedServices,  // Store as an array
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
});


// Добавляем текущую дату в поле даты
document.addEventListener('DOMContentLoaded', (event) => {
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('date').setAttribute('min', today);
});
