"""
模型:efficient_netB0
数据集:github25种水果数据集
路径:flask_demo/model/lk_fruit_25.h5
"""
import os
import tensorflow as tf
import numpy as np
from tensorflow.keras.models import load_model
import efficientnet.tfkeras  # 这个库必须导入,否则无法识别FixedDropout这个layer

index_to_label = {0: '茄子',
                  1: '椰子',
                  2: '李子',
                  3: '杨桃',
                  4: '玉米',
                  5: '苹果',
                  6: '木瓜',
                  7: '生姜',
                  8: '菠萝',
                  9: '火龙果',
                  10: '牛油果',
                  11: '蓝莓',
                  12: '榛子',
                  13: '核桃',
                  14: '草莓',
                  15: '西红柿',
                  16: '桑葚',
                  17: '猕猴桃',
                  18: '无花果',
                  19: '樱桃',
                  20: '柠檬',
                  21: '荔枝',
                  22: '香蕉',
                  23: '洋葱',
                  24: '西瓜'}


def load_preprocess_image(path):
    image = tf.io.read_file(path)
    image = tf.image.decode_jpeg(image, channels=3)
    image = tf.image.resize(image, [260, 260])
    # image = tf.image.random_brightness(image,0.7)
    image = tf.cast(image, tf.float32)
    image = image / 125.0 - 1
    return image


def check(image, my_model):
    image = tf.expand_dims(image, 0)
    pred = my_model.predict(image)
    return index_to_label[np.argmax(pred)], pred[0][np.argmax(pred)]


my_image = load_preprocess_image('D:/AI Projects/food-identification/ys_model/dataset/images/avocado/ia_100000004303'
                                 '.jpg')
model_path = os.path.abspath('../..') + '/model/lk_fruit_25.h5'
model_path = model_path.replace('\\', '/')
model = load_model(model_path)

a, b = check(my_image, model)

print(a, b)
