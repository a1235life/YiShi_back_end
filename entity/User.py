# 从app_config文件中导入实例化的SQLAlchemy对象db
from config.app_config import db, app
from flask import Blueprint, request, jsonify, session, redirect, url_for, make_response
from utils.DictToObject import dict_to_object
# 导入swag_from包
from flasgger import swag_from
from entity.Verification import send_email, get_one
from entity.Article import find_article_by_id
from datetime import datetime, timedelta
from functools import wraps
# 密码加密工具
from werkzeug.security import check_password_hash, generate_password_hash

# 实现收藏功能的多对多关系
favorite = db.Table('favorite',
                    db.Column('favorite_id', db.Integer, primary_key=True, autoincrement=True, comment='收藏id'),
                    db.Column('user_id', db.Integer, db.ForeignKey('t_user.id'), nullable=False, comment='用户id'),
                    db.Column('article_id', db.Integer, db.ForeignKey('t_article.id'), nullable=False, comment='文章id')
                    )


class User(db.Model):
    __tablename__ = 't_user'
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    username = db.Column('username', db.Unicode)
    password = db.Column('password', db.Unicode)
    phone = db.Column('phone', db.Unicode)
    email = db.Column('email', db.String(30), comment='电子邮箱')
    favorites = db.relationship('Article', secondary=favorite, backref=db.backref('favorites', lazy='dynamic'))

    def __init__(self, username, password, phone, email):
        self.username = username
        self.password = password
        self.phone = phone
        self.email = email

    def create_user(self):
        user = User(username=self.username, password=self.password, phone=self.phone, email=self.email)
        db.session.add(user)
        db.session.commit()

    def delete_user(self):
        db.session.delete(self)
        db.session.commit()

    def update_user(self):
        user = User.query.filter_by(id=self.id).first()
        user.username = self.username
        user.password = self.password
        user.phone = self.phone
        user.email = self.email
        db.session.commit()

    def retrieve_user(tag, content):

        if tag == 'username':
            user = User.query.filter_by(username=content).first()
        if tag == 'phone':
            user = User.query.filter_by(phone=content).first()
        if user is None:
            return 'null'
        else:
            return user


user_view = Blueprint("user_view", __name__, url_prefix='/user')


@user_view.route('')
def index():
    return '用户模块根目录'


@user_view.route('/retrieve_user')
def retrieve_user():
    """
    :desc
    用户管理检索功能
    :param
    :return:
    """
    request_dict = dict(request.args)
    query = request_dict['query']
    page_num = int(request_dict['page_num'])
    page_size = int(request_dict['page_size'])
    if query == '':
        # 不查询东西，将所有数据分页返回
        pagination = User.query.paginate(page=page_num, per_page=page_size, error_out=False)
        user_list = []
        for item in pagination.items:
            user = {
                'id': item.id,
                'username': item.username,
                'phone': item.phone,
                'email': item.email
            }
            user_list.append(user)
        response = {
            'data': {
                'per_page': pagination.per_page,  # 每页多少条数据
                'current_page': pagination.page,  # 当前页码
                'total_pages': pagination.pages,  # 总共多少页
                'total': pagination.total,  # 总记录数
                'user_list': user_list
            },
            'meta': {
                'msg': '获取成功',
                'status': 200
            }
        }
        return jsonify(response), response['meta']['status']
    else:
        filter_list = ['@', '.']
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
            user_list = []
            # id_list = User.query.filter(User.id.like('%' + query + '%')).all()
            username_list = User.query.filter(User.username.like('%' + query + '%')).all()
            phone_list = User.query.filter(User.phone.like('%' + query + '%')).all()
            email_list = User.query.filter(User.email.like('%' + query + '%')).all()
            # user_list += id_list
            user_list += username_list
            user_list += phone_list
            user_list += email_list
            user_set = set(user_list)
            user_list.clear()
            for item in user_set:
                user = {
                    'id': item.id,
                    'username': item.username,
                    'phone': item.phone,
                    'email': item.email
                }
                user_list.append(user)
            total_pages, left = divmod(len(user_list), page_size)
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
                        'total': len(user_list),
                        'user_list': user_list
                    },
                    'meta': {
                        'msg': '获取成功',
                        'status': 200
                    }
                }
                return jsonify(response), response['meta']['status']


@user_view.route('/add_user', methods=['POST'])
def add_user():
    username_user = User.query.filter(User.username == request.json['username']).first()
    # 检测昵称是否被注册过
    if username_user is None:
        # 检测手机号是否被注册过
        phone_user = User.query.filter(User.phone == request.json['phone']).first()
        if phone_user is None:
            # 检测邮箱是否被注册过
            email_user = User.query.filter(User.email == request.json['email']).first()
            if email_user is None:
                # 昵称、手机号、邮箱都没被注册过
                user = User(username=request.json['username'],
                            password=generate_password_hash(request.json['password']), phone=request.json['phone'],
                            email=request.json['email'])
                # 添加数据
                db.session.add(user)
                db.session.commit()
                response = {
                    'data': {
                        'username': request.json['username'],
                        'password': request.json['password'],
                        'phone': request.json['phone'],
                        'email': request.json['email']
                    },
                    'meta': {
                        'msg': '添加成功',
                        'status': 202
                    }
                }
            else:
                response = {
                    'data': None,
                    'meta': {
                        'msg': '该邮箱已被注册',
                        'status': 200
                    }
                }
        else:
            response = {
                'data': None,
                'meta': {
                    'msg': '该手机号已被注册',
                    'status': 200
                }
            }
    else:
        response = {
            'data': None,
            'meta': {
                'msg': '该昵称已被注册',
                'status': 200
            }
        }
    return jsonify(response), response['meta']['status']


@user_view.route('/modify_user/<int:id>', methods=['PUT'])
def modify_user(id):
    """
    :desc 修改用户
    :param id: 用户id
    :return: 修改成功
    """
    user = User.query.filter(User.id == id).first()
    user_username = User.query.filter(User.username == request.json['username']).first()
    if (user_username is None) or (user.username == user_username.username):
        user_phone = User.query.filter(User.phone == request.json['phone']).first()
        if (user_phone is None) or (user.phone == user_phone.phone):
            user_email = User.query.filter(User.email == request.json['email']).first()
            if (user_email is None) or (user.email == user_email.email):
                user.username = request.json['username']
                user.phone = request.json['phone']
                user.email = request.json['email']
                db.session.commit()
                response = {
                    'data': {
                        'id': id,
                        'username': request.json['username'],
                        'phone': request.json['phone'],
                        'email': request.json['email']
                    },
                    'meta': {
                        'msg': '修改成功',
                        'status': 202
                    }
                }
            else:
                response = {
                    'data': {
                        'id': id,
                        'username': request.json['username'],
                        'phone': request.json['phone'],
                        'email': request.json['email']
                    },
                    'meta': {
                        'msg': '该邮箱已被使用',
                        'status': 200
                    }
                }
        else:
            response = {
                'data': {
                    'id': id,
                    'username': request.json['username'],
                    'phone': request.json['phone'],
                    'email': request.json['email']
                },
                'meta': {
                    'msg': '该手机号已被使用',
                    'status': 202
                }
            }
    else:
        response = {
            'data': {
                'id': id,
                'username': request.json['username'],
                'phone': request.json['phone'],
                'email': request.json['email']
            },
            'meta': {
                'msg': '该昵称已被使用',
                'status': 202
            }
        }
    return jsonify(response), response['meta']['status']


@user_view.route('/delete_user/<int:id>', methods=['DELETE'])
def delete_user(id):
    user = User.query.filter(User.id == id).first()
    db.session.delete(user)
    db.session.commit()
    response = {
        'data': {
            'id': id
        },
        'meta': {
            'msg': '删除成功',
            'status': 202
        }
    }
    return jsonify(response), response['meta']['status']


# # 登录验证
# @user_view.route('/login/<phone>/<password>')
# @swag_from('API_properties/User/user_login.yml')
# def login_controller(phone, password):
#     if User.query.filter(User.phone == phone).count() > 0:
#         result = User.query.filter(User.phone == phone).first()
#         if check_password_hash(result.password, password):
#             return '登录成功', 200
#         if result.password == password:
#             return 'Success!', 200
#         else:
#             return 'Wrong password.', 400
#     else:
#         return 'This phone number does not exist.', 404

# 登录验证
# Input:
# {
#   'login': '手机号或用户名或邮箱',
#   'password': 'lk123'
# }
@user_view.route('/login', methods=['POST'])
def login_controller():
    if User.query.filter(User.phone == request.json['login']).count() > 0:
        result = User.query.filter(User.phone == request.json['login']).first()
        if check_password_hash(result.password, request.json['password']):
            return '登录成功', 200
        if result.password == request.json['password']:
            return 'Success!', 200
        else:
            return 'Wrong password.', 400
    if User.query.filter(User.email == request.json['login']).count() > 0:
        result = User.query.filter(User.email == request.json['login']).first()
        if check_password_hash(result.password, request.json['password']):
            return '登录成功', 200
        if result.password == request.json['password']:
            return 'Success!', 200
        else:
            return 'Wrong password.', 400
    if User.query.filter(User.username == request.json['login']).count() > 0:
        result = User.query.filter(User.username == request.json['login']).first()
        if check_password_hash(result.password, request.json['password']):
            return '登录成功', 200
        if result.password == request.json['password']:
            return 'Success!', 200
        else:
            return 'Wrong password.', 400
    else:
        return 'This user does not exist.', 404


# flask-rest plus
# 注册验证
@user_view.route('/register', methods=['POST'])
def register_controller():
    """
    :param:
    {
        'phone': '19959233359',
        'username': 'a1235life',
        'email': 'a1235life@gmail.com',
        'password': 'bitter_tea'
    }
    :return:
    1.手机号已被注册，400
    2.账号已被注册，405
    3.邮箱已被注册，406
    4.注册成功，200
    """
    if (User.query.filter(User.phone == request.json['phone']).count()) > 0:
        return 'This phone number has been registered', 400
    if (User.query.filter(User.username == request.json['username']).count()) > 0:
        return 'This username already exists', 405
    if (User.query.filter(User.email == request.json['email']).count()) > 0:
        return 'This email has been registered', 406
    user = dict_to_object(request.json)
    User.create_user(user)
    return 'success', 200


# 分页查询所有
@user_view.route('/findAll/<page>/<size>', methods=['GET'])
def find_all_users(page, size):
    # 获取所有对象
    users = User.query.all()
    # total为对象的数量
    total = len(users)
    # 如果一页有size个对象，则需要max_page页；left为total除以size的余数
    max_page, left = divmod(int(total), int(size))
    if left > 0:
        max_page = max_page + 1
    if int(page) < 1 or int(page) > max_page:
        return 'Please input the right page.Page ranges from 1~%s' % max_page, 400
    else:
        start = ((int(page) - 1) * int(size))
        end = int(page) * int(size)
        # print(start)
        # print(end)
        # print(users)
        content = []
        sort = {"sorted": False, "unsorted": True, "empty": True}
        pageable = {"sort": sort, "pageNumber": int(page) - 1, "pageSize": int(size), "offset": 0, "unpaged": False,
                    "paged": True}
        for user in users:
            user_dict = {'id': user.id, 'username': user.username, 'password': user.password, 'phone': user.phone}
            content.append(user_dict)
        # print(content)
        data = content[start:end]
        result = {"content": data, "pageable": pageable, "totalPages": max_page, "totalElements": total, "last": False,
                  "sort": sort, "numberOfElements": int(size), "first": True, "size": int(size), "number": 0,
                  "empty": False}
        return jsonify(result), 200


@user_view.route('/deleteUserById/<id>', methods=['DELETE'])
@swag_from('API_properties/User/user_deleteUserById.yml')
def delete_user_by_id(id):
    if (User.query.filter(User.id == id).count()) > 0:
        user = User.query.filter(User.id == id).first()
        User.delete_user(user)
        if (User.query.filter(User.id == id).count()) == 0:
            return '删除成功!!', 200
    else:
        return '该用户不存在，删除失败！！', 404
    return '操作失败！！！', 400


@user_view.route('/saveUser', methods=['POST'])
def save_user():
    if (User.query.filter(User.phone == request.json['phone']).count()) > 0:
        return 'This phone number has been registered'
    if (User.query.filter(User.username == request.json['username']).count()) > 0:
        return 'This username already exists'
    user = dict_to_object(request.json)
    User.create_user(user)
    return 'success'


@user_view.route('/findUserById/<id>', methods=['GET'])
def find_user_by_id(id):
    user = User.query.filter(User.id == id).first()
    user_dict = {'id': id, 'username': user.username, 'password': user.password, 'phone': user.phone}
    return user_dict


@user_view.route('/updateUser', methods=['PUT'])
@swag_from('API_properties/User/user_updateUser.yml')
def update_user():
    """
    :param
    {
    "id": 582,
    "username": "test_user_23",
    "password": "test_pwd_23",
    "phone": "10000000023",
    "email": "a1235fe@gmail.com"
    }
    :return:
    1.用户不存在，404
    2.修改成功，200
    3.修改失败，400
    """
    if (User.query.filter_by(id=request.json['id']).count()) > 0:
        User.update_user(dict_to_object(request.json))
    else:
        return 'This user does not exist.', 404
    user = User.query.filter_by(id=request.json['id']).first()
    if (user.username == request.json['username'] and user.password == request.json['password'] and user.phone ==
            request.json['phone']):
        return 'success', 200
    else:
        return 'error', 400


@user_view.route('/findUserByKeyword/<tag>/<content>', methods=['GET'])
def find_user_by_keyword(tag, content):
    result = User.retrieve_user(tag, content)
    # print(result)

    if result == 'null':
        return 'null'

    if tag == "username" or tag == "phone":
        user_dict = {'id': result.id, 'username': result.username, 'password': result.password, 'phone': result.phone}
        return user_dict


# app.logger.info('id为%d的有%d个', count, count)
@user_view.route('/validate_email', methods=['POST'])
def validate_email():
    """
    :description
    向给定邮箱发送验证码
    :param
    {
        'email': 'a1235life@gmail.com'
    }
    :return
    {
        'result': '验证码已发送到该邮箱中',
        'code': 'ivKu'
    }
    """
    user = User.query.filter(User.email == request.json['email']).first()
    if user is None:
        response = {
            'result': '该邮箱没有对应的用户'
        }
        return jsonify(response)
    app.logger.info('修改密码：用户的邮箱为' + user.email)
    # 获取一个验证码
    code = get_one()
    app.logger.info('修改密码：验证码为%s', code['code'])
    flag = send_email(user.email, code['code'])
    if flag == 'success':
        app.logger.info('修改密码：验证码邮件发送成功')
        response = {
            'result': '验证码已发送到该邮箱中',
            'code': code['code']
        }
        return jsonify(response)
    else:
        response = {
            'result': '验证码发送失败'
        }
        app.logger.info('修改密码：验证码邮件发送失败')
        return jsonify(response)


# 将给定的邮箱用户的密码修改成给定的密码
# Input:
# {
#   'email': 'a1235life@gmail.com',
#   'password': 'lk123'
# }
# Output:
# {
#   'result': '密码修改成功'
# }
@user_view.route('/password_modify', methods=['PUT'])
def password_modify():
    user_email = request.json['email']
    user = User.query.filter(User.email == user_email).first()
    if user is None:
        response = {
            'result': '该邮箱没有对应的用户'
        }
        return jsonify(response)
    # 密码加密存储
    user.password = generate_password_hash(request.json['password'])
    User.update_user(user)
    response = {
        'result': '密码修改成功'
    }
    return jsonify(response)


# 将给定的邮箱用户的密码修改成给定的密码
# Input:
# {
#   'email': 'a1235life@gmail.com',
#   'username': 'a1235life'
# }
# Output:
# {
#   'result': '邮箱绑定成功'
# }
@user_view.route('/bind_email', methods=['PUT'])
def bind_email():
    user = User.query.filter(User.username == request.json['username']).first()
    if user is None:
        response = {
            'result': '该账号没有对应的用户'
        }
        return jsonify(response)
    user.email = request.json['email']
    User.update_user(user)
    response = {
        'result': '邮箱绑定成功'
    }
    return jsonify(response)


# {
#     'user_id':1,
#     'article_id':3
# }
# 用户收藏一篇文章，user_id代表用户的id，article_id代表文章的id
@user_view.route('/add_one_favorite', methods=['PUT'])
def add_one_favorite():
    user_id = request.json['user_id']
    article_id = request.json['article_id']
    article = find_article_by_id(article_id)
    if article == '该文章不存在':
        return '该文章不存在'
    # article.favorites为列表
    for user in article.favorites:
        if user.id == user_id:
            return '该文章已被收藏'
    user = User.query.filter(User.id == user_id).first()
    article.favorites.append(user)
    db.session.commit()
    return '收藏成功'


# 获取用户的收藏
@user_view.route('/get_favorites/<int:id>')
def get_favorites(id):
    user = User.query.filter(User.id == id).first()
    favorites_dict = {
        'favorite_list': []
    }
    # user.favorites为列表
    for item in user.favorites:
        article = {
            'id': item.id,
            'location': item.location,
            'weight': item.weight,
            'article_name': item.article_name,
            'cover_pic': item.cover_pic
        }
        favorites_dict['favorite_list'].append(article)
    return favorites_dict


# 1.使用session完成登录验证
# 2.使用cookie完成记住密码
# 3.在登录框下加入”一周内免登录“或”记住密码“的勾选框来作为记住密码的形式
# 4.记住密码后要直接登录到管理页面，不要再出现登陆页面
# 5.当用户选择注销时，要删除cookie和session
# 6.cookie内不能存敏感信息

# 浏览器端也可以通过session['admin']获取用户名
@user_view.route('/test')
def login_test():
    if session.get('user', None) is None:  # session.get('key',默认值)，也可以用session['key']
        # return redirect(url_for('user_view.index'))
        return 'session没登录'
    else:
        return 'session登录了'


# 管理用户会话状态session
@user_view.route('/login_test/<username>', methods=['DELETE', 'POST'])
def status_manager(username):
    if request.method == 'DELETE':
        session.pop('user')
        return 'session没了'
    if request.method == 'POST':
        session['user'] = username
        return 'session有了'


# 设置Cookie
@user_view.route('/set_cookie')
def set_my_cookie():
    resp = make_response('ok', 200)
    # resp.set_cookie('username', 'lk')  # cookie中以键值对形式
    # domain作用域名、path作用路径、max_age生命周期秒数、expires过期时间
    # 设置cookie七天过期
    resp.set_cookie('username', 'lk', path='/', expires=datetime.now() + timedelta(days=7))
    return resp


# 取得cookie
@user_view.route('/get_cookie')
def get_my_cookie():
    cookie = request.cookies.get('username', None)
    if cookie:
        return cookie
    return '没找到cookie'


# 移除cookie
@user_view.route('/remove_cookie')
def remove_cookie():
    resp = make_response('删除cookie')
    # 将cookie的值设为空，过期时间设置为当前时间的前一分钟或者0（即当前时间）
    # 通过重设cookie的使用时间强行过期来完成移除cookie的操作
    resp.set_cookie('username', '', expires=datetime.now() + timedelta(minutes=-1))
    return resp


# 装饰器装饰多个视图函数
def wrapper(func):
    @wraps(func)  # 保存原来函数的所有属性,包括文件名
    def inner(*args, **kwargs):
        # 校验session
        if session.get("user"):
            ret = func(*args, **kwargs)  # func = home
            return ret
        else:
            return '登录页面'

    return inner
