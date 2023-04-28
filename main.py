import os
import csv

from flask import Flask, render_template, redirect, session, request
from forms.user import RegisterForm, LoginForm
from forms.vacansion import CreateForm
from data import db_session
from data.users import User
from data.vacan import Vacansion
from flask_login import LoginManager, login_user, logout_user, login_required, current_user


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)


# РЕГИСТРАЦИЯ, ВХОД И ПРОЧЕЕ

@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                                message="Неправильный логин или пароль",
                                form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                    form=form,
                                    message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                    form=form,
                                    message="Такой пользователь уже есть")
        user = User(
            username=form.username.data,
            email=form.email.data,
            name=form.name.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    else:
        print('неверные данные')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


# ОСНОВНАЯ ЧАСТЬ САЙТА

@app.route("/")
def index():
    param = dict()
    param['title'] = 'Домашняя страница'
    return render_template('index.html', **param)


@app.route("/people")
def people():
    param = dict()
    param['title'] = 'Состав'
    param['peoples'] = []
    with open('people.csv', encoding="utf8") as csvfile:
        reader = csv.reader(csvfile, delimiter=';', quotechar='"')
        for row in reader:
            param['peoples'].append([row[0], row[1], row[2], row[3]])

    return render_template('people.html', **param)


@app.route("/about")
def about():
    param = dict()
    param['title'] = 'О нас'
    return render_template('about.html', **param)


@app.route("/jobs", methods=['GET', 'POST'])
def jobs():
    form = CreateForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        vac = Vacansion(
            job=form.job.data,
            year=form.year.data,
            desc=form.desc.data
        )
        ftype = form.photo.data.content_type.split('/')
        if ftype[0] != 'image':
            return render_template('jobs.html', title='Вакансии', form=form, message="Вы должны загрузить изображение.")
        ftype = ftype[1]
        vac.user_id = current_user.id
        db_sess.add(vac)
        db_sess.commit()
        form.photo.data.save(f'photos/{vac.id}.{ftype}')
        vac.photo = f'photos/{vac.id}.{ftype}'
        db_sess.commit()
        return redirect('/')
    else:
        print('неверные данные')
    return render_template('jobs.html', title='Вакансии', form=form)


if __name__ == '__main__':
    db_session.global_init("db/main.db")
    
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)