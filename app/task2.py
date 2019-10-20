import os
from datetime import timedelta
from io import BytesIO

import wtforms.validators as validators
from flask import Flask, render_template, flash, make_response, session, redirect
from flask_bootstrap import Bootstrap
from flask_wtf import Form
from wtforms import StringField, PasswordField, SubmitField

from util.captcha_code import generate_captcha

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=2.0)
# 初始化操作，之后就可以在程序中使用基模板
bootstrap = Bootstrap(app)


# 初始化操作，之后就可以在浏览器中渲染日期和时间
# app.config['DATABASE'] = 'test_data.db'
# conn = sqlite3.connect(app.config['DATABASE'], check_same_thread=False)


class loginForm(Form):
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


@app.route('/login', methods=['GET', 'POST'])
def task2login():
    form = loginForm()
    if form.validate_on_submit():
        print(form.username.data, form.password.data, form.captcha_code.data)
        if form.username.data == "123@qq.com" and form.password.data == "123456":
            flash("It's OK")

    return render_template('task2/login.html', form=form)


@app.route("/get_captcha", methods=['GET', 'POST'])
def get_captcha():
    save_captcha_imge, hashed_code = generate_captcha(length=4, include_char=False)
    io_handler = BytesIO()
    save_captcha_imge(io_handler)
    captcha_image = io_handler.getvalue()

    response = make_response(captcha_image)
    response.headers["Content-Type"] = "image/png"

    session["captcha"] = hashed_code
    session.permanent = True

    return response


@app.route('/')
def index():
    return redirect('/login')


# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     form = SigninForm()
#     if form.validate_on_submit():
#         cur = conn.cursor()
#         if cur.execute("select * from users where username = '%s' and password = '%s'"
#                        % (form.username.data, form.password.data)).fetchone() is not None:
#             flash("Login successfully")
#             # return render_template(url_for('index'))
#         else:
#             flash("Authentication failed")
#     return render_template('sign.html', form=form, current_time=datetime.utcnow())


@app.errorhandler(404)
def page_not_found(e):
    return render_template('task2/404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('task2/500.html'), 500


if __name__ == '__main__':
    app.run()
