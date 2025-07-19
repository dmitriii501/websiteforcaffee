from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Для flash-сообщений

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')
        date = request.form.get('date')
        time = request.form.get('time')
        guests = request.form.get('guests')
        # Здесь можно добавить сохранение брони в БД или отправку на email
        flash(f'Спасибо, {name}! Ваша бронь на {date} в {time} для {guests} гостей принята.', 'success')
        return redirect(url_for('index'))
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)

