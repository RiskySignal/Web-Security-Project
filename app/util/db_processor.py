# coding=utf-8
import sqlite3
import os
import json
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


def trans_data_fromTxt(txt_file, db_file="../database/default.db", is_plaintxt=True):
    """
    transform data in txt to databse
    :param txt_file: txt file path
    :param db_file: database file
    :param is_plaintxt: whether is the plain txt, Default is True
    """
    if not os.path.exists(txt_file):
        raise FileNotFoundError("Text file not exists.")

    connection = sqlite3.connect(db_file)

    with open(txt_file, 'r') as _file:
        for _line in _file.readlines():
            if _line:
                j_line = json.loads(_line)
                username = j_line["username"]

                if is_plaintxt:
                    password = password_hash_db(j_line["passwordplaintext"])
                else:
                    password = j_line["passwordhash"]

                if username and password:
                    try:
                        connection.execute("insert into user values(null,?,?)", (username, password))
                    except Exception as _err:
                        print(username, password)
                        raise _err

    connection.commit()
    connection.close()


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
