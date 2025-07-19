// Плавная прокрутка по якорям
const navLinks = document.querySelectorAll('nav a[href^="#"]');
navLinks.forEach(link => {
    link.addEventListener('click', function(e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({ behavior: 'smooth' });
        }
    });
});

// Валидация формы бронирования
const form = document.getElementById('bookingForm');
if (form) {
    form.addEventListener('submit', function(e) {
        const name = form.elements['name'].value.trim();
        const phone = form.elements['phone'].value.trim();
        const date = form.elements['date'].value;
        const time = form.elements['time'].value;
        const guests = form.elements['guests'].value;
        if (!name || !phone || !date || !time || !guests) {
            alert('Пожалуйста, заполните все поля!');
            e.preventDefault();
        }
    });
    
    // Проверка доступности столиков при изменении даты/времени
    const dateInput = form.elements['date'];
    const timeInput = form.elements['time'];
    const guestsInput = form.elements['guests'];
    
    function checkAvailability() {
        if (dateInput.value && timeInput.value && guestsInput.value) {
            fetch(`/api/check_availability?date=${dateInput.value}&time=${timeInput.value}&guests=${guestsInput.value}`)
                .then(response => response.json())
                .then(data => {
                    const submitBtn = form.querySelector('button[type="submit"]');
                    if (data.available) {
                        submitBtn.disabled = false;
                        submitBtn.textContent = 'Забронировать';
                        submitBtn.style.background = '#d35400';
                    } else {
                        submitBtn.disabled = true;
                        submitBtn.textContent = 'Нет свободных столиков';
                        submitBtn.style.background = '#95a5a6';
                    }
                });
        }
    }
    
    dateInput.addEventListener('change', checkAvailability);
    timeInput.addEventListener('change', checkAvailability);
    guestsInput.addEventListener('change', checkAvailability);
} 