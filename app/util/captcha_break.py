# coding=utf-8
import tensorflow as tf
import tensorflow._api.v1.keras.backend as K
from tensorflow._api.v1.keras.utils import Sequence
import numpy as np
from util.captcha_code import random_captcha_string, get_captcha_str_map
from captcha.image import ImageCaptcha
from tensorflow._api.v1.keras.models import *
from tensorflow._api.v1.keras.layers import *
from tensorflow._api.v1.keras.utils import plot_model
from IPython.display import Image
from tensorflow._api.v1.keras.callbacks import EarlyStopping, CSVLogger, ModelCheckpoint
from tensorflow._api.v1.keras.optimizers import *

HEIGHT = 60
WIDTH = 160
INCLUDE_CHAR = False
C_LENGTH = 4


class CaptchaSequence(Sequence):
    def __init__(self, batch_size, steps, width=160, height=60, c_length=4, include_char=False):
        """
        :param batch_size: batch size
        :param steps: step nums
        :param width: the width of captcha image
        :param height: the height of captcha image
        :param c_length: captcha length, Default is 4
        :param include_char: whether including english character. Default is False
        """
        self.batch_size = batch_size
        self.steps = steps
        self.width = width
        self.height = height
        self.c_len = c_length
        self.include_char = include_char
        self.generator = ImageCaptcha(width=self.width, height=self.height)
        self.characters = get_captcha_str_map(include_char=include_char)
        self.n_len = len(self.characters)  # character type num

    def __len__(self):
        return self.steps

    def __getitem__(self, index):
        X = np.zeros(
            (self.batch_size, self.height, self.width, 3),
            dtype=np.float32
        )
        Y = [
            np.zeros(
                (self.batch_size, self.n_len),
                dtype=np.uint8
            ) for _i in range(self.c_len)
        ]

        for _i in range(self.batch_size):
            captcha_string = random_captcha_string(length=self.c_len, include_char=self.include_char)
            X[_i] = np.array(self.generator.generate_image(captcha_string)) / 255.0
            for _j, ch in enumerate(captcha_string):
                Y[_j][_i, self.characters.find(ch)] = 1

        return X, Y


def decode(y, include_char=False):
    """
    transform the probability metics to string
    :param y: the output probability metics
    :param include_char: whether including english characters
    :return: the decoded string
    """
    y = np.argmax(np.array(y), axis=2)[:, 0]
    characters = get_captcha_str_map(include_char=include_char)

    return "".join([characters[x] for x in y])


def create_model(height, width, c_length):
    """
    create model
    :param height: the image height
    :param width: the image width
    :param c_length: the captcha length
    :return: Model
    """
    input_tensor = Input((height, width, 3))
    x = input_tensor
    for _i, n_cnn in enumerate([2, 2, 2, 2, 2]):
        for _i in range(n_cnn):
            x = Conv2D(32 * 2 ** min(_i, 3), kernel_size=3, padding="same", kernel_initializer="he_uniform")(x)
            x = BatchNormalization()(x)
            x = Activation('relu')(x)
        x = MaxPool2D(2)(x)

    x = Flatten()(x)
    x = [
        Dense(c_length, activation="softmax", name="c%d" % (_i + 1))(x) for _i in range(c_length)
    ]
    model = Model(inputs=input_tensor, outputs=x)

    return model


def train_model():
    # 防止tensorflow占用所有显存
    config = tf.ConfigProto()
    config.gpu_options.allow_growth = True
    sess = tf.Session(config=config)
    K.set_session(sess)

    # 配置生成器
    train_data = CaptchaSequence(batch_size=128, steps=1000)
    valid_data = CaptchaSequence(batch_size=128, steps=100)
    callbacks = [EarlyStopping(patience=3), CSVLogger('cnn.csv'), ModelCheckpoint('cnn_best.h5', save_best_only=True)]

    # 初步训练
    model = create_model(height=HEIGHT, width=WIDTH, c_length=4)
    model.compile(
        loss="categorical_crossentropy",
        optimizer=Adam(1e-3, amsgrad=True),
        metrics=['accuracy']
    )
    model.fit_generator(train_data, epochs=100, validation_data=valid_data, workers=4, use_multiprocessing=True, callbacks=callbacks)

    # 微调
    model.compile(
        loss="categorical_crossentropy",
        optimizer=Adam(1e-4, amsgrad=True),
        metrics=['accuracy']
    )
    model.fit_generator(train_data, epochs=100, validation_data=valid_data, workers=4, use_multiprocessing=True, callbacks=callbacks)


def get_visual_model(file_path="../model/cnn.png"):
    """
    visualization model
    :param file_path: output image path
    """
    model = create_model(height=HEIGHT, width=WIDTH, c_length=C_LENGTH)
    plot_model(model, to_file=file_path, show_shapes=True)


if __name__ == '__main__':
    # get_visual_model()
    train_model()
