import os
import sqlite3
from datetime import datetime

from flask import Flask, render_template, flash
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import Form
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, equal_to
import wtforms.validators as validators

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'
# 初始化操作，之后就可以在程序中使用基模板
bootstrap = Bootstrap(app)
# 初始化操作，之后就可以在浏览器中渲染日期和时间
moment = Moment(app)
app.config['DATABASE'] = 'test_data.db'
conn = sqlite3.connect(app.config['DATABASE'], check_same_thread=False)


class SignupForm(Form):
    # 四个框：用户名，密码，确认密码，邮箱
    username = StringField('Input your username between 6-15 characters',
                           validators=[Length(min=6, max=15, message='Length between 6-15')])
    password = PasswordField('Input your password between 6-15 characters',
                             validators=[Length(min=6, max=15, message='Length between 6-15')])
    confirm = PasswordField('Confirm your password',
                            validators=[equal_to('password', 'Password must match.')])
    email = StringField('Input your e-mail',
                        validators=[DataRequired()])
    # 一个注册按钮
    submit = SubmitField('signup')


class Task2LoginForm(Form):
    # wtforms form module for task 2
    username = StringField(
        label="Input your email address",
        validators=[
            validators.data_required(message="Please input your email address."),
            validators.email(message="Please input a legal email address.")
        ]
    )
    password = PasswordField(
        label="Input your password",
        validators=[
            validators.data_required(message="Please input your password."),
            validators.length(min=8, max=15, message="The password's length must be between 8 and 15 character.")
        ]
    )
    captcha_code = StringField(
        label="Input captcha",
        validators=[
            validators.data_required(message="Please input the captcha."),
            validators.length(min=4, max=4, message="The length must be 4 numbers.")
        ]
    )

    submit = SubmitField('Login')


@app.route('/task2login', methods=['GET', 'POST'])
def task2login():
    form = Task2LoginForm()
    if form.validate_on_submit():
        print(form.username.data, form.password.data, form.captcha_code.data)
        if form.username.data == "123@qq.com" and form.password.data == "123456":
            flash("It's OK")

    return render_template('login-task2.html', form=form)


class SigninForm(Form):
    # 两个框：用户名，密码
    username = StringField('Input your username',
                           validators=[DataRequired(message='Say something I am giving up on you')])
    password = PasswordField('Input your password',
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
    form = SigninForm()
    if form.validate_on_submit():
        cur = conn.cursor()
        if cur.execute("select * from users where username = '%s' and password = '%s'"
                       % (form.username.data, form.password.data)).fetchone() is not None:
            flash("Login successfully")
            # return render_template(url_for('index'))
        else:
            flash("Authentication failed")
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
