from flask import Flask, render_template, url_for, flash
from flask_bootstrap import Bootstrap
from flask_wtf import Form
from flask_moment import Moment
from flask_login import UserMixin

from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, equal_to

import os
import re
import sqlite3
import hashlib
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

key = {'select': r'[sS][eE][lL][eE][cC][tT]',
       'from': r'[fF][rR][oO][mM]',
       'where': r'[wW][hH][eE][rR][eE]',
       'and': r'[aA][nN][dD]'
       }
rand_key = {'select': r'[sS][eE][lL][eE][cC][tT][0-9a-zA-Z]+',
            'from': r'[fF][rR][oO][mM][0-9a-zA-Z]+',
            'where': r'[wW][hH][eE][rR][eE][0-9a-zA-Z]+',
            'and': r'[aA][nN][dD][0-9a-zA-Z]+'}


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


class LoginForm(Form):
    # 两个框：用户名，密码
    username = StringField('Input your username',
                           validators=[DataRequired(message='Say something I am giving up on you')])
    password = StringField('Input your password',
                             validators=[DataRequired(message='Say something I am giving up on you')])
    # 一个登录按钮
    submit = SubmitField('login')


def randomize(query):
    secret_key = hashlib.md5('a4567486fjfttfyf132'.encode('utf-8')).hexdigest()
    temp_query = query.split(' ')
    rand_query = temp_query
    for instruction in temp_query:
        if re.findall(key['select'], instruction):
            rand_query[temp_query.index(instruction)] += secret_key
        elif re.findall(key['from'], instruction):
            rand_query[temp_query.index(instruction)] += secret_key
        elif re.findall(key['where'], instruction):
            rand_query[temp_query.index(instruction)] += secret_key
        elif re.findall(key['and'], instruction):
            rand_query[temp_query.index(instruction)] += secret_key
    return ' '.join(rand_query)


def check(query):
    selection = {}
    table_list = {}
    clause = {}
    key_index = {}
    temp_query = query.split(' ')
    # 提取三个基本关键字select from where
    for instruction in temp_query:
        if re.findall(rand_key['select'], instruction):
            key_index['select'] = temp_query.index(instruction)
        elif re.findall(rand_key['from'], instruction):
            key_index['from'] = temp_query.index(instruction)
        elif re.findall(rand_key['where'], instruction):
            key_index['where'] = temp_query.index(instruction)
    # 开始进行语法解析
    # 一、确定selection
    temp_selection = ''
    for ind in range(key_index['from'] - key_index['select'] - 1):
        temp_selection += temp_query[key_index['select'] + ind + 1]
    for ind in range(len(temp_selection.split(','))):
        selection[ind] = temp_selection.split(',')[ind]
    # 二、确定table_list
    temp_table_list = ''
    for ind in range(key_index['where'] - key_index['from'] - 1):
        temp_table_list += temp_query[key_index['from'] + ind + 1]
    for ind in range(len(temp_table_list.split(','))):
        table_list[ind] = temp_table_list.split(',')[ind]
    # 三、确定clause
    temp_clause = ''
    for ind in range(len(temp_query) - key_index['where'] - 1):
        temp_clause = temp_clause +  temp_query[key_index['where'] + ind + 1] + ' '
    temp_clause = temp_clause[:-1]
    and_key = re.findall(rand_key['and'], temp_clause)
    # 此处加一个可以判断是否存在注入：and_key列表内元素是否一致
    for ind in range(len(temp_clause.split(and_key[0]))):
        clause[ind] = temp_clause.split(and_key[0])[ind]
        if temp_clause.split(clause[ind])[1][:len(and_key[0])] == and_key[0]:
            clause['key'+str(ind)] = and_key[0]
    # 四、判断clause是否符合标准
    for ind in clause:
        if type(ind) is int:
            son_clause = clause[ind]
            if len(son_clause.split('=')) == 2:
                pass
            else:
                return 'error'
    # 五、进行去随机化
    return 'checked'


@app.route('/')
def index():
    return render_template('index.html', current_time=datetime.utcnow())


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        print(form.username.data, form.password.data, form.email.data)
        cur = conn.cursor()
        if not cur.execute("select * from users where username = '%s' " % form.username.data).fetchall():
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
    # print('login')
    start = datetime.now()
    form = LoginForm()
    query = "select * from users where username = '%s' and password = '%s'"
    if form.validate_on_submit():
        # print('validated')
        rand_query = randomize(query)
        # print('randomized')
        print(rand_query % (form.username.data, form.password.data))
        final_query = check(rand_query % (form.username.data, form.password.data))
        if final_query == 'error':
            flash("You are injecting")
        elif final_query == 'checked':
            cur = conn.cursor()
            # print(query % (form.username.data, form.password.data))
            if cur.execute(query % (form.username.data, form.password.data)).fetchone() is not None:
                flash("Login successfully")
                # return render_template(url_for('index'))
            else:
                flash("Authentication failed")
    end = datetime.now()
    # print(end - start)
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

