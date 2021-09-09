# 从app_config文件中导入实例化的SQLAlchemy对象db
from config.app_config import db
# 导入蓝图
from flask import Blueprint, request, jsonify
# 导入食材实体封装的工具包
from utils.DataEncapsulation import FoodEncapsulation
# 导入食材识别的接口
from utils.Picture_Recogition import ingredient_model_10, fruit_model_131, fruit_model_25, ingredient_model_20
from utils import advanced_general
# 导入swag_from包
from flasgger import swag_from
from entity.Rate import recognition_times_plus
import random


class Food(db.Model):
    __tablename__ = 'food'
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    name = db.Column('name', db.Unicode)
    introduction = db.Column('introduction', db.Unicode)
    nickname = db.Column('nickname', db.Unicode)
    calorie = db.Column('calorie', db.Unicode)
    classification = db.Column('classification', db.Unicode)
    dishes = db.Column('dishes', db.Unicode)
    benefits = db.Column('benefits', db.Unicode)
    suitable = db.Column('suitable', db.Unicode)
    unsuitable = db.Column('unsuitable', db.Unicode)
    tag = db.Column('tag', db.Unicode)
    weight = db.Column('weight', db.Integer, default=0)
    choose = db.Column('choose', db.Unicode)
    storage = db.Column('storage', db.Unicode)
    conflict = db.Column('conflict', db.Unicode)
    mate = db.Column('mate', db.Unicode)
    recipes = db.relationship('Recipe', backref='owner')
    pics = db.relationship('Pic', backref='master')


class Recipe(db.Model):
    __tablename__ = 't_recipe'
    recipe_id = db.Column('recipe_id', db.Integer, primary_key=True, autoincrement=True)
    recipe_name = db.Column('recipe_name', db.Unicode)
    picture_link = db.Column('picture_link', db.Unicode)
    url = db.Column('url', db.Unicode)
    id = db.Column(db.Integer, db.ForeignKey('food.id'))


class Pic(db.Model):
    __tablename__ = 't_pic'
    pic_id = db.Column('pic_id', db.Integer, primary_key=True, autoincrement=True, comment='食材图片id')
    location = db.Column('location', db.String(500), nullable=False, comment='图片链接')
    id = db.Column(db.Integer, db.ForeignKey('food.id'))


food_view = Blueprint("food_view", __name__, url_prefix='/food')


@food_view.route('/retrieve_ingredient')
def retrieve_ingredient():
    """
    :desc
    检索食材
    :param
    query:查询内容
    page_num:当前页码
    page_size:每个页面几条数据
    :return:
    1.获取成功
    2.查询结果为空
    3.页码与数据量不符
    """
    request_dict = dict(request.args)
    query = request_dict['query'][0]
    page_num = int(request_dict['page_num'][0])
    page_size = int(request_dict['page_size'][0])
    if query == '':
        # 不查询东西，将所有数据分页返回
        pagination = Food.query.paginate(page=page_num, per_page=page_size, error_out=False)
        ingredient_list = []
        for item in pagination.items:
            food = FoodEncapsulation(item)
            ingredient_list.append(food)
        response = {
            'data': {
                'per_page': pagination.per_page,  # 每页多少条数据
                'current_page': pagination.page,  # 当前页码
                'total_pages': pagination.pages,  # 总共多少页
                'total': pagination.total,  # 总记录数
                'ingredient_list': ingredient_list
            },
            'meta': {
                'msg': '获取成功',
                'status': 200
            }
        }
        return jsonify(response), response['meta']['status']
    else:
        filter_list = ['.', ',', '、', '，']
        if query in filter_list:
            response = {
                'data': None,
                'meta': {
                    'msg': '查询结果为空',
                    'status': 202
                }
            }
            return jsonify(response), response['meta']['status']
        else:
            ingredient_list = []
            name_list = Food.query.filter(Food.name.like('%' + query + '%')).all()
            introduction_list = Food.query.filter(Food.introduction.like('%' + query + '%')).all()
            nickname_list = Food.query.filter(Food.nickname.like('%' + query + '%')).all()
            calorie_list = Food.query.filter(Food.calorie.like('%' + query + '%')).all()
            classification_list = Food.query.filter(Food.classification.like('%' + query + '%')).all()
            dishes_list = Food.query.filter(Food.dishes.like('%' + query + '%')).all()
            benefits_list = Food.query.filter(Food.benefits.like('%' + query + '%')).all()
            suitable_list = Food.query.filter(Food.suitable.like('%' + query + '%')).all()
            unsuitable_list = Food.query.filter(Food.unsuitable.like('%' + query + '%')).all()
            tag_list = Food.query.filter(Food.tag.like('%' + query + '%')).all()
            choose_list = Food.query.filter(Food.choose.like('%' + query + '%')).all()
            storage_list = Food.query.filter(Food.storage.like('%' + query + '%')).all()
            conflict_list = Food.query.filter(Food.conflict.like('%' + query + '%')).all()
            mate_list = Food.query.filter(Food.mate.like('%' + query + '%')).all()
            ingredient_list += name_list
            ingredient_list += introduction_list
            ingredient_list += nickname_list
            ingredient_list += calorie_list
            ingredient_list += classification_list
            ingredient_list += dishes_list
            ingredient_list += benefits_list
            ingredient_list += suitable_list
            ingredient_list += unsuitable_list
            ingredient_list += tag_list
            ingredient_list += choose_list
            ingredient_list += storage_list
            ingredient_list += conflict_list
            ingredient_list += mate_list
            ingredient_set = set(ingredient_list)
            ingredient_list.clear()
            for item in ingredient_set:
                food = FoodEncapsulation(item)
                ingredient_list.append(food)
            total_pages, left = divmod(len(ingredient_list), page_size)
            if left > 0:
                total_pages = total_pages + 1
            if page_num < 1 or page_num > total_pages:
                response = {
                    'data': None,
                    'meta': {
                        'msg': '页码与数据量不符',
                        'status': 202
                    }
                }
                return jsonify(response), response['meta']['status']
            else:
                response = {
                    'data': {
                        'per_page': page_size,
                        'current_page': page_num,
                        'total_pages': total_pages,
                        'total': len(ingredient_list),
                        'ingredient_list': ingredient_list
                    },
                    'meta': {
                        'msg': '获取成功',
                        'status': 200
                    }
                }
                return jsonify(response), response['meta']['status']


@food_view.route('/add_ingredient', methods=['POST'])
def add_ingredient():
    """
    :desc
    添加食材
    :param
    食材对象,application/json形式
    :return:
    1.添加成功
    2.该食材已存在
    """
    name_list = Food.query.filter(Food.name == request.json['name']).first()
    # 检测该食材是否已存在
    if name_list is None:
        # 不存在
        ingredient = Food(name=request.json['name'], introduction=request.json['introduction'],
                          nickname=request.json['nickname'], calorie=request.json['calorie'],
                          classification=request.json['classification'], dishes=request.json['dishes'],
                          benefits=request.json['benefits'], suitable=request.json['suitable'],
                          unsuitable=request.json['unsuitable'], tag=request.json['tag'],
                          weight=0, choose=request.json['choose'],
                          storage=request.json['storage'], conflict=request.json['conflict'],
                          mate=request.json['mate'])
        db.session.add(ingredient)
        db.session.commit()
        response = {
            'data': {
                'id': ingredient.id,
                'name': request.json['name']
            },
            'meta': {
                'msg': '添加成功',
                'status': 202
            }
        }
    else:
        # 已存在
        response = {
            'data': None,
            'meta': {
                'msg': '该食材已存在',
                'status': 200
            }
        }
    return jsonify(response), response['meta']['status']


@food_view.route('/get_recipes/<int:id>')
def get_recipes(id):
    """
    :desc
    获取菜谱
    :param id:
    :return:
    """
    ingredient = Food.query.get(id)
    recipes = []
    if len(ingredient.recipes) == 0:
        response = {
            'data': None,
            'meta': {
                'msg': '该食材暂未添加食谱',
                'status': 200
            }
        }
    else:
        for item in ingredient.recipes:
            recipe = {
                'recipe_id': item.recipe_id,
                'recipe_name': item.recipe_name,
                'picture_link': item.picture_link,
                'url': item.url
            }
            recipes.append(recipe)
        response = {
            'data': recipes,
            'meta': {
                'msg': '获取成功',
                'status': 202
            }
        }
    return jsonify(response), response['meta']['status']


@food_view.route('/upload_img', methods=['POST'])
def upload_img():
    """
    :desc
    上传图片
    :param
    图片文件
    :return:
    1.文件后缀不符合上传规定
    2.上传成功
    """
    # 1.获取文件
    file = request.files['file']
    if file.filename.split(".")[1] not in ['jpg', 'png', 'jpeg', 'JPG']:
        response = {
            'data': None,
            'meta': {
                'msg': '请上传jpg、png、jpeg、JPG的文件',
                'status': 200
            }
        }
        return jsonify(response), response['meta']['status']
    # 2.定义文件存储位置
    upload_location = 'http://47.98.201.222:8080/ingredients/img/'
    # upload_location = 'D:/flutter/'
    # 3.定义文件名
    filename = upload_location + 'img_' + str(random.randint(0, 100000)) + '_' + str(random.randint(0, 100000))
    if file.filename.endswith('.jpg'):
        filename += '.jpg'
    if file.filename.endswith('.png'):
        filename += '.png'
    if file.filename.endswith('.jpeg'):
        filename += '.jpeg'
    if file.filename.endswith('JPG'):
        filename += '.JPG'
    file.save(filename)
    response = {
        'data': {
            'filename': filename
        },
        'meta': {
            'msg': '文件上传成功',
            'status': 202
        }
    }
    return jsonify(response), response['meta']['status']


@food_view.route('/add_recipe/<int:id>', methods=['POST'])
def add_recipe(id):
    """
    :desc
    确定添加食谱，同时保存该食谱
    :return:
    """
    ingredient = Food.query.get(id)
    recipe = Recipe(recipe_name=request.json['recipe_name'], picture_link=request.json['picture_link'],
                    url=request.json['url'], owner=ingredient)
    db.session.add(recipe)
    db.session.commit()
    response = {
        'data': {
            'recipe_name': request.json['recipe_name'],
            'picture_link': request.json['picture_link'],
            'url': request.json['url']
        },
        'meta': {
            'msg': '添加成功',
            'status': 202
        }
    }
    return jsonify(response), response['meta']['status']


@food_view.route('/delete_recipe/<int:recipe_id>', methods=['DELETE'])
def delete_recipe(recipe_id):
    """
    :desc
    删除某个食谱
    :param recipe_id:
    :return:
    """
    recipe = Recipe.query.get(recipe_id)
    db.session.delete(recipe)
    db.session.commit()
    response = {
        'data': {
            'recipe_id': recipe_id
        },
        'meta': {
            'msg': '删除成功',
            'status': 202
        }
    }
    return jsonify(response)


@food_view.route('/edit_ingredient', methods=['PUT'])
def edit_ingredient():
    """
    :desc
    编辑食材
    :return:
    """
    food = Food.query.get(request.json['id'])
    food.name = request.json['name']
    food.introduction = request.json['introduction']
    food.nickname = request.json['nickname']
    food.calorie = request.json['calorie']
    food.classification = request.json['classification']
    food.dishes = request.json['dishes']
    food.benefits = request.json['benefits']
    food.suitable = request.json['suitable']
    food.unsuitable = request.json['unsuitable']
    food.tag = request.json['tag']
    food.choose = request.json['choose']
    food.storage = request.json['storage']
    food.conflict = request.json['conflict']
    food.mate = request.json['mate']
    db.session.commit()
    response = {
        'data': {
            'id': request.json['id'],
            'name': request.json['name']
        },
        'meta': {
            'msg': '修改成功',
            'status': 202
        }
    }
    return jsonify(response), response['meta']['status']


@food_view.route('/picture', methods=['POST'])
@swag_from('API_properties/Food/food_picture.yml')
def picture():
    recognition_times_plus(1)
    bytes_base64 = request.get_data()  # 获得加密后的base64，类型为bytes
    # print(type(data))#打印前端传过来的数据的类型
    # print(data)#打印前端传过来的数据
    str_base64 = bytes_base64.decode('utf8')  # 通过decode将bytes转成str
    # print(type(data))#str
    result_name = ingredient_model_10(str_base64)
    food = Food.query.filter(Food.name == result_name).first()
    return FoodEncapsulation(food), 200


@food_view.route('/photo', methods=['POST'])  # http请求的结果
@swag_from('API_properties/Food/food_photo.yml')
def photo():
    bytes_base64 = request.get_data()  # 前端传的数据是bytes类型的base64
    # data=str(data)
    str_base64 = bytes_base64.decode('utf8')  # 转成str类型的base64
    # data2 = unquote(data1, 'utf-8')
    # print(type(data2))
    # print(data2)
    # for index in range(0, 10):
    #     if (data2[index] == '/'):
    #         break
    # data3 = data2[index:]
    # print(data3)
    get_json_data = advanced_general.photo(str_base64)
    # print(get_json_data)
    # print(type(get_json_data))
    # print('-----------------------')
    # for item in range(0,len(get_json_data)):
    #     print(get_json_data[item])
    # print(get_json_data[0])
    food = Food.query.filter(Food.name == get_json_data[0]).first()
    return FoodEncapsulation(food), 200


@food_view.route('/getFood', methods=['GET'])
@swag_from('API_properties/Food/food_getFood.yml')
def send_data():
    index_to_label = ['冬虫夏草',
                      '菠萝',
                      '胡萝卜',
                      '草莓',
                      '香菇',
                      '鲍鱼',
                      '海参',
                      '洋葱',
                      '榴莲',
                      '西红柿',
                      '金针菇',
                      '牛油果',
                      '苹果',
                      '银耳',
                      '香蕉',
                      '人参',
                      '西兰花',
                      '腰果',
                      '茄子',
                      '杨桃']
    foods = []
    for item in index_to_label:
        food = Food.query.filter(Food.name == item).first()
        foods.append(food)
    # foods = Food.query.filter(Food.name != '香蕉').all()  # 从数据库中获取所有的食材，将所有食材放在列表foods中
    # print(foods)
    food_list = []
    for i in range(0, len(foods)):
        food_dict = FoodEncapsulation(foods[i])
        food_list.append(food_dict)
    result_dict = {
        'result': food_list
    }
    return result_dict, 200


@food_view.route('/search/<content>', methods=['GET'])
@swag_from('API_properties/Food/food_search.yml')
def search(content):
    print('用户输入的搜索内容:' + content)
    # 过滤掉常用的标点符号
    if content == ',' or content == '、' or content == '，':
        return {'result': []}, 404
    else:
        # 从标签字段中模糊查询，查询结果置入列表temp_list
        temp_list = Food.query.filter(Food.tag.like('%' + content + '%')).all()
        print('根据标签查询到的数据：', temp_list)
        if len(temp_list) <= 0:
            return {'result': []}, 404
        else:
            # 将临时列表中的temp_list的food对象封装到result_list列表中
            result_list = []
            for i in range(0, len(temp_list)):
                result_list.append(FoodEncapsulation(temp_list[i]))
            # 将result_list列表打包在字典中
            search_result_dict = {
                'result': result_list
            }
            return search_result_dict, 200


@food_view.route('/classify', methods=['GET'])
@swag_from('API_properties/Food/food_classify.yml')
def classify():
    # 蔬菜类
    vegetable_list = []
    vegetables = Food.query.filter(Food.classification.like('%蔬菜%')).all()
    for item in vegetables:
        vegetable_list.append(FoodEncapsulation(item))
    # 水果类
    fruit_list = []
    fruits = Food.query.filter(Food.classification.like('%水果%')).all()
    for item in fruits:
        fruit_list.append(FoodEncapsulation(item))
    # 菌类
    fungus_list = []
    fungus = Food.query.filter(Food.classification.like('%菌%')).all()
    for item in fungus:
        fungus_list.append(FoodEncapsulation(item))
    # 谷类
    cereal_list = []
    cereals = Food.query.filter(Food.classification.like('%谷%')).all()
    for item in cereals:
        cereal_list.append(FoodEncapsulation(item))
    # 其它类
    something_else_list = []
    # 分类结果字典
    classify_result_dict = {
        '蔬菜类': vegetable_list,
        '水果类': fruit_list,
        '菌类': fungus_list,
        '谷类': cereal_list,
        '其它类': something_else_list
    }
    return classify_result_dict, 200


# 生成菜谱post请求示例：
# 请求地址：http://localhost:5000/generateRecipe/草莓
# {
#     "recipe_name":"草莓酸奶慕斯蛋糕",
#     "picture_link":"http://47.98.201.222:8080/ingredients/img/strawberry/Strawberry_yogurt_mousse_cake.jpeg",
#     "url":"https://www.douguo.com/cookbook/2427951.html"
# }
@food_view.route('/generateRecipe/<food_name>', methods=['POST'])
@swag_from('API_properties/Food/food_generateRecipe.yml')
def recipe_data_generator(food_name):
    # 获取食材对象
    # food=Food.query.filter(Food.name==request.json['food']).first()
    food = Food.query.filter(Food.name == food_name).first()
    recipe = Recipe(recipe_name=request.json['recipe_name'], picture_link=request.json['picture_link'],
                    url=request.json['url'], owner=food)
    db.session.add(recipe)
    db.session.commit()
    if (Recipe.query.filter(Recipe.recipe_name == request.json['recipe_name']).count()) > 0:
        return 'success', 200
    else:
        return 'failure', 400


@food_view.route('/fruit_recognition_131', methods=['POST'])
def fruit_recognition_131():
    """
    :desc:
        模型：lk_fruit_131.h5
    :return:
    """
    recognition_times_plus(2)  # 统计模型识别次数
    bytes_base64 = request.get_data()  # 获得加密后的base64，类型为bytes
    str_base64 = bytes_base64.decode('utf8')  # 通过decode将bytes转成str，编码为utf-8
    result_name = fruit_model_131(str_base64)
    # food = Food.query.filter(Food.name == result_name).first()
    # return FoodEncapsulation(food), 200
    return result_name


@food_view.route('/fruit_recognition_25', methods=['POST'])
def fruit_recognition_25():
    """
    :desc:
        模型：lk_fruit_25.h5
    :return:
    """
    # recognition_times_plus(3)  # 统计模型识别次数
    bytes_base64 = request.get_data()  # 获得加密后的base64，类型为bytes
    str_base64 = bytes_base64.decode('utf8')  # 通过decode将bytes转成str，编码为utf-8
    result_name = fruit_model_25(str_base64)
    # food = Food.query.filter(Food.name == result_name).first()
    # return FoodEncapsulation(food), 200
    return result_name


@food_view.route('/ingredient_recognition_20', methods=['POST'])
def ingredient_recognition_20():
    """
    :desc:
        模型：lk_ingredient_20.h5
    :return:
    """
    # recognition_times_plus(4)  # 统计模型识别次数
    bytes_base64 = request.get_data()  # 获得加密后的base64，类型为bytes
    str_base64 = bytes_base64.decode('utf8')  # 通过decode将bytes转成str，编码为utf-8
    result_name = ingredient_model_20(str_base64)
    food = Food.query.filter(Food.name == result_name).first()
    return FoodEncapsulation(food), 200
    # return result_name
