from flask import Flask, render_template, redirect, flash
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from flask_moment import Moment

from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, equal_to

import os
import random
from datetime import datetime

rand = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9,
        'A', 'B', 'C', 'D', 'E', 'F', 'G',
        'H', 'I', 'J', 'K', 'L', 'M', 'N',
        'O', 'P', 'Q', 'R', 'S', 'T',
        'U', 'V', 'W', 'X', 'Y', 'Z']
rand_value = ''


def create_code(rand_value):
    for i in range(0, 4):
        num = random.randint(0, 36)
        rand_value += str(rand[num])


basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'
# 初始化操作，之后就可以在程序中使用基模板
bootstrap = Bootstrap(app)
# 初始化操作，之后就可以在浏览器中渲染日期和时间
moment = Moment(app)


class SignupForm(FlaskForm):
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


class LoginForm(FlaskForm):
    # 两个框：用户名，密码
    username = StringField('Input your username',
                           validators=[DataRequired(message='Say something I am giving up on you')])
    password = StringField('Input your password',
                             validators=[DataRequired(message='Say something I am giving up on you')])

    verification = StringField('Input the verification code below',
                               validators=[DataRequired(message='Say something I am giving up on you')])

    code = SubmitField(render_kw={'type': 'test', 'value': rand_value, 'Onclick': 'createCode()'})

    # 一个登录按钮
    submit = SubmitField('login', render_kw={'Onclick': 'validate()'})


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    return redirect('/login')


@app.route('/')
def index():
    return redirect('/login')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.username.data == 'TonyLin' and form.password.data == '123456':
            flash("Login successfully")
            # return render_template(url_for('index'))
        else:
            flash("Authentication failed")
    return render_template('sign.html', form=form, current_time=datetime.utcnow())


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


if __name__ == '__main__':
    app.run(host='127.0.0.1')
