document.getElementById('loginForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    
    // Здесь будет запрос к API для авторизации
    console.log('Попытка входа:', { username, password });
    
    // Временный редирект для демонстрации
    // В реальном проекте это будет после успешной авторизации
    setTimeout(() => {
        window.location.href = 'index.html';
    }, 1000);
});