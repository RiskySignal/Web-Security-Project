import os
import sqlite3
from datetime import timedelta
from io import BytesIO
import wtforms.validators as validators
from flask import Flask, render_template, flash, make_response, session, redirect, request
from flask_bootstrap import Bootstrap
from flask_wtf import Form
from wtforms import StringField, PasswordField, SubmitField
from util.captcha_code import generate_captcha, captcha_hash
from db_processor import verify_user

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=2.0)
CAPTCHA_SESSION_NAME = "captcha"
app.config['DATABASE'] = './database/test.db'
bootstrap = Bootstrap(app)

connection = sqlite3.connect(app.config['DATABASE'], check_same_thread=False)


class LoginForm(Form):
    # Note that: If you use the db_processor to transform the data from txt to db, you may set the length according to that
    username_min_l = 1
    username_max_l = 20
    password_min_l = 1
    password_max_l = 32

    username = StringField(
        label="Input your email address",
        validators=[
            validators.data_required(message="Please input your email address."),
            # validators.email(message="Please input a legal email address."),
            validators.length(min=username_min_l, max=username_max_l, message="The usernmae's length must be between {min_length} and {max_length} characters.".format(min_length=username_min_l, max_length=username_max_l))
        ]
    )
    password = PasswordField(
        label="Input your password",
        validators=[
            validators.data_required(message="Please input your password."),
            validators.length(min=password_min_l, max=password_max_l, message="The password's length must be between {min_length} and {max_length} characters.".format(min_length=password_min_l, max_length=password_max_l))
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


@app.route('/login', methods=['GET', 'POST'])
def task2login():
    form = LoginForm()
    if request.method == "POST" and form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        captcha = form.captcha_code.data

        if CAPTCHA_SESSION_NAME in session:
            if session[CAPTCHA_SESSION_NAME] == captcha_hash(captcha):
                if verify_user(username, password, connection):
                    flash("成功！")
                else:
                    flash("用户名密码错误！")
            else:
                # the captcha is not right
                flash("验证码错误！")
        else:
            # the captcha is out of date
            flash("验证码过期！")

    return render_template('task2/login.html', form=form)


@app.route("/get_captcha", methods=['GET', 'POST'])
def get_captcha():
    save_captcha_imge, hashed_code = generate_captcha(length=4, include_char=False)
    io_handler = BytesIO()
    save_captcha_imge(io_handler)
    captcha_image = io_handler.getvalue()

    response = make_response(captcha_image)
    response.headers["Content-Type"] = "image/png"

    session[CAPTCHA_SESSION_NAME] = hashed_code
    session.permanent = True

    return response


@app.route('/')
def index():
    return redirect('/login')


@app.errorhandler(404)
def page_not_found():
    return render_template('task2/404.html'), 404


@app.errorhandler(500)
def internal_server_error():
    return render_template('task2/500.html'), 500


if __name__ == '__main__':
    app.run()
