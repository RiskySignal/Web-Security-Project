from flask import Flask, render_template, url_for, flash
from flask_bootstrap import Bootstrap
from flask_wtf import Form
from flask_moment import Moment
from flask_login import UserMixin

from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, equal_to, regexp

import re
import os
import sqlite3
from datetime import datetime

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'
# 初始化操作，之后就可以在程序中使用基模板
bootstrap = Bootstrap(app)
# 初始化操作，之后就可以在浏览器中渲染日期和时间
moment = Moment(app)
app.config['DATABASE'] = 'test_data.db'
conn = sqlite3.connect(app.config['DATABASE'], check_same_thread=False)
# cur = conn.cursor()


class SignupForm(Form):
    # 四个框：用户名，密码，确认密码，邮箱
    username = StringField('Input your username between 6-15 characters',
                           validators=[Length(min=6, max=15, message='Length between 6-15'),
                                       regexp(r'[0-9a-zA-Z]', message='Letters and numbers only')])
    password = PasswordField('Input your password between 6-15 characters',
                             validators=[Length(min=6, max=15, message='Length between 6-15'),
                                         regexp(r'[0-9a-zA-Z]', message='Letters and numbers only')])
    confirm = PasswordField('Confirm your password',
                            validators=[equal_to('password', 'Password must match.')])
    email = StringField('Input your e-mail',
                        validators=[DataRequired()])
    # 一个注册按钮
    submit = SubmitField('signup')


class LoginForm(Form):
    # 两个框：用户名，密码
    username = StringField('Input your username',
                           validators=[DataRequired(message='Say something I am giving up on you')])
    password = StringField('Input your password',
                           validators=[DataRequired(message='Say something I am giving up on you')])
    # 一个登录按钮
    submit = SubmitField('login')


@app.route('/')
def index():
    return render_template('index.html', current_time=datetime.utcnow())


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        print(form.username.data, form.password.data, form.email.data)
        cur = conn.cursor()
        if cur.execute("select * from users where username = '%s' " % form.username.data).fetchall() == []:
            temp_id = cur.execute("select count (*) from users").fetchone()[0] + 1
            cur.execute("insert into users values('%d', '%s', '%s', '%s')"
                        % (temp_id, form.username.data, form.password.data, form.email.data))
            conn.commit()
            flash("It's done. Thank you!")
            # render_template(url_for('index'))
        else:
            flash('This username has been taken. Please try again with another one')
    return render_template('sign.html', form=form, current_time=datetime.utcnow())


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    start = datetime.now()
    if form.validate_on_submit():
        cur = conn.cursor()
        if cur.execute("select * from users where username = '%s' and password = '%s'"
                       % (form.username.data, form.password.data)).fetchone() is not None:
            flash("Login successfully")
            # return render_template(url_for('index'))
        else:
            flash("Authentication failed")
    end = datetime.now()
    print(end - start)
    return render_template('sign.html', form=form, current_time=datetime.utcnow())


@app.route('/dashboard')
def user_dashboard(name):
    return render_template('user.html', name=name)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run()

