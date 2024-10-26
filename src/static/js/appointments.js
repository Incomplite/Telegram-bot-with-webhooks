document.addEventListener('DOMContentLoaded', function() {
    function applyFilters() {
      const searchTerm = document.getElementById('searchInput').value.toLowerCase();
      const dateFilter = document.getElementById('dateFilter').value;
      const serviceFilters = Array.from(document.querySelectorAll('input[name="service"]:checked')).map(input => input.value);

      document.querySelectorAll('.appointment-card').forEach(card => {
        const name = card.querySelector('h2').textContent.toLowerCase();
        const services = card.querySelector('.services').textContent.toLowerCase();
        const date = card.querySelector('p:nth-child(2)').textContent.split(': ')[1];

        const matchesSearch = name.includes(searchTerm) || services.includes(searchTerm);
        const matchesDate = dateFilter === '' || date.includes(dateFilter);
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
      }

      document.getElementById('cancelDelete').onclick = function() {
        modal.style.display = 'none';
      }

      window.onclick = function(event) {
        if (event.target == modal) {
          modal.style.display = 'none';
        }
      }
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

    document.getElementById('searchInput').addEventListener('input', applyFilters);
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
});