import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

conn = sqlite3.connect('test.db')


def init():
    c = conn.cursor()
    c.execute("create table user(id, username, password)")
    c.execute("insert into user values('1', 'TonyLin', '123456')")
    conn.commit()
    conn.close()


def insert():
    pass


def verify():
    c = conn.cursor()


c = conn.cursor()
# c.execute("create table users(id int, username varchar(128), password varchar(128))")
# print(c.execute("select * from user where username = 'Tonysin'").fetchone())
# print(type(c.execute("select count (*) from user").fetchone()[0]))
# conn.commit()
# conn.close()

username = 'TonyLin'
username2 = "' or 1 = 1 --"
username3 = 'lllll'
password = '123456'
password2 = '1234567'
password_hash = generate_password_hash(password)
user_id = c.execute("select count (*) from users").fetchone()[0] + 1
'''
print(generate_password_hash(password))
print(type(generate_password_hash(password)))
print(check_password_hash(generate_password_hash(password), password))
print(check_password_hash(generate_password_hash(password), password2))'''


# c.execute("insert into users values('%d', '%s', '%s')" % (user_id, username, password_hash))
# conn.commit()
# print(c.execute("select * from users where username = '%s' and password = '%s'"
#  % (username, generate_password_hash(password))).fetchone())
temp_hash = c.execute("select * from user where username = '%s'" % username3).fetchone()
conn.close()
# print(check_password_hash(temp_hash, password))
# print(check_password_hash(temp_hash, password2))
print(temp_hash)
