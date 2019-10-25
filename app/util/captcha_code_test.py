# coding=utf-8
from util.captcha_code import generate_captcha, gen_captcha_train_data
import time
import random
import os


def generate_captcha_test(length, include_char=False):
    save_captcha_imge, hash_string = generate_captcha(length=length, include_char=include_char)

    if not os.path.exists("../image source/"):
        os.makedirs("../image source/")

    test_outputPath = "../image source/" + str(int(time.time())) + "_" + str(random.randint(1, 100)) + ".png"
    save_captcha_imge(output_path=test_outputPath)

    print(test_outputPath, hash_string)


if __name__ == '__main__':
    generate_captcha_test(length=4, include_char=False)
    # generate_captcha_test(length=4, include_char=True)

    # image_root = "../image source/"
    # gen_captcha_train_data(num=100, image_root=image_root, length=4, include_char=False)
