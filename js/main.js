// Открытие модального окна
document.querySelectorAll('.book-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        if (this.disabled) return;
        
        const roomCard = this.closest('.room-card');
        const roomName = roomCard.querySelector('h3').textContent;
        
        document.getElementById('roomName').value = roomName;
        document.getElementById('bookingModal').style.display = 'block';
    });
});

// Закрытие модального окна
document.querySelector('.close').addEventListener('click', function() {
    document.getElementById('bookingModal').style.display = 'none';
});

// Обработка формы бронирования
document.getElementById('bookingForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const roomName = document.getElementById('roomName').value;
    const date = document.getElementById('bookingDate').value;
    const time = document.getElementById('bookingTime').value;
    
    console.log('Бронирование:', { roomName, date, time });
    
    // Здесь будет запрос к API
    alert(`Комната ${roomName} успешно забронирована на ${date} в ${time}`);
    document.getElementById('bookingModal').style.display = 'none';
});

// Закрытие модального окна при клике вне его
window.addEventListener('click', function(e) {
    if (e.target === document.getElementById('bookingModal')) {
        document.getElementById('bookingModal').style.display = 'none';
    }
});

// Инициализация даты (сегодняшняя)
document.getElementById('date').valueAsDate = new Date();
document.getElementById('bookingDate').valueAsDate = new Date();