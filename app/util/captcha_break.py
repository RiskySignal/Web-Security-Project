# coding=utf-8
import numpy as np
import tensorflow as tf
import tensorflow._api.v1.keras.backend as K
from captcha.image import ImageCaptcha
from tensorflow._api.v1.keras.callbacks import EarlyStopping, CSVLogger, ModelCheckpoint
from tensorflow._api.v1.keras.layers import *
from tensorflow._api.v1.keras.models import *
from tensorflow._api.v1.keras.optimizers import *
from tensorflow._api.v1.keras.utils import Sequence
from util.captcha_code import random_captcha_string, get_captcha_str_map, get_str_map_len
from PIL import Image
from tqdm import tqdm

import pandas as pd

# the width and width default is 160 and 60
HEIGHT = 60
WIDTH = 160
INCLUDE_CHAR = False
N_CAPT = 4
BATCH_SIZE = 8
TRAINING_STEPS = 1000
VALIDA_STEPS = 100
EPOCHS = 100
N_CHAR = get_str_map_len(include_char=INCLUDE_CHAR)


class CaptchaSequence(Sequence):
    def __init__(self, batch_size, steps, width=160, height=60, n_capt=4, include_char=False):
        """
        :param batch_size: batch size
        :param steps: step nums
        :param width: the width of captcha image
        :param height: the height of captcha image
        :param n_capt: captcha length, Default is 4
        :param include_char: whether including english character. Default is False
        """
        self.batch_size = batch_size
        self.steps = steps
        self.width = width
        self.height = height
        self.n_capt = n_capt
        self.include_char = include_char
        self.generator = ImageCaptcha(width=self.width, height=self.height)
        self.characters = get_captcha_str_map(include_char=include_char)
        self.n_char = len(self.characters)  # character type num

    def __len__(self):
        return self.steps

    def __getitem__(self, index):
        X = np.zeros(
            (self.batch_size, self.height, self.width, 3),
            dtype=np.float32
        )
        Y = [
            np.zeros(
                (self.batch_size, self.n_char),
                dtype=np.uint8
            ) for _i in range(self.n_capt)
        ]

        for _i in range(self.batch_size):
            captcha_string = random_captcha_string(length=self.n_capt, include_char=self.include_char)
            X[_i] = np.array(self.generator.generate_image(captcha_string)) / 255.0
            for _j, ch in enumerate(captcha_string):
                Y[_j][_i, self.characters.find(ch)] = 1

        return X, Y


def decode(y, include_char=INCLUDE_CHAR):
    """
    transform the probability metics to string
    :param y: the output probability metics
    :param include_char: whether including english characters
    :return: the decoded string
    """
    y = np.argmax(np.array(y), axis=2)[:, 0]
    characters = get_captcha_str_map(include_char=include_char)

    return "".join([characters[x] for x in y])


def create_model(height=HEIGHT, width=WIDTH, n_char=N_CHAR, n_capt=N_CAPT):
    """
    create model
    :param height: the image height
    :param width: the image width
    :param n_capt: the captcha length
    :param n_char: the char map length
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
        Dense(n_char, activation="softmax", name="c%d" % (_i + 1))(x) for _i in range(n_capt)
    ]
    model = Model(inputs=input_tensor, outputs=x)

    return model


def set_config():
    config = tf.ConfigProto()
    config.gpu_options.allow_growth = True
    sess = tf.Session(config=config)
    K.set_session(sess)


def train_model(epochs=EPOCHS, batch_size=BATCH_SIZE, training_steps=TRAINING_STEPS, valida_steps=VALIDA_STEPS, height=HEIGHT, width=WIDTH, include_char=INCLUDE_CHAR, train_model_path="../model/cnn_best.h5", model_path="../model/cnn.h5", csvlogger_path="../model/cnn.csv", n_char=N_CHAR, n_capt=N_CAPT):
    """
    train a cnn model
    :param epochs:
    :param batch_size:
    :param training_steps:
    :param valida_steps:
    :param height:
    :param width:
    :param include_char:
    :param train_model_path:
    :param model_path:
    :param csvlogger_path:
    :param n_char:
    :param n_capt:
    :return:
    """
    set_config()

    # 配置生成器
    train_data = CaptchaSequence(batch_size=batch_size, steps=training_steps, width=width, height=height, include_char=include_char)
    valid_data = CaptchaSequence(batch_size=batch_size, steps=valida_steps, width=width, height=height, include_char=include_char)
    callbacks = [EarlyStopping(patience=3), CSVLogger(csvlogger_path), ModelCheckpoint(train_model_path, save_best_only=True)]

    # 初步训练
    model = create_model(height=height, width=width, n_char=n_char, n_capt=n_capt)
    model.compile(
        loss="categorical_crossentropy",
        optimizer=Adam(1e-3, amsgrad=True),
        metrics=['accuracy']
    )
    model.fit_generator(train_data, epochs=epochs, validation_data=valid_data, workers=4, use_multiprocessing=True, callbacks=callbacks)

    # 微调
    model.load_weights(train_model_path)
    model.compile(
        loss="categorical_crossentropy",
        optimizer=Adam(1e-4, amsgrad=True),
        metrics=['accuracy']
    )
    model.fit_generator(train_data, epochs=epochs, validation_data=valid_data, workers=4, use_multiprocessing=True, callbacks=callbacks)

    # 保存模型
    model.load_weights(train_model_path)
    model.save(model_path, include_optimizer=False)


def predict_captcha(input_tensor, height=HEIGHT, width=WIDTH, n_capt=N_CAPT, n_char=N_CHAR, include_char=INCLUDE_CHAR, model_path="../model/cnn.h5"):
    """
    predict the captcha in the image input
    :param input_tensor: image input with axis(width, height, 3)
    :type input_tensor: np.ndarray
    :param height: image heigth
    :param width: image width
    :param n_capt: captchar strign length
    :param model_path: model path
    :param include_char: whether including english characters, Default is False
    :return: the predicted string
    """
    assert type(input_tensor) == np.ndarray
    if len(input_tensor.shape) == 3:
        assert (height, width, 3) == input_tensor.shape
        input_tensor = np.expand_dims(input_tensor, axis=0)
    else:
        assert input_tensor.shape[1] == height
        assert input_tensor.shape[2] == width
        assert input_tensor.shape[3] == 3

    model = create_model(height=height, width=width, n_char=n_char, n_capt=n_capt)
    model.load_weights(model_path)
    output = model.predict(input_tensor)
    o_str = decode(output, include_char=include_char)

    return o_str


def convert_image(image_path, width=WIDTH, height=HEIGHT):
    """
    convert image to fixed size numpy array
    :param image_path: the path of the image which need to identify
    :param width: the width axis
    :param height: the height axis
    :return: numpy array
    """
    image = Image.open(image_path, 'r')
    image = image.resize((width, height))

    return np.array(image) / 255.0


def evaluate(height=HEIGHT, width=WIDTH, n_capt=N_CAPT, n_char=N_CHAR, model_path="../model/cnn.h5", batch_num=100, batch_size=64):
    """

    :param height:
    :param width:
    :param n_capt:
    :param n_char:
    :param model_path:
    :param batch_num:
    :param batch_size:
    :return:
    """
    set_config()

    model = create_model(height=height, width=width, n_capt=n_capt, n_char=n_char)
    model.load_weights(model_path)
    batch_acc = 0
    with tqdm(CaptchaSequence(batch_size=batch_size, steps=batch_num)) as pbar:
        for X, y in pbar:
            y_pred = predict_captcha(X)
            y_pred = np.argmax(y_pred, axis=-1).T
            y_true = np.argmax(y, axis=-1).T

            batch_acc += (y_true == y_pred).all(axis=-1).mean()

    return batch_acc / batch_num


def predict_image(image_path, height=HEIGHT, width=WIDTH, n_capt=N_CAPT, n_char=N_CHAR, include_char=INCLUDE_CHAR, model_path="../model/cnn.h5"):
    """
    predict image
    :param image_path:
    :param height:
    :param width:
    :param n_capt:
    :param n_char:
    :param model_path:
    :return: the predicted result string
    """
    set_config()
    input = convert_image(image_path, width=width, height=height)
    return predict_captcha(input, height=height, width=width, n_capt=n_capt, n_char=n_char, include_char=include_char, model_path=model_path)


if __name__ == '__main__':
    train_model()
