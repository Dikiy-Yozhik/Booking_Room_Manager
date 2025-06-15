document.getElementById('registerForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    // Получаем значения полей
    const fullName = document.getElementById('fullName').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    const userType = document.getElementById('userType').value;
    
    // Сбрасываем предыдущие ошибки
    document.querySelectorAll('.error-message').forEach(el => el.style.display = 'none');
    document.querySelectorAll('.input-error').forEach(el => el.classList.remove('input-error'));
    
    // Валидация
    let isValid = true;
    
    if (password !== confirmPassword) {
        showError('confirmPassword', 'Пароли не совпадают');
        isValid = false;
    }
    
    if (password.length < 8) {
        showError('password', 'Пароль должен содержать не менее 8 символов');
        isValid = false;
    }
    
    if (!userType) {
        showError('userType', 'Выберите тип учетной записи');
        isValid = false;
    }
    
    if (isValid) {
        // Здесь будет запрос к API для регистрации
        console.log('Регистрация:', { fullName, email, password, userType });
        
        // Временный редирект для демонстрации
        alert('Регистрация прошла успешно!');
        window.location.href = 'index.html';
    }
});

function showError(fieldId, message) {
    const field = document.getElementById(fieldId);
    field.classList.add('input-error');
    
    let errorElement = field.nextElementSibling;
    if (!errorElement || !errorElement.classList.contains('error-message')) {
        errorElement = document.createElement('div');
        errorElement.className = 'error-message';
        field.parentNode.insertBefore(errorElement, field.nextSibling);
    }
    
    errorElement.textContent = message;
    errorElement.style.display = 'block';
}