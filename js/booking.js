// Обработка отмены бронирования
document.querySelectorAll('.cancel-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        const bookingCard = this.closest('.booking-card');
        const roomName = bookingCard.querySelector('h3').textContent;
        
        document.getElementById('cancelRoomName').textContent = roomName;
        document.getElementById('cancelModal').style.display = 'block';
    });
});

// Закрытие модального окна
document.querySelector('#cancelModal .close').addEventListener('click', function() {
    document.getElementById('cancelModal').style.display = 'none';
});

document.querySelector('.cancel-modal-btn').addEventListener('click', function() {
    document.getElementById('cancelModal').style.display = 'none';
});

// Подтверждение отмены
document.querySelector('.confirm-cancel-btn').addEventListener('click', function() {
    // Здесь будет запрос к API для отмены брони
    alert('Бронирование отменено');
    document.getElementById('cancelModal').style.display = 'none';
    
    // В реальном проекте нужно обновить список броней
});

// Закрытие модального окна при клике вне его
window.addEventListener('click', function(e) {
    if (e.target === document.getElementById('cancelModal')) {
        document.getElementById('cancelModal').style.display = 'none';
    }
});