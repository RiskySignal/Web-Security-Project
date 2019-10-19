# coding=utf-8
from captcha.image import ImageCaptcha

if __name__ == '__main__':
    new_image = ImageCaptcha()

    new_image.write("1234", "./image source/test.png")
