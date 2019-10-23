# coding=utf-8
from captcha.image import ImageCaptcha
import time
import random
import os
import hashlib


def generate_captcha(length, include_char=False):
    """
    generate captcha
    :param length: the captcha length
    :param include_char: whether include the english character
    :return: the captcha image object and the hashed string
    """
    captcha_string = random_captcha_string(length=length, include_char=include_char)

    def save_captcha_imge(output_path):
        """
        captcha image handler
        :param output_path: output path
        """
        image_generator = ImageCaptcha()
        image_generator.write(captcha_string, output_path)

    return save_captcha_imge, captcha_hash(captcha_string)


def captcha_hash(captcha_string):
    """
    generate captcha_hash
    :param captcha_string: string
    :return: hash
    """
    return hashlib.md5(captcha_string.encode('utf-8')).hexdigest()


def get_captcha_str_map(include_char=False):
    """
    get captcha string map
    :param include_char: whether using english characters, Default is False
    :return: total captcha string
    """
    str_map = "012345789"
    if include_char:
        str_map += "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

    return str_map


def random_captcha_string(length, include_char=False):
    """
    randomly select a captcha string
    :return: the captcha string
    """
    MAX_LENGTH = 8
    length = int(length)
    length = min(length, MAX_LENGTH)
    assert length > 0

    str_map = get_captcha_str_map(include_char=include_char)
    captcha_string = ""
    for _i in range(length):
        captcha_string += random.choice(str_map)

    return captcha_string


def random_filename():
    """
    randomly select a filename
    :return: filename
    """
    filename = str(int(time.time()))
    filename += str(random.randint(1, 10000))

    return filename


def gen_captcha_train_data(num, image_root, length, include_char=False):
    """
    generate captcha training dataset
    :param num: number of the image
    :type num: int
    :param image_root: the image folder root
    :param length: the captcha length
    :type length: int
    :param include_char: whether including english character
    """
    if not os.path.isdir(image_root):
        raise NotADirectoryError("The path is not a directory.")

    list_file_name = "list.txt"
    list_file_path = os.path.join(image_root, list_file_name)
    list_file_handler = open(list_file_path, 'w')

    image_generator = ImageCaptcha()
    for _i in range(num):
        captcha_string = random_captcha_string(length=length, include_char=include_char)
        while True:
            image_file_name = random_filename() + ".png"
            image_file_path = os.path.join(image_root, image_file_name)
            if not os.path.exists(image_file_path):
                break

        image_generator.write(captcha_string, image_file_path)
        list_file_handler.write("{file_name}\t{captcha_string}\n".format(file_name=image_file_name, captcha_string=captcha_string))

    list_file_handler.close()
