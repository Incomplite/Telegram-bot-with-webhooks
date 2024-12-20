document.addEventListener('DOMContentLoaded', function() {

  if (Telegram.WebApp) {
      Telegram.WebApp.expand();
  }

  function applyFilters() {
      const searchInput = document.getElementById('searchInput');
      const searchTerm = searchInput ? searchInput.value.toLowerCase() : '';
      const dateFilter = document.getElementById('dateFilter').value;
      const serviceFilters = Array.from(document.querySelectorAll('input[name="service"]:checked')).map(input => input.value);
      const currentTab = document.querySelector('.tab.active').dataset.tab;
      const currentContainer = currentTab === 'active' ? 
          document.getElementById('activeAppointments') : 
          document.getElementById('archivedAppointments');

      currentContainer.querySelectorAll('.appointment-card').forEach(card => {
          const name = card.querySelector('h2').textContent.toLowerCase();
          const services = card.querySelector('.services').textContent.toLowerCase();
          const cardDateText = card.querySelector('p:nth-child(2)').textContent.split(': ')[1];
          const [day, month, year] = cardDateText.split('.'); // Разбиваем дату по формату dd.mm.yyyy
          const cardDate = `${year}-${month}-${day}`; // Переводим в формат yyyy-mm-dd

          const matchesSearch = !searchTerm || name.includes(searchTerm) || services.includes(searchTerm);
          const matchesDate = !dateFilter || cardDate === dateFilter;
          const matchesService = serviceFilters.length === 0 || 
                                  serviceFilters.some(filter => services.includes(filter.toLowerCase()));

          card.style.display = matchesSearch && matchesDate && matchesService ? 'block' : 'none';
      });
  }

  function showDeleteConfirmation(id) {
      const modal = document.getElementById('deleteModal');
      modal.style.display = 'block';

      document.getElementById('confirmDelete').onclick = function() {
          deleteAppointment(id);
          modal.style.display = 'none';
      };

      document.getElementById('cancelDelete').onclick = function() {
          modal.style.display = 'none';
      };

      window.onclick = function(event) {
          if (event.target === modal) {
              modal.style.display = 'none';
          }
      };
  }

  function deleteAppointment(id) {
      fetch(`/api/appointment/${id}`, {
          method: 'DELETE',
      })
      .then(response => {
          if (response.ok) {
              const card = document.querySelector(`.appointment-card[data-id="${id}"]`);
              if (card) {
                  card.remove();
              }
          } else {
              console.error('Error deleting appointment:', response.statusText);
          }
      })
      .catch(error => {
          console.error('Error deleting appointment:', error);
      });
  }

  const toggleFiltersBtn = document.getElementById('toggleFilters');
  const filtersContainer = document.getElementById('filtersContainer');

  toggleFiltersBtn.addEventListener('click', function() {
      filtersContainer.classList.toggle('show');
      toggleFiltersBtn.textContent = filtersContainer.classList.contains('show') ? 'Скрыть фильтры' : 'Фильтры';
  });

  const searchInput = document.getElementById('searchInput');
  if (searchInput) {
      searchInput.addEventListener('input', applyFilters);
  }
  document.getElementById('dateFilter').addEventListener('change', applyFilters);
  document.querySelectorAll('input[name="service"]').forEach(checkbox => {
      checkbox.addEventListener('change', applyFilters);
  });

  document.querySelectorAll('.delete-button').forEach(button => {
      button.addEventListener('click', function() {
          const id = this.getAttribute('data-id');
          showDeleteConfirmation(id);
      });
  });

  const tabs = document.querySelectorAll('.tab');
  tabs.forEach(tab => {
      tab.addEventListener('click', () => {
          // Update active tab
          tabs.forEach(t => t.classList.remove('active'));
          tab.classList.add('active');

          // Show/hide appointment containers based on the selected tab
          const status = tab.dataset.tab;
          document.getElementById('activeAppointments').style.display = 
              status === 'active' ? 'grid' : 'none';
          document.getElementById('archivedAppointments').style.display = 
              status === 'archive' ? 'grid' : 'none';

          // Reapply current filters
          applyFilters();
      });
  });
});
