# coding=utf-8
from captcha.image import ImageCaptcha
import time
import random
import hashlib


def generate_captcha(length, include_char=False):
    """
    generate captcha
    :param length: the captcha length
    :param include_char: whether include the english character
    :return: the captcha image object and the hashed string
    """
    MAX_LENGTH = 8
    length = int(length)
    length = min(length, MAX_LENGTH)
    assert length > 0

    char_map = "012345789"
    if include_char:
        char_map += "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

    captcha_string = ""
    random.seed(int(time.time()))
    for _i in range(length):
        captcha_string += random.choice(char_map)

    def save_captcha_imge(output_path):
        """
        captcha image handler
        :param output_path: output path
        """
        image_object = ImageCaptcha()
        image_object.write(captcha_string, output_path)

    return save_captcha_imge, captcha_hash(captcha_string)


def captcha_hash(captcha_string):
    """
    generate captcha_hash
    :param captcha_string: string
    :return: hash
    """
    return hashlib.md5(captcha_string.encode('utf-8')).hexdigest()
