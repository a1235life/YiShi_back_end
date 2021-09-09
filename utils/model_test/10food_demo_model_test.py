"""
模型:efficient_netB0
数据集:手动收集十种食材图片
路径:flask_demo/model/10food_demo.h5
"""
import tensorflow as tf
import numpy as np
from tensorflow.keras.models import load_model
import efficientnet.tfkeras  # 这个库必须导入,否则无法识别FixedDropout这个layer

index_to_lable = {0: '玉米', 1: '茄子', 2: '胡萝卜', 3: '蘑菇', 4: '西兰花', 5: '鱼', 6: '苹果', 7: '草莓', 8: '洋葱', 9: '西红柿'}


def load_preprocess_image(path):
    image = tf.io.read_file(path)
    image = tf.image.decode_jpeg(image, channels=3)
    image = tf.image.resize(image, [260, 260])
    # image = tf.image.random_brightness(image,0.7)
    image = tf.cast(image, tf.float32)
    image = image / 125.0 - 1
    return image


def check(my_image, my_model, index_to_lable):
    my_image = tf.expand_dims(my_image, 0)
    pred = my_model.predict(my_image)
    return (index_to_lable[np.argmax(pred)], pred[0][np.argmax(pred)])


my_image = load_preprocess_image('C:/Users/42276/Desktop/1.jpg')

model_super = load_model('/model/10food_demo.h5')

a, b = check(my_image, model_super, index_to_lable)
print(a, b)
