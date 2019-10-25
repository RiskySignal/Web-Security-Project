# coding=utf-8
from util.captcha_break import predict_image
import glob
import os

if __name__ == '__main__':
    image_root = "../image source/"
    index = 0
    for _file in glob.glob(os.path.join(image_root, "*.png")):
        index += 1
        if index > 100:
            break
        c = predict_image(_file, model_path="../model/cnn.h5")
        print(_file, c)
