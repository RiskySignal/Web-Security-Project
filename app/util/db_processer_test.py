# coding=utf-8
import os
from util.db_processor import create_db, trans_data_fromTxt

if __name__ == '__main__':
    test_db_file = "../database/test.db"
    if os.path.exists(test_db_file):
        os.remove(test_db_file)

    create_db(db_file=test_db_file)

    """
    Note that: We use the unhashed plain text data since we would add salt when hash the password
    """
    unhashed_txt = 'D:\\workspace\\Web-Security-Project\\dataset\\unhashed.json'
    trans_data_fromTxt(txt_file=unhashed_txt, db_file=test_db_file, is_plaintxt=True)
