# note

## 1.flask

### 1.在8181端口运行

```shell
flask run -p 8181
flask run -p 8181 -h 192.168.137.1
```

### 2.flask分页

https://www.pianshen.com/article/1100318401/

### 3.蓝图+基于方法的视图

```python
from flask import Blueprint
from flask.views import MethodView
article_view = Blueprint('article',__name__,url_prefix='/article')
class ArticleListView(MethodView):
    def get(self,id=None):
        return 'get请求'+str(id)
    def post(self):
        return 'post请求'
article_view.add_url_rule('/list/<int:id>',view_func=ArticleListView.as_view('article_list'))
```

### 4.处理url传递的参数

```python
@admin_view.route("/req", methods=["POST", "GET"])
def req():
    # http://localhost:8181/admin/req?id=12&age=18
    print(request.args)  # ImmutableMultiDict([('id', '12'), ('age', '18')])
    print(request.args["id"])  # 12
    print(type(request.args["id"])) # <class 'str'>
    print(request.args.get("age"))  # 18
    print(type(request.args.get("age")))  # <class 'str'>
    print(list(request.args.keys()))  # ['id', 'age']
    print(list(request.args.values()))  # ['12', '18']
    req_dict = dict(request.args)  # {'id': '12', 'age': '18'}
    print(req_dict)
    return "ok"
```

## 2.http常见请求

- post侧重于对于数据的增加
- delete请求用来删除服务器的资源。
- put的侧重点在于对于数据的修改操作
- get请求是用来获取数据的，只是用来查询数据，不对服务器的数据做任何的修改，新增，删除等操作

## 3.SQLAlchemy常用指令

https://segmentfault.com/a/1190000016767008

https://www.bilibili.com/video/BV19k4y1d7G7

### 1.创建数据库表

```python
from entity.Admin import db
db.create_all()
```

### 2.一对多关系

#### 1.添加菜谱

```python
from run import db,Food,Recipe
onion=Food.query.filter(Food.name=='洋葱').first()
Sauteed_fattened_cattle_with_Onions=Recipe(recipe_name='洋葱炒肥牛',picture_link='http://47.98.201.222:8080/ingredients/img/onion/Sauteed_fattened_cattle_with_Onions.jpeg',url='https://www.douguo.com/cookbook/2389059.html',owner=onion)
db.session.add(Sauteed_fattened_cattle_with_Onions)
db.session.commit()
```

#### 2.由食材获取菜谱

```python
onion.recipes
```

[<Recipe 1>, <Recipe 2>]

```python
onion.recipes[0]
```

<Recipe 1>

```python
onion.recipes[0].recipe_name
```

'洋葱炒肉丝'

```python
onion.recipes[1].recipe_name
```

'洋葱炒肥牛'

#### 3.由菜谱获取食材

```python
a=Recipe.query.filter_by(recipe_name='洋葱炒肥牛').first()
a
```

<Recipe 2>

```python
a.recipe_name
```

'洋葱炒肥牛'

```python
a.owner
```

<Food 47>

```python
a.owner.name
```

'洋葱'

### 3.多对多关系

#### 1.添加收藏

```python
from entity.User import *
lk = User.query.filter(User.id==219).first()
from entity.Article import *
article1=Article.query.filter(Article.id==20).first()
lk
<User 219>
article1
<Article 20>
article1.favorites.append(lk)
db.session.commit()
```

#### 2.遍历收藏

```python
for user in article1.favorites:
    print(user.phone)
```

19959233359

## 4.pip库操作

### 1.导出pip库

```shell
pip freeze > config/requirements.txt
```

将pip库导出到config目录下的requirements.txt文件中

### 2.导入pip库

```shell
pip install -r requirements.txt
```

