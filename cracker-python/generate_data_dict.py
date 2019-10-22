from optparse import OptionParser
import os
import random


def get_str_from_list(data_list, minl=6, maxl=10):
    user_length = int((random.random() * (maxl - minl)) + minl)
    user = ''
    for _ in range(user_length):
        index = int(random.random() * len(data_list))
        user += data_list[index]
    return user


if __name__ == '__main__':
    parser = OptionParser('To generate user and password dictionary')
    parser.add_option('-c', '--count', dest='line_count', type="int")
    options, _ = parser.parse_args()
    line_count = options.line_count

    user_char_list = []
    pass_char_str = './,<>?\'";:\\|[]{}=+-_`~!@#$%^&*()'
    pass_char_list = [c for c in pass_char_str]
    for i in range(26):
        user_char_list.append(chr(ord('a') + i))
        user_char_list.append(chr(ord('A') + i))
        pass_char_list.append(chr(ord('a') + i))
        pass_char_list.append(chr(ord('A') + i))

    data_dict_path = 'dict.txt'
    if os.path.exists(data_dict_path):
        os.remove(data_dict_path)

    with open(data_dict_path, 'w') as data_dict:
        for i in range(line_count):
            user_name = get_str_from_list(user_char_list)
            password = get_str_from_list(pass_char_list, minl=8, maxl=16)
            data_dict.write(user_name + ' ' + password)
            data_dict.write('\n')
