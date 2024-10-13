document.getElementById('appointmentForm').addEventListener('submit', function (e) {
    e.preventDefault();

    const name = document.getElementById('name').value;

    // Get all selected services and join them into a string
    const serviceSelect = document.getElementById('service');
    const selectedServices = Array.from(serviceSelect.selectedOptions).map(option => option.text);
    const serviceText = selectedServices.map(service => service.toLowerCase()).join(', ');

    const date = document.getElementById('date').value;
    const time = document.getElementById('time').value;

    const popupMessage = `${name}, вы записаны на следующие услуги: ${serviceText} ${date} в ${time}.`;
    document.getElementById('popupMessage').textContent = popupMessage;

    document.getElementById('popup').style.display = 'flex';
});

document.getElementById('closePopup').addEventListener('click', async function () {
    const name = document.getElementById('name').value.trim();

    // Get all selected services and join them into a string for storage
    const serviceSelect = document.getElementById('service');
    const selectedServices = Array.from(serviceSelect.selectedOptions).map(option => option.text);
    const serviceText = selectedServices.join(', ');

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

// Анимация появления элементов при загрузке страницы
function animateElements() {
    const elements = document.querySelectorAll('h1, .form-group, .btn');
    elements.forEach((el, index) => {
        setTimeout(() => {
            el.style.opacity = '1';
            el.style.transform = 'translateY(0)';
        }, 100 * index);
    });
}

// Стили для анимации
var styleSheet = document.styleSheets[0];
styleSheet.insertRule(`
    h1, .form-group, .btn {
        opacity: 0;
        transform: translateY(20px);
        transition: opacity 0.5s ease, transform 0.5s ease;
    }
`, styleSheet.cssRules.length);

// Плавное появление страницы при загрузке
window.addEventListener('load', function () {
    document.body.style.opacity = '1';
    animateElements();
});

styleSheet.insertRule(`
    body {
        opacity: 0;
        transition: opacity 0.5s ease;
`, styleSheet.cssRules.length);

// Добавляем текущую дату в поле даты
document.addEventListener('DOMContentLoaded', (event) => {
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('date').setAttribute('min', today);
});
