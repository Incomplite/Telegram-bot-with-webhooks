document.addEventListener('DOMContentLoaded', () => {

    if (Telegram.WebApp) {
      Telegram.WebApp.expand();
    }

    const modal = document.getElementById('editModal');
    const editButtons = document.querySelectorAll('.edit-button');
    const closeButton = document.querySelector('.modal-close');
    const editForm = document.getElementById('editForm');
    const addButton = document.getElementById('addServiceButton');
    let currentCard = null;
    let isEditing = false;
    let cardToDelete = null;

    function createNewServiceCard(name, price, duration, description) {
      const card = document.createElement('div');
      card.className = 'service-card';
      card.setAttribute('data-id', Date.now());
      
      card.innerHTML = `
        <div class="service-name">${name}</div>
        <div class="service-price">${price} ₽</div>
        <div class="service-duration">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/>
            <path d="M12 6v6l4 2"/>
          </svg>
          ${duration}
        </div>
        <div class="service-description">${description}</div>
        <div class="button-group">
          <button class="edit-button">Редактировать</button>
          <button class="delete-button">Удалить</button>
        </div>
      `;

      // Add edit button listener to new card
      card.querySelector('.edit-button').addEventListener('click', handleEditClick);
      card.querySelector('.delete-button').addEventListener('click', handleDeleteClick);
      
      return card;
    }

    function handleEditClick(e) {
      const card = e.target.closest('.service-card');
      currentCard = card;
      isEditing = true;
      
      document.getElementById('modalTitle').textContent = 'Редактировать услугу';
      document.getElementById('serviceName').value = card.querySelector('.service-name').textContent;
      // Обработка цены
      const priceElement = card.querySelector('.service-price');
      const priceText = priceElement.textContent.trim();
      const isPriceFrom = priceText.startsWith('От');
      const priceValue = priceText.replace(/От\s*/, '').replace(/\s*₽/, '').trim(); // Удаляем "От" и знак ₽

      document.getElementById('servicePrice').value = parseInt(priceValue);
      document.getElementById('serviceDuration').value = card.querySelector('.service-duration').textContent.trim();
      document.getElementById('serviceDescription').value = card.querySelector('.service-description').textContent;
      
      modal.style.display = 'flex';
    }

    function resetForm() {
      editForm.reset();
      currentCard = null;
      isEditing = false;
    }

    editButtons.forEach(button => {
        button.addEventListener('click', handleEditClick);
    });

    function handleDeleteClick(e) {
        cardToDelete = e.target.closest('.service-card');
        deleteConfirmModal.style.display = 'flex';
    }

    document.querySelectorAll('.delete-button').forEach(button => {
        button.addEventListener('click', handleDeleteClick);
    });

    document.querySelector('.confirm-yes').addEventListener('click', () => {
        if (cardToDelete) {
            const serviceId = cardToDelete.getAttribute('data-id');
            fetch(`/api/services/${serviceId}`, {
                method: 'DELETE'
            })
            .then(response => {
                if (response.ok) {
                    cardToDelete.remove();
                    cardToDelete = null;
                } else {
                    console.error('Error deleting service:', response.statusText);
                }
            });
        }
        deleteConfirmModal.style.display = 'none';
    });

    document.querySelector('.confirm-no').addEventListener('click', () => {
        cardToDelete = null;
        deleteConfirmModal.style.display = 'none';
    });

    addButton.addEventListener('click', () => {
      resetForm();
      document.getElementById('modalTitle').textContent = 'Добавление услуги';
      modal.style.display = 'flex';
    });

    closeButton.addEventListener('click', () => {
      modal.style.display = 'none';
      resetForm();
    });

    window.addEventListener('click', (e) => {
      if (e.target === modal) {
        modal.style.display = 'none';
        resetForm();
      }
      if(e.target === deleteConfirmModal) {
        deleteConfirmModal.style.display = 'none';
        cardToDelete = null;
      }
    });

    editForm.addEventListener('submit', (e) => {
      e.preventDefault();
      
      const name = document.getElementById('serviceName').value;
      const price = document.getElementById('servicePrice').value;
      const duration = document.getElementById('serviceDuration').value;
      const description = document.getElementById('serviceDescription').value;

      const serviceData = {
        name,
        price,
        duration,
        description,
      };

      if (isEditing && currentCard) {
        // Update existing card
        const serviceId = currentCard.getAttribute('data-id');
        fetch(`/api/services/${serviceId}`, {
            method: 'PUT',
            headers: {
                 'Content-Type': 'application/json',
            },
            body: JSON.stringify(serviceData),
        })
        .then(response => response.json())
        .then(data => {
            currentCard.querySelector('.service-name').textContent = data.name;
            currentCard.querySelector('.service-price').textContent = data.price + ' ₽';
            const durationElement = currentCard.querySelector('.service-duration');
            const svgIcon = durationElement.querySelector('svg');
            durationElement.innerHTML = '';
            durationElement.appendChild(svgIcon);
            durationElement.appendChild(document.createTextNode(data.duration));
            currentCard.querySelector('.service-description').textContent = data.description;
        });
      } else {
        // Create new card
        fetch('/api/services', {
            method: 'POST',
            headers: {
                 'Content-Type': 'application/json',
            },
            body: JSON.stringify(serviceData),
        })
        .then(response => response.json())
        .then(data => {
            const newCard = createNewServiceCard(data.name, data.price, data.duration, data.description);
            document.querySelector('.services-grid').appendChild(newCard);
        });
      }
      modal.style.display = 'none';
      resetForm();
    });
});