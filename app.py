import datetime
import os
import random

import numpy as np
import plotly.graph_objects as go
import mysql.connector
from flask import Flask, render_template, url_for, request, redirect, flash, session, abort, jsonify
# from flask_sqlalchemy import SQLAlchemy
# from flask_login import LoginManager, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from scramble_generator import generate_scramble


### configuration ###

config = {
    'user': 'root',
    'password': 'root',
    'host': 'localhost',
    'unix_socket': '/Applications/MAMP/tmp/mysql/mysql.sock',
    'database': 'scubertimer',
    'raise_on_warnings': True
}

app = Flask(__name__)
start_time = None
running = False

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@localhost/scubertimer'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'fgghaks92s2d5hfh32jkhh9hj38jdhs8hh35h8k2'
app.secret_key = 'kas9-/ai1-l]/,175agtp4[[bydp;'


def ao5_def():
    if len(time_list_def()) >= 5:
        time_ao5 = time_list_def()[-5:].copy()
        time_ao5 = [float(time) for time in time_ao5]
        time_ao5.remove(max(time_ao5))
        time_ao5.remove(min(time_ao5))
        ao5 = round(np.mean(time_ao5), 2)
        if ao5 == float('inf'):
            ao5 = 'DNF'
    else:
        ao5 = '--'
    return ao5


def ao10_def():
    if len(time_list_def()) >= 10:
        time_ao10 = time_list_def()[-10:].copy()
        time_ao10 = [float(time) for time in time_ao10]
        time_ao10.remove(max(time_ao10))
        time_ao10.remove(min(time_ao10))
        ao10 = round(np.mean(time_ao10), 2)
        if ao10 == float('inf'):
            ao10 = 'DNF'
    else:
        ao10 = '--'
    return ao10


def ao100_def():
    if len(time_list_def()) >= 100:
        time_ao100 = time_list_def()[-100:].copy()
        time_ao100 = [float(time) for time in time_ao100]
        time_ao100.remove(max(time_ao100))
        time_ao100.remove(min(time_ao100))
        ao100 = round(np.mean(time_ao100), 2)
        if ao100 == float('inf'):
            ao100 = 'DNF'
    else:
        ao100 = '--'
    return ao100


def mean_def():
    if len(time_list_def()) >= 1:
        time_mean = time_list_def().copy()
        time_mean = [float(time) for time in time_mean]
        time_mean.remove(max(time_mean))
        time_mean.remove(min(time_mean))
        mean = round(np.mean(time_mean), 2)
        if mean == float('inf'):
            mean = 'DNF'
    else:
        mean = '--'
    return mean


def time_list_def():
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor(dictionary=True)

    users_id = session.get('users_id')
    query = "SELECT * FROM user_solves WHERE users_id = %s"
    cursor.execute(query, (users_id,))
    user3 = cursor.fetchall()
    # print('user3', len(user3))

    time_list = []

    # Проходим по каждой строке результата запроса и извлекаем время
    for row in user3:
        time = row['time']  # Здесь 'time' - это название столбца с временем
        if time == 'DNF':
            time = float('inf')
        time_list.append(time)

    # print('3', time_list)
    return time_list



@app.route('/exit')
def exit():
    session.clear()
    return redirect('/')

@app.route('/get_ao_data')
def get_ao_data():
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor(dictionary=True)

    users_id = session.get('users_id')
    query = "SELECT * FROM user_solves WHERE users_id = %s"
    cursor.execute(query, (users_id,))
    user3 = cursor.fetchall()

    time_list = []

    # Проходим по каждой строке результата запроса и извлекаем время
    for row in user3:
        time = row['time']
        time_list.append(time)

    # AO5
    ao5_result = ao5_def()

    # AO10
    ao10_result = ao10_def()

    # AO100
    ao100_result = ao100_def()

    # MEAN
    mean_result = mean_def()

    return jsonify({'ao5': ao5_result, 'ao10': ao10_result, 'ao100': ao100_result, 'mean': mean_result})

@app.context_processor
def inject_user_id():
    user_id = session.get('users_id')
    return dict(users_id=user_id)

@app.route('/')
def helloo():
    show_button = True
    users_id = session.get('users_id')
    # print("users_id:", users_id)
    return render_template('main_page.html', scramble=generate_scramble(), users_id=users_id)


@app.route('/generate_scramble', methods=['GET'])
def generate_scramble_route():
    new_scramble = generate_scramble()
    return new_scramble


@app.route('/stop_timer', methods=['POST'])
def stop_timer():
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor(dictionary=True)

    users_id = session.get('users_id')
    time = request.form.get('time')
    if len(time) == 3:
        time = float('0' + time[:-3] + '.' + time[-3:])
    else:
        time = float(time[:-3] + '.' + time[-3:])
    scramble = (request.form.get('scramble')).strip()
    try:
        query = "INSERT INTO user_solves (users_id, time, scramble, created_at) VALUES (%s, %s, %s, %s)"
        data = (users_id, time, scramble, datetime.datetime.now())
        cursor.execute(query, data)
        cnx.commit()
        cnx.close()  # Вызов функции для вставки данных в базу
        return ""
    except Exception as e:
        print(e)
        return ""


@app.route('/login', methods=['POST', 'GET'])
def login():
    show_button = False
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor(dictionary=True)
    if 'userLogged' in session:
        return redirect(url_for('profile', username=session['userLogged']))
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        query = "SELECT * FROM users WHERE email = %s"
        cursor.execute(query, (email,))
        user = cursor.fetchone()
        cnx.close()

        if user != None and check_password_hash(user['password'], password):
            users_id = int(user['id'])
            session['users_id'] = users_id

            session['userLogged'] = user['id']

            return redirect(url_for('profile', username=user['id']))
        else:
            flash('Неверный логин или пароль')
            return render_template('login.html', show_button= show_button)
    return render_template('login.html', show_button=show_button)


@app.route('/add_friend', methods=['POST'])
def add_friend():
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor(dictionary=True)
    if request.method == 'POST':
        ids_friend = request.form['ids_friend']

        # Проверяем, что ids_friend не равно текущему пользователю
        if ids_friend != str(session.get('users_id')):
            query = "SELECT id FROM users WHERE id = %s"
            cursor.execute(query, (ids_friend,))
            id = cursor.fetchone()
            if id:
                # Проверяем, не существует ли уже такого друга в базе данных
                query_check = "SELECT * FROM friends WHERE users_id = %s AND friend_id = %s"
                cursor.execute(query_check, (session.get('users_id'), id['id']))
                existing_friend = cursor.fetchone()

                if not existing_friend:
                    try:
                        # Добавляем друга в таблицу friends
                        query_insert = "INSERT INTO friends (users_id, friend_id) VALUES (%s, %s)"
                        data = (session.get('users_id'), id['id'])
                        cursor.execute(query_insert, data)

                        # Добавляем обратную связь, чтобы друг был виден в обоих профилях
                        query_insert_reverse = "INSERT INTO friends (users_id, friend_id) VALUES (%s, %s)"
                        data_reverse = (id['id'], session.get('users_id'))
                        cursor.execute(query_insert_reverse, data_reverse)

                        cnx.commit()
                        cnx.close()
                        flash('Вы добавили друга')
                    except Exception as e:
                        print(e)
                        flash('Ошибка добавления друга')
                else:
                    flash('Такой друг уже существует')
            else:
                flash('Нет такого пользователя')
        else:
            flash('Вы не можете добавить сами себя в друзья')

    return redirect(url_for('profile', username=session.get('users_id')))

@app.route('/del_solves', methods=['GET', 'POST'])
def del_solves():
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor(dictionary=True)
    query = "DELETE FROM user_solves WHERE users_id = %s ORDER BY created_at DESC LIMIT 1"
    cursor.execute(query, ((session.get('users_id'),)))
    cnx.commit()
    cnx.close()
    return redirect('/')

@app.route('/dnf', methods=['GET', 'POST'])
def dnf():
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor(dictionary=True)
    query = "UPDATE user_solves SET time = 'DNF' WHERE users_id = %s ORDER BY created_at DESC LIMIT 1"
    cursor.execute(query, ((session.get('users_id'),)))
    cnx.commit()
    cnx.close()
    return redirect('/')

@app.route('/plus2', methods=['GET', 'POST'])
def plus2():
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor(dictionary=True)
    query = "UPDATE user_solves SET time = time + 2, comments = '+2' WHERE users_id = %s ORDER BY created_at DESC LIMIT 1"
    cursor.execute(query, ((session.get('users_id'),)))
    cnx.commit()
    cnx.close()
    return redirect('/')

@app.route('/del_friend', methods=['GET', 'POST'])
def del_friend():
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor(dictionary=True)
    query = "DELETE FROM friends WHERE users_id = %s AND friend_id = %s"
    query1 = "DELETE FROM friends WHERE friend_id = %s AND users_id = %s"
    flash('Вы удалили друга')
    cursor.execute(query, (session.get('users_id'), request.form['friend_id']))
    cursor.execute(query1, (session.get('users_id'), request.form['friend_id']))
    cnx.commit()
    cnx.close()
    return redirect(url_for('profile', username=session.get('users_id')))

@app.route('/profile/<username>', methods = ['GET', 'POST'])
def profile(username):
    show_button = False
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor(dictionary=True)

    default_values = {
        'times': '--',
        'ao5': '--',
        'count': '--',
        'ao10': '--',
        'scrambles': '--',
    }


    # friends
    friends_name_list = []
    friends_id_list = []

    query = "SELECT * FROM users WHERE id = %s"
    cursor.execute(query, (username,))
    user = cursor.fetchone()

    unique_id = user['unique_id']

    query = "SELECT friend_id FROM friends WHERE users_id = %s"
    cursor.execute(query, (username,))
    friend_id = cursor.fetchall()
    if len(friend_id) == 1:
        friend_status = 1
    elif len(friend_id) == 2:
        friend_status = 2
    elif len(friend_id) == 3:
        friend_status = 3
    elif len(friend_id) == 4:
        friend_status = 4
    else:
        friend_status = 0

    for row in friend_id:
        friend_id = row['friend_id']
        query = "SELECT * FROM users WHERE id = %s"
        cursor.execute(query, (friend_id,))
        friends_info = cursor.fetchall()
        if friends_info:
            f = friends_info[0]['username']
            friends_id_list.append(friends_info[0]['id'])
            friends_name_list.append(f)

    query = "SELECT * FROM user_solves WHERE users_id = %s"
    cursor.execute(query, (username,))
    user3 = cursor.fetchall()

    times = []
    scrambles = []
    comments = []

    for row in user3:
        times.append(row['time'])
        scrambles.append(row['scramble'])
        comments.append(row['comments'])

    # AO5
    ao5 = ao5_def()

    # AO10
    ao10 = ao10_def()

    count = len(times)
    if 'userLogged' not in session or int(username) != session['userLogged']:
        abort(404)

    if len(user3) == 0:
        times = ['--', '--', '--', '--', '--', '--']
        ao5 = '--'
        count = '--'
        ao10 = '--'
        scrambles = '--'

    if len(friends_name_list) == 0:
        friends_name_list = None
        friends_id_list = None

    if os.path.isfile('static/images/' + str(session.get('users_id')) + '.png'):
        profile_img = '/static/images/' + str(session.get('users_id')) + '.png'
    else:
        profile_img = '/static/images/default.png'

    friends_img = []

    if friends_id_list != None:
        for id in friends_id_list:
            if os.path.exists('static/images/' + str(id) + '.png'):
                friends_img.append(id)
                # print(id, 'id')
            else:
                friends_img.append('default')


    return render_template('profile.html', profile_img=profile_img, username=user['username'], email=user['email'],
                            times=times, ao5=ao5, count=count, ao10=ao10, friends=friends_name_list, comments=comments,
                           show_button=show_button, scrambles=scrambles, friend_status=friend_status, friends_id=friends_id_list,
                           user_id=session.get('users_id'), friends_img=friends_img, unique_id=unique_id)

@app.route('/change_profile_img', methods=['GET', 'POST'])
def change_profile_img():
    if request.method == 'POST':
        img = (request.files['profile_img'])
        if img:
            img.save('static/images/' + str(session.get('users_id')) + '.png')
            print('success')
    return redirect(url_for('profile', username=session.get('users_id')))

# from flask_wtf import FlaskForm, RecaptchaField
# from flask_wtf.recaptcha import Recaptcha
# from wtforms import (StringField, SubmitField)
# from wtforms.validators import DataRequired

# app.config['RECAPTCHA_PUBLIC_KEY'] = '6Ld4dCgoAAAAAIT7PrFocpFckwNhNWOx1sk2mzr_'
# app.config['RECAPTCHA_PRIVATE_KEY'] = '6Ld4dCgoAAAAAJmE6rLDMiX3wfcEb0jbf0CsI1Cq'
# recaptcha = Recaptcha(app)

# class MyForm(FlaskForm):
#     name = StringField('Name', validators=[DataRequired()])
#     recaptcha = RecaptchaField()
#     submit = SubmitField('Submit')



# @app.route('/m', methods=['GET', 'POST'])
# def my_route():
#     # form = MyForm()
#     if form.validate_on_submit():
#         if recaptcha.verify():
#             # Реализуйте вашу логику обработки формы здесь
#             name = form.name.data
#             return f'Форма отправлена успешно, имя: {name}'
#         else:
#             return 'Ошибка reCAPTCHA. Пожалуйста, пройдите проверку CAPTCHA.'
#     return render_template('captcha.html', form=form)


@app.route('/signup', methods=['GET', 'POST'])
def create_article():
    if 'userLogged' in session:
        return redirect(url_for('profile', username=session['userLogged']))
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor(dictionary=True)
    # form = MyForm()
    if request.method == 'POST':
        # if form.validate_on_submit():
        #     if recaptcha.verify():
        username = request.form['username']
        email = request.form['email']
        if request.form['password'] == request.form['password1']:
            password = generate_password_hash(request.form['password'])
            try:
                unique_id = random.randrange(000000, 999999)
                query = "INSERT INTO users (unique_id, username, email, password, date) VALUES (%s, %s, %s, %s, %s)"
                data = (unique_id, username, email, password, datetime.datetime.now())
                cursor.execute(query, data)
                cnx.commit()


                query = "SELECT * FROM users WHERE email = %s"
                cursor.execute(query, (email,))
                user = cursor.fetchone()
                cnx.close()

                users_id = int(user['id'])
                session['users_id'] = users_id

                session['userLogged'] = user['id']
                return redirect(url_for('profile', username=user['id']))
            except Exception as e:
                print(e)
                flash('Ошибка регистрации')
        else:
            flash('Пароли не совпадают')



        return render_template('signup.html', show_button=False)

    return render_template('signup.html', show_button=False)


@app.route('/graph', methods=['GET', 'POST'])
def graph():
    x = [1, 2, 3, 4, 5, 6, 7, 8]
    y = [29, 31, 39, 33, 37, 39, 48, 43, 38]

    # Создание графика с закругленными линиями и закрашенной областью под графиком
    fig = go.Figure()

    # Добавляем закрашенную область под графиком с прозрачностью
    fig.add_trace(go.Scatter(x=x, y=y, mode='lines', fill='tozeroy', fillcolor='rgba(0, 159, 255, 0.2)',
                             line=dict(color='#009FFF', shape='spline')))

    # Настройка начальной точки оси y
    fig.update_yaxes(range=[min(y), max(y) + 2])  # Устанавливаем диапазон оси y с учетом начальной точки

    fig.update_xaxes(showticklabels=False)

    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    # Сохранение графика как изображение
    img_path = os.path.join('static/images/', 'graph.png')
    fig.write_image(img_path, format='png', width=800, height=600)

    return render_template('profile.html', img_path='static/images/graph.png')


### ERRORS ###

@app.errorhandler(404)
def page_not_found(error):
    return render_template('page404.html'), 404


@app.errorhandler(401)
def unauthorized(error):
    return render_template('page401.html'), 401


if __name__ == '__main__':
    app.run(debug=True, port=5016)
