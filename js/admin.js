// Открытие модального окна редактирования
document.querySelectorAll('.edit-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        document.getElementById('editModal').style.display = 'block';
    });
});

// Закрытие модальных окон
document.querySelectorAll('.close, .cancel-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        document.querySelectorAll('.modal').forEach(modal => {
            modal.style.display = 'none';
        });
    });
});

// Сохранение изменений
document.querySelector('.admin-form').addEventListener('submit', function(e) {
    e.preventDefault();
    // Здесь будет запрос к API для сохранения изменений
    alert('Изменения сохранены');
    document.getElementById('editModal').style.display = 'none';
});

// Закрытие модального окна при клике вне его
window.addEventListener('click', function(e) {
    if (e.target.classList.contains('modal')) {
        document.querySelectorAll('.modal').forEach(modal => {
            modal.style.display = 'none';
        });
    }
});

// Экспорт в CSV
document.querySelector('.export-btn').addEventListener('click', function() {
    // Здесь будет логика экспорта
    alert('Данные экспортированы в CSV');
});