# coding=utf-8
import sqlite3
import os
import json
import sys
import hashlib


def create_db(db_file="../database/default.db"):
    """
    create database    
    :param db_file: database file name
    """
    if os.path.exists(db_file):
        raise FileExistsError("The database file exists.")

    dir_path = os.path.dirname(db_file)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

    connection = sqlite3.connect(db_file)
    try:
        connection.execute("create table user(id INTEGER PRIMARY KEY, username VARCHAR(255) NOT NULL UNIQUE, password VARCHAR(32) NOT NULL);")
        connection.commit()
        connection.close()
    except Exception as _err:
        connection.close()
        os.remove(db_file)
        raise _err


def trans_data_fromTxt(txt_file, db_file="../database/default.db", is_plaintxt=True, web_hash_func=None):
    """
    transform data in txt to databse
    :param txt_file: txt file path
    :param db_file: database file
    :param is_plaintxt: whether is the plain txt, Default is True
    :param web_hash_func: web hash fucntion uesd when commit password from web to server, Default is None
    """
    if not os.path.exists(txt_file):
        raise FileNotFoundError("Text file not exists.")

    connection = sqlite3.connect(db_file)

    max_username_length = 0
    min_username_length = sys.maxsize
    max_password_length = 0
    min_password_length = sys.maxsize

    with open(txt_file, 'r') as _file:
        for _line in _file.readlines():
            if _line:
                j_line = json.loads(_line)
                username = j_line["username"]

                if is_plaintxt:
                    password = j_line["passwordplaintext"]
                else:
                    # Note that: if you use the hashed password data, you should be careful of transforming the data by youself.
                    password = j_line["passwordhash"]

                if username and password:
                    max_username_length = max(max_username_length, len(username))
                    min_username_length = min(min_username_length, len(username))
                    max_password_length = max(max_password_length, len(password))
                    min_password_length = min(min_password_length, len(password))
                    if web_hash_func:
                        password = web_hash_func(password)
                    password = password_hash_db(password)
                    try:
                        connection.execute("insert into user values(null,?,?)", (username, password))
                    except Exception as _err:
                        print(username, password)
                        raise _err

    connection.commit()
    connection.close()

    if is_plaintxt:
        print("Max username length: ", max_username_length)
        print("Min username length: ", min_username_length)
        print("Max password length: ", max_password_length)
        print("Min password length: ", min_password_length)


def password_hash_db(password_string):
    """
    generate hash for password storation
    :param password_string: the password string
    :type password_string: str
    :return: hash
    """
    password_string += hash_salt_db(password_string)
    return hashlib.md5(password_string.encode('utf-8')).hexdigest()


def hash_salt_db(password_string):
    """
    generate salt for password hash
    :param password_string: the password sting
    :type password_string: str
    :return: salt string
    """
    return hashlib.sha512(password_string.encode('utf-8')).hexdigest()


def verify_user(username, password, db_connection):
    """
    verify the user
    :param username: username
    :param password: password hashed by web transformation
    :param db_connection: datebase connection handler
    :return: boolean
    :raise:
    """
    db_cursor = db_connection.cursor()
    password = password_hash_db(password)
    db_cursor.execute("select * from user where username=? and password=?", (username, password))
    if db_cursor.fetchone() is None:
        db_cursor.close()
        return False
    else:
        db_cursor.close()
        return True
