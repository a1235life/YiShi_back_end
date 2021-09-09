import xlrd

from entity.Food import db, Food, Recipe, Pic

# 导入需要读取的Excel表格的路径

# 如果路径或者文件名有中文给前面加一个字符

# 读取文件
# workbook = xlrd.open_workbook(r'D:\\AI Projects\\food-material\\数据收集\\食材数据\\20210121食材的基本信息.xlsx')
workbook = xlrd.open_workbook(r'D:\\AI Projects\\food-material\\数据收集\\食材数据\\20210121食谱信息.xlsx')
# 根据文件的sheet获取表格
table = workbook.sheets()[0]

# 表格行数
rows = table.nrows
# print(rows)

# 表格列数
cols = table.ncols
# print(cols)
labels = table.row_values(0, start_colx=0, end_colx=cols)
# print(labels)
food_list = []
for row in range(1, rows):
    # 返回第row行中从第0列到第table.ncols列的数据组成的列表
    data = table.row_values(row, start_colx=0, end_colx=cols)
    # print(data)
    food = {}
    for col in range(0, cols):
        food[labels[col]] = data[col]
    food_list.append(food)


# print(food_list)

def table_food():
    """
    :desc
        将食材excel表数据写入数据库
    :return:
    """
    ingredient_list = []
    for item in range(0, len(food_list)):
        ingredient = Food(name=food_list[item]['name'], introduction=food_list[item]['introduction'],
                          nickname=food_list[item]['nickname'], calorie=food_list[item]['calorie'],
                          classification=food_list[item]['classification'], dishes=food_list[item]['dishes'],
                          benefits=food_list[item]['benefits'], suitable=food_list[item]['suitable'],
                          unsuitable=food_list[item]['unsuitable'], tag='',
                          weight=0, choose=food_list[item]['choose'],
                          storage=food_list[item]['storage'], conflict=food_list[item]['conflict'],
                          mate=food_list[item]['mate'])
        ingredient_list.append(ingredient)
    db.session.add_all(ingredient_list)
    db.session.commit()


# print(food_list[1]['name'])


# table_food()


def table_pic():
    """
    :desc
        将食材图片写入数据库
    :return:
    """
    import os
    from pypinyin import pinyin
    # 文件夹列表
    dir_list = os.listdir('D:\\AI Projects\\food-material\\数据收集\\食材数据\\20210121图片')
    pic_list = []
    log_list = []
    for item in range(0, len(food_list)):
        # excel表中的食材名food_list[item]['name']
        pinyin_list = pinyin(food_list[item]['name'])
        name = ''
        for word in pinyin_list:
            name += word[0] + '_'
        name = name.strip('_')
        if name in dir_list:
            # http://47.98.201.222:8080/ingredients/img/onion/onion_4.jpg
            location = 'http://47.98.201.222:8080/ingredients/img/' + name + '/1.jpg'
            # location = 'D:\\AI Projects\\food-material\\数据收集\\食材数据\\20210121图片\\' + name + '\\1.jpg'
            pic_list.append({'location': location, 'name': food_list[item]['name']})
        else:
            log_list.append(food_list[item]['name'])
    commit_list = []
    for pic in pic_list:
        master = Food.query.filter(Food.name == pic['name']).first()
        commit = Pic(location=pic['location'], master=master)
        commit_list.append(commit)
    db.session.add_all(commit_list)
    db.session.commit()
    # print(log_list)
    # ['火腿', '猪肚', '猪血', '牛排', '牛腩', '肥牛', '牛蹄筋', '牛肚', '牛里脊', '牛尾', '牛心', '羊后腿', '羊蝎子', '羊肚', '羊腿', '鸡腿', '鸡爪',
    # '鸭腿', '鸭血', '牛蛙', '驴肉', '柚子', '柿子', '石榴', '橙子', '桔子', '桂圆', '榴莲', '金桔', '李子', '椰子', '牛油果', '桂花', '莲子', '松子',
    # '栗子', '枸杞', '榛子', '瓜子仁', '山楂干', '干枣', '桃脯', '胡萝卜', '白萝卜', '芋头', '茄子', '韭菜', '芥蓝', '荠菜', '韭黄', '牛蒡', '鸡腿菇',
    # '牛肝菌', '黑牛肝菌', '黄皮牛肝菌', '滑子菇', '羊肚菌', '罗汉果', '人参', '阿胶', '肉桂', '对虾', '梭子蟹', '蛤蜊', '蛏子', '生蚝', '文蛤', '河蚬', '鲅鱼',
    # '桂鱼', '秋刀鱼', '罗非鱼', '虹鳟鱼', '华子鱼', '海参', '海蜇', '金枪鱼罐头', '蟹柳', '鱼干', '干鱿鱼', '粳米', '燕麦片', '牛奶', '绿豆', '牛至', '茴香',
    # '罗勒', '薄荷', '咖喱粉', '老干妈', '牛肉酱']
    # print(len(log_list))
    # 91


# table_pic()


def table_recipe():
    """
    :desc
        将食谱excel表数据写入数据库
    :return:
    """
    index_to_label = ['冬虫夏草',
                      '菠萝',
                      '鲍鱼',
                      '海参',
                      '榴莲',
                      '金针菇',
                      '牛油果',
                      '银耳',
                      '人参',
                      '腰果',
                      '杨桃']
    label_to_index = [
        'cordyceps',
        'pineapple',
        'abalone', 'trepang', 'durian', 'enoki_mushroom', 'avocado', 'tremella', 'ginseng',
        'cashew', 'carambola']
    recipe_list = []
    flag = True
    for item in range(0, len(food_list)):
        if food_list[item]['name'] in index_to_label:
            index = index_to_label.index(food_list[item]['name'])
            if flag:
                picture_link = 'http://47.98.201.222:8080/ingredients/img/' + label_to_index[index] + '/2.jpg'
                flag = False
            else:
                picture_link = 'http://47.98.201.222:8080/ingredients/img/' + label_to_index[index] + '/3.jpg'
                flag = True
            owner = Food.query.filter(Food.name == food_list[item]['name']).first()
            recipe = Recipe(recipe_name=food_list[item]['recipe_name'],
                            picture_link=picture_link,
                            url=food_list[item]['url'],
                            owner=owner)
            recipe_list.append(recipe)
    db.session.add_all(recipe_list)
    db.session.commit()


table_recipe()
