from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import json
import os
from datetime import datetime, timedelta
from functools import wraps

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Конфигурация
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'password123'
MAX_TABLES = 10  # Максимальное количество столиков

# Файл для хранения броней
BOOKINGS_FILE = 'bookings.json'

def load_bookings():
    """Загружает брони из файла"""
    if os.path.exists(BOOKINGS_FILE):
        with open(BOOKINGS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_bookings(bookings):
    """Сохраняет брони в файл"""
    with open(BOOKINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(bookings, f, ensure_ascii=False, indent=2)

def login_required(f):
    """Декоратор для проверки авторизации"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in session:
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

def check_table_availability(date, time, guests, exclude_booking_id=None):
    """Проверяет доступность столиков на указанное время"""
    bookings = load_bookings()
    
    # Подсчитываем уже забронированные места на это время
    booked_tables = 0
    for booking in bookings:
        if booking['id'] == exclude_booking_id:
            continue
        if booking['date'] == date and booking['time'] == time:
            booked_tables += int(booking['guests'])
    
    # Проверяем, хватит ли места
    return (booked_tables + int(guests)) <= MAX_TABLES

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')
        date = request.form.get('date')
        time = request.form.get('time')
        guests = request.form.get('guests')
        
        # Проверяем доступность столиков
        if not check_table_availability(date, time, guests):
            flash('Извините, на это время нет свободных столиков. Выберите другое время.', 'error')
            return redirect(url_for('index'))
        
        # Сохраняем бронь
        bookings = load_bookings()
        new_booking = {
            'id': len(bookings) + 1,
            'name': name,
            'phone': phone,
            'date': date,
            'time': time,
            'guests': guests,
            'created_at': datetime.now().isoformat()
        }
        bookings.append(new_booking)
        save_bookings(bookings)
        
        flash(f'Спасибо, {name}! Ваша бронь на {date} в {time} для {guests} гостей принята.', 'success')
        return redirect(url_for('index'))
    
    return render_template('index.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Неверный логин или пароль', 'error')
    
    return render_template('admin_login.html')

@app.route('/admin')
@login_required
def admin_dashboard():
    bookings = load_bookings()
    
    # Группируем брони по датам для календаря
    calendar_data = {}
    for booking in bookings:
        date = booking['date']
        if date not in calendar_data:
            calendar_data[date] = []
        calendar_data[date].append(booking)
    
    return render_template('admin_dashboard.html', calendar_data=calendar_data, bookings=bookings)

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))

@app.route('/admin/delete/<int:booking_id>', methods=['POST'])
@login_required
def delete_booking(booking_id):
    bookings = load_bookings()
    bookings = [b for b in bookings if b['id'] != booking_id]
    save_bookings(bookings)
    flash('Бронь удалена', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/api/check_availability')
def api_check_availability():
    """API для проверки доступности столиков"""
    date = request.args.get('date')
    time = request.args.get('time')
    guests = request.args.get('guests', 1)
    
    if not date or not time:
        return jsonify({'available': False, 'message': 'Не указаны дата или время'})
    
    available = check_table_availability(date, time, guests)
    return jsonify({
        'available': available,
        'message': 'Свободно' if available else 'Нет свободных столиков'
    })

if __name__ == '__main__':
    app.run(debug=True) 