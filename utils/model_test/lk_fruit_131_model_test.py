"""
模型:github模型
数据集:github131种水果数据集
路径:flask_demo/model/lk_fruit_131.h5
"""

import os
import cv2
import numpy as np
import tensorflow as tf

"""
labels = ['Apple Braeburn', 'Apple Crimson Snow', 'Apple Golden 1', 'Apple Golden 2', 'Apple Golden 3',
          'Apple Granny Smith',
          'Apple Pink Lady', 'Apple Red 1', 'Apple Red 2', 'Apple Red 3', 'Apple Red Delicious',
          'Apple Red Yellow 1',
          'Apple Red Yellow 2', 'Apricot', 'Avocado', 'Avocado ripe', 'Banana', 'Banana Lady Finger', 'Banana Red',
          'Beetroot', 'Blueberry', 'Cactus fruit', 'Cantaloupe 1', 'Cantaloupe 2', 'Carambula', 'Cauliflower',
          'Cherry 1',
          'Cherry 2', 'Cherry Rainier', 'Cherry Wax Black', 'Cherry Wax Red', 'Cherry Wax Yellow', 'Chestnut',
          'Clementine',
          'Cocos', 'Corn', 'Corn Husk', 'Cucumber Ripe', 'Cucumber Ripe 2', 'Dates', 'Eggplant', 'Fig',
          'Ginger Root',
          'Granadilla', 'Grape Blue', 'Grape Pink', 'Grape White', 'Grape White 2', 'Grape White 3',
          'Grape White 4',
          'Grapefruit Pink', 'Grapefruit White', 'Guava', 'Hazelnut', 'Huckleberry', 'Kaki', 'Kiwi', 'Kohlrabi',
          'Kumquats',
          'Lemon', 'Lemon Meyer', 'Limes', 'Lychee', 'Mandarine', 'Mango', 'Mango Red', 'Mangostan', 'Maracuja',
          'Melon Piel de Sapo', 'Mulberry', 'Nectarine', 'Nectarine Flat', 'Nut Forest', 'Nut Pecan', 'Onion Red',
          'Onion Red Peeled', 'Onion White', 'Orange', 'Papaya', 'Passion Fruit', 'Peach', 'Peach 2', 'Peach Flat',
          'Pear',
          'Pear 2', 'Pear Abate', 'Pear Forelle', 'Pear Kaiser', 'Pear Monster', 'Pear Red', 'Pear Stone',
          'Pear Williams',
          'Pepino', 'Pepper Green', 'Pepper Orange', 'Pepper Red', 'Pepper Yellow', 'Physalis',
          'Physalis with Husk',
          'Pineapple', 'Pineapple Mini', 'Pitahaya Red', 'Plum', 'Plum 2', 'Plum 3', 'Pomegranate',
          'Pomelo Sweetie',
          'Potato Red', 'Potato Red Washed', 'Potato Sweet', 'Potato White', 'Quince', 'Rambutan', 'Raspberry',
          'Redcurrant',
          'Salak', 'Strawberry', 'Strawberry Wedge', 'Tamarillo', 'Tangelo', 'Tomato 1', 'Tomato 2', 'Tomato 3',
          'Tomato 4',
          'Tomato Cherry Red', 'Tomato Heart', 'Tomato Maroon', 'Tomato not Ripened', 'Tomato Yellow', 'Walnut',
          'Watermelon']
"""

base_dir = "D:/AI Projects/food-identification/ys_model/dataset/github_image_source/Fruit-Images-Dataset/"
labels = os.listdir(base_dir + "Training")
model = tf.keras.models.load_model(base_dir + "src/image_classification/output_files/fruit-360 model/model.h5")
image = cv2.imread(base_dir + "Test/Potato Sweet/r2_62_100.jpg")
image = cv2.resize(image, (100, 100))
data = np.ndarray(shape=(1, 100, 100, 3), dtype=np.int)
image_array = np.asarray(image)
data[0] = image_array
y_pred = model.predict(data, 1)
# print("识别概率：" + str(y_pred))
print("识别概率：" + str(y_pred[0][np.argmax(y_pred)]))
print("识别索引：" + str(y_pred.argmax(axis=-1)))
print("识别结果：" + labels[y_pred.argmax(axis=-1)[0]])
