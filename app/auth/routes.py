from flask import render_template, flash, redirect, url_for, request
from app.auth.forms import LoginForm, RegistrationForm
from app.auth import bp

from flask_login import current_user, login_user, logout_user, login_required
from app.models import User
from werkzeug.urls import url_parse
from app import db
import pandas as pd

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
       return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Неверный логин или пароль!')
            return redirect(url_for('auth.login'))
        login_user(user)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
           next_page = url_for('main.index')
        return redirect(next_page)
    return render_template('auth/login.html', title='Авторизация', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@login_required
@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.role!='admin':
        return redirect(url_for('main.index'))
    users=User.query.filter(User.role!="admin")
    usr = []
    for i in users:
        usr += [i.as_dict()]
    usr=pd.DataFrame(usr)

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data,fullname=form.fullname.data,role="user")
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Регистрация прошла успешно!')
        return redirect(url_for('auth.register'))
    return render_template('auth/register.html', title='Register', form=form,users=usr)