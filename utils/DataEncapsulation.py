# 将参数food对象封装成一个字典
def FoodEncapsulation(food):
    # pic_dic = {
    #     '苹果': 'http://47.98.201.222:8080/ingredients/img/apple/apple_2.jpg',
    #     '香蕉': 'http://47.98.201.222:8080/ingredients/img/banana/banana_1.jpg',
    #     '西兰花': 'http://47.98.201.222:8080/ingredients/img/broccoli/broccoli_2.jpg',
    #     '胡萝卜': 'http://47.98.201.222:8080/ingredients/img/carrot/carrot_2.jpg',
    #     '玉米': 'http://47.98.201.222:8080/ingredients/img/corn/corn_2.jpg',
    #     '茄子': 'http://47.98.201.222:8080/ingredients/img/eggplant/eggplant_1.jpg',
    #     '鱼': 'http://47.98.201.222:8080/ingredients/img/fish/fish_1.jpg',
    #     '香菇': 'http://47.98.201.222:8080/ingredients/img/mushroom/mushroom_2.jpg',
    #     '洋葱': 'http://47.98.201.222:8080/ingredients/img/onion/onion_4.jpg',
    #     '草莓': 'http://47.98.201.222:8080/ingredients/img/strawberry/strawberry_2.jpg',
    #     '西红柿': 'http://47.98.201.222:8080/ingredients/img/tomato/tomato_1.jpg'
    # }
    food_dict = {'id': food.id, 'name': food.name, 'introduction': food.introduction, 'nickname': food.nickname,
                 'calorie': food.calorie, 'classification': food.classification, 'dishes': food.dishes,
                 'benefits': food.benefits, 'suitable': food.suitable, 'unsuitable': food.unsuitable, 'tag': food.tag,
                 'weight': food.weight, 'choose': food.choose, 'storage': food.storage, 'conflict': food.conflict,
                 'mate': food.mate, 'pic': food.pics[0].location,
                 # 'mate': food.mate, 'pic': pic_dic[food.name],
                 'recipe':
                     [
                         {
                             'recipe_id': food.recipes[0].recipe_id,
                             'recipe_name': food.recipes[0].recipe_name,
                             'picture_link': food.recipes[0].picture_link,
                             'url': food.recipes[0].url
                         },
                         {
                             'recipe_id': food.recipes[1].recipe_id,
                             'recipe_name': food.recipes[1].recipe_name,
                             'picture_link': food.recipes[1].picture_link,
                             'url': food.recipes[1].url
                         }
                     ]
                 }
    return food_dict
