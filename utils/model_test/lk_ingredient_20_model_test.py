"""
模型:efficient_netB0
数据集:手动收集二十种食材图片
路径:flask_demo/model/lk_ingredient_20.h5
"""
import tensorflow as tf
import numpy as np
from tensorflow.keras.models import load_model
import efficientnet.tfkeras  # 这个库必须导入,否则无法识别FixedDropout这个layer

index_to_label = {0: '冬虫夏草',
                  1: '菠萝',
                  2: '胡萝卜',
                  3: '草莓',
                  4: '香菇',
                  5: '鲍鱼',
                  6: '海参',
                  7: '洋葱',
                  8: '榴莲',
                  9: '西红柿',
                  10: '金针菇',
                  11: '牛油果',
                  12: '苹果',
                  13: '银耳',
                  14: '香蕉',
                  15: '人参',
                  16: '西兰花',
                  17: '腰果',
                  18: '茄子',
                  19: '杨桃'}


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


my_image = load_preprocess_image('D:/AI Projects/food-identification/ys_model/dataset/images/菠萝/ia_300006471.jpeg')

model_super = load_model('D:/AI Projects/food-material/flask_demo/model/lk_ingredient_20.h5')

a, b = check(my_image, model_super)
print(a, b)
