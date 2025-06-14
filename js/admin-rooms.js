// Открытие модального окна для добавления комнаты
document.getElementById('addRoomBtn').addEventListener('click', function() {
    document.getElementById('modalRoomTitle').textContent = 'Добавить новую комнату';
    document.getElementById('roomForm').reset();
    document.getElementById('roomModal').style.display = 'block';
});

// Открытие модального окна для редактирования комнаты
document.querySelectorAll('.edit-room-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        const card = this.closest('.room-admin-card');
        const roomName = card.querySelector('h3').textContent;
        
        document.getElementById('modalRoomTitle').textContent = 'Редактировать комнату';
        document.getElementById('roomName').value = roomName;
        
        // Здесь можно добавить заполнение других полей данными комнаты
        document.getElementById('roomModal').style.display = 'block';
    });
});

// Переключение статуса комнаты
document.querySelectorAll('.disable-room-btn, .enable-room-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        const card = this.closest('.room-admin-card');
        const roomName = card.querySelector('h3').textContent;
        const action = this.classList.contains('disable-room-btn') ? 'отключить' : 'активировать';
        
        if (confirm(`Вы уверены, что хотите ${action} комнату ${roomName}?`)) {
            // Здесь будет запрос к API для изменения статуса
            alert(`Комната ${roomName} успешно ${action}на`);
            // В реальном проекте нужно обновить интерфейс
        }
    });
});

// Обработка сохранения комнаты
document.getElementById('roomForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const roomName = document.getElementById('roomName').value;
    // Здесь будет запрос к API для сохранения комнаты
    
    alert(`Комната "${roomName}" успешно сохранена`);
    document.getElementById('roomModal').style.display = 'none';
});

// Закрытие модального окна
document.querySelectorAll('.close, .cancel-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        document.getElementById('roomModal').style.display = 'none';
    });
});

// Закрытие модального окна при клике вне его
window.addEventListener('click', function(e) {
    if (e.target === document.getElementById('roomModal')) {
        document.getElementById('roomModal').style.display = 'none';
    }
});