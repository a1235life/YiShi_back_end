import base64
import os

import cv2

import matplotlib.pyplot as plt
import numpy as np
import efficientnet.tfkeras  # 这个库必须导入,否则无法识别FixedDropout这个layer

import tensorflow as tf
from tensorflow.keras.models import load_model
from config.app_config import app

index_to_lable = {0: '玉米', 1: '茄子', 2: '胡萝卜', 3: '蘑菇', 4: '西兰花', 5: '鱼', 6: '苹果', 7: '草莓', 8: '洋葱', 9: '西红柿'}


def load_preprocess_image(path):
    image = tf.io.read_file(path)
    image = tf.image.decode_jpeg(image, channels=3)
    image = tf.image.resize(image, [260, 260])
    image = tf.cast(image, tf.float32)
    image = image / 125.0 - 1
    return image


def check(my_image, my_model, index_to_lable):
    my_image = tf.expand_dims(my_image, 0)
    pred = my_model.predict(my_image)
    return index_to_lable[np.argmax(pred)], pred[0][np.argmax(pred)]


def picture_recognition():
    picture_path = os.path.abspath('..') + '/PairrService/pic.jpg'
    picture_path = picture_path.replace('\\', '/')
    print(picture_path)
    my_image = load_preprocess_image(picture_path)  # 从path中得到图片
    plt.imshow(my_image)

    model_path = os.path.abspath('..') + '/PairrService/model_self'  # 获取父目录路径
    model_super_path = model_path + '/9superb2.h5'  # 模型路径
    model_super_path = model_super_path.replace('\\', '/')
    print(model_super_path)
    model_super = load_model(model_super_path)  # 加载模型
    name, rate = check(my_image, model_super, index_to_lable)  # 得到物种和概率
    print(name, rate)


def ingredient_model_10(str_base64):
    """
    :desc
        模型：10food_demo.h5
    :param str_base64: str类型base64编码（utf8）
    :return:
        name：识别结果
        rate: 识别概率
    """
    img = base64.b64decode(str_base64)  # 保存图片
    # fh = open("pic.jpg", "wb")
    # fh.write(img)
    # fh.close()

    image = tf.image.decode_jpeg(img, channels=3)
    image = tf.image.resize(image, [260, 260])
    image = tf.cast(image, tf.float32)
    image = image / 125.0 - 1
    # plt.imshow(image)
    model_path = os.path.abspath('..') + '/flask_demo/model/'
    model_super_path = model_path + '10food_demo.h5'
    model_super_path = model_super_path.replace('\\', '/')
    app.logger.info('模型路径：%s', model_super_path)
    model_super = load_model(model_super_path)  # 模型
    name, rate = check(image, model_super, index_to_lable)
    app.logger.info('识别结果：%s', name)
    app.logger.info('概率：%s', str(rate))
    return name
    # img = base64.b64decode(data)


labels = ['贝宝果（红青色苹果）', '苹果', '日本金星苹果', '国光苹果', '日本王林苹果', '澳洲青苹果',

          '法国姬娜苹果', '新疆阿克苏苹果', '苹果', '红富士苹果', '蛇果',

          '苹果',

          '苹果', '杏子', '牛油果', '鳄梨', '香蕉', '香蕉', '香蕉',

          '甜菜根', '蓝莓', '仙人掌果', '哈密瓜', '哈密瓜', '杨桃', '花椰菜',

          '樱桃',

          '樱桃', '雷尼尔樱桃', '樱桃', '樱桃', '樱桃', '板栗',

          '橘子',

          '椰子', '玉米', '玉米（带壳）', '黄瓜', '黄瓜', '黑枣干', '茄子', '无花果',

          '生姜',

          '鸡蛋果', '葡萄', '提子', '青提', '白葡萄', '白葡萄',

          '青提',

          '葡萄柚', '柚子', '番石榴', '榛子', '越橘', '柿子', '猕猴桃', '大头菜',

          '金橘',

          '柠檬', '梅耶柠檬', '青柠', '荔枝', '柑桔', '青芒', '芒果', '山竹', '西番莲',

          '甜瓜', '桑葚', '油桃', '油桃（扁平种）', '板栗', '山核桃', '洋葱',

          '洋葱（去皮）', '洋葱', '橘子', '木瓜', '百香果', '毛桃', '黄桃', '毛桃（扁平种）',

          '鸭梨',

          '梨', '阿巴特梨', '福瑞尔梨', '凯撒梨', '怪兽梨', '红梨', '石梨',

          '梨',

          '香瓜茄', '青灯笼椒', '橙灯笼椒', '红灯笼椒', '黄灯笼椒', '灯笼果',

          '灯笼果（带壳）',

          '菠萝', '小菠萝', '火龙果', '李子', '李子', '李子', '石榴',

          '西柚',

          '红薯', '红薯', '地瓜', '土豆', '榅桲', '红毛丹', '覆盆子',

          '红醋栗',

          '蛇皮果', '草莓', '草莓', '树番茄', '橘柚', '番茄', '圣女果', '番茄',

          '番茄',

          '番茄', '番茄', '番茄', '番茄（未成熟）', '黄番茄', '核桃',

          '西瓜']


def fruit_model_131(str_base64):
    """
    :desc
        模型：lk_fruit_131.h5
    :param
        str_base64:    str类型base64编码（utf8）
    :return:
        返回识别结果
    """
    model_path = os.path.abspath('..') + '/flask_demo/model/'
    model = model_path + 'lk_fruit_131.h5'
    model = model.replace('\\', '/')  # 获取模型路径
    model = tf.keras.models.load_model(model)  # 加载模型
    image = base64.b64decode(str_base64)  # base64解码,解码后类型为bytes
    np_array = np.frombuffer(image, dtype=np.uint8)
    image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
    image = cv2.resize(image, (100, 100))
    data = np.ndarray(shape=(1, 100, 100, 3), dtype=np.int)
    image_array = np.asarray(image)
    data[0] = image_array
    y_pred = model.predict(data, 1)
    # print("识别概率：" + str(y_pred))
    app.logger.info('识别概率：%s', str(y_pred[0][np.argmax(y_pred)]))
    app.logger.info('识别索引：%s', str(y_pred.argmax(axis=-1)))
    app.logger.info('识别结果：%s', labels[y_pred.argmax(axis=-1)[0]])
    return labels[y_pred.argmax(axis=-1)[0]]


def fruit_model_25(str_base64):
    """
    :desc
        模型：lk_fruit_25.h5
    :param str_base64: str类型base64编码（utf8）
    :return:
        name：识别结果
        rate: 识别概率
    """
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
    img = base64.b64decode(str_base64)  # 保存图片
    # fh = open("pic.jpg", "wb")
    # fh.write(img)
    # fh.close()

    image = tf.image.decode_jpeg(img, channels=3)
    image = tf.image.resize(image, [260, 260])
    image = tf.cast(image, tf.float32)
    image = image / 125.0 - 1
    # plt.imshow(image)
    model_path = os.path.abspath('..') + '/flask_demo/model/'
    model_super_path = model_path + 'lk_fruit_25.h5'
    model_super_path = model_super_path.replace('\\', '/')
    app.logger.info('模型路径：%s', model_super_path)
    model_super = load_model(model_super_path)  # 模型
    name, rate = check(image, model_super, index_to_label)
    app.logger.info('识别结果：%s', name)
    app.logger.info('概率：%s', str(rate))
    return name


def ingredient_model_20(str_base64):
    """
    :desc
        模型：lk_ingredient_20.h5
    :param str_base64: str类型base64编码（utf8）
    :return:
        name：识别结果
        rate: 识别概率
    """
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
    img = base64.b64decode(str_base64)  # 保存图片
    # fh = open("pic.jpg", "wb")
    # fh.write(img)
    # fh.close()

    image = tf.image.decode_jpeg(img, channels=3)
    image = tf.image.resize(image, [260, 260])
    image = tf.cast(image, tf.float32)
    image = image / 125.0 - 1
    # plt.imshow(image)
    model_path = os.path.abspath('..') + '/flask_demo/model/'
    model_super_path = model_path + 'lk_ingredient_20.h5'
    model_super_path = model_super_path.replace('\\', '/')
    app.logger.info('模型路径：%s', model_super_path)
    model_super = load_model(model_super_path)  # 模型
    name, rate = check(image, model_super, index_to_label)
    app.logger.info('识别结果：%s', name)
    app.logger.info('概率：%s', str(rate))
    return name
