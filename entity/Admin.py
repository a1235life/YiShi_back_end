# 导入数据库实例化对象db
from config.app_config import db
# 导入flask的蓝图和http请求的request
from flask import Blueprint, request, jsonify, session, make_response
from werkzeug.security import check_password_hash, generate_password_hash
from utils.DictToObject import dict_to_object
from entity.Verification import get_one, send_email
from datetime import datetime, timedelta
from functools import wraps


# 装饰器，用于装饰多个视图函数
# 判断用户是否使用此视图函数
def wrapper(func):
    @wraps(func)  # 保存原来函数的所有属性,包括文件名
    def inner(*args, **kwargs):
        # 校验session
        if session.get('username', None) is None:
            ret = func(*args, **kwargs)  # func = home
            return ret
        else:
            response = {
                'data': None,
                'meta': {
                    'msg': '您无权使用此功能',
                    'status': 200
                }
            }
            return jsonify(response), response['meta']['status']

    return inner


role_auth = db.Table('role_auth',
                     db.Column('id', db.Integer, primary_key=True, autoincrement=True, comment='角色-权限关系序列'),
                     db.Column('role_id', db.Integer, db.ForeignKey('role.role_id'), nullable=False, comment='角色id'),
                     db.Column('auth_id', db.Integer, db.ForeignKey('auth.auth_id'), nullable=False, comment='权限id'))


# Role实体对象
class Role(db.Model):
    __tablename__ = 'role'
    role_id = db.Column('role_id', db.Integer, primary_key=True, autoincrement=True, comment='角色表序列')
    role_name = db.Column('role_name', db.String(10), unique=True, nullable=False, comment='角色名')
    role_desc = db.Column('role_desc', db.String(50), nullable=False, comment='角色描述')
    admins = db.relationship('Admin', backref='parent')
    properties = db.relationship('Auth', secondary=role_auth, backref=db.backref('properties', lazy='dynamic'))


role_view = Blueprint("role_view", __name__, url_prefix='/role')


@role_view.route('/add_role', methods=['POST'])
@wrapper
def add_role():
    """
    :param
    {
        'role_name': '超级管理员',
        'role_desc': '拥有所有权限'
    }
    :return:
    """
    role = Role.query.filter(Role.role_name == request.json['role_name']).first()
    if role is None:
        add = Role(role_name=request.json['role_name'], role_desc=request.json['role_desc'])
        db.session.add(add)
        db.session.commit()
        response = {
            'data': {
                'role_name': request.json['role_name'],
                'role_desc': request.json['role_desc']
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
                'msg': '该角色已存在',
                'status': 200
            }
        }
    return jsonify(response), response['meta']['status']


@role_view.route('/edit_role/<int:role_id>', methods=['PUT'])
@wrapper
def edit_role(role_id):
    """
    :param
    {
        'role_name': '测试员',
        'role_desc': '测试专用'
    }
    :return:
    """
    role = Role.query.filter(Role.role_id == role_id).first()
    if role.role_name == request.json['role_name'] and role.role_desc == request.json['role_desc']:
        # 一点都没改过就返回请修改后再提交
        response = {
            'data': None,
            'meta': {
                'msg': '请修改后再提交',
                'status': 200
            }
        }
    else:
        # 修改过,判断修改后的内容是否与其他数据重复
        role_name = Role.query.filter(Role.role_name == request.json['role_name']).first()
        role_desc = Role.query.filter(Role.role_desc == request.json['role_desc']).first()
        # 修改后的内容不与其他数据重复
        if role_name is None or role_desc is None:
            role.role_name = request.json['role_name']
            role.role_desc = request.json['role_desc']
            db.session.commit()
            response = {
                'data': {
                    'role_id': role_id,
                    'role_name': request.json['role_name'],
                    'role_desc': request.json['role_desc']
                },
                'meta': {
                    'msg': '修改成功',
                    'status': 202
                }
            }
        else:
            response = {
                'data': None,
                'meta': {
                    'msg': '数据重复了，修改失败',
                    'status': 200
                }
            }
    return jsonify(response), response['meta']['status']


@role_view.route('/delete_role/<int:role_id>', methods=['DELETE'])
@wrapper
def delete_role(role_id):
    role = Role.query.get(role_id)
    db.session.delete(role)
    db.session.commit()
    response = {
        'data': {
            'role_id': role_id
        },
        'meta': {
            'msg': '删除成功',
            'status': 202
        }
    }
    return jsonify(response), response['meta']['status']


@role_view.route('/get_role_auth', methods=['GET'])
@wrapper
def get_role_auth():
    """
    :desc
    获取所有角色及其对应的权限
    :return:
    """
    role_list = []
    roles = Role.query.all()
    for role_item in roles:
        admin_auth = []  # 管理员
        user_auth = []  # 用户管理
        ingredient_auth = []  # 食材管理
        article_auth = []  # 文章管理
        for auth_item in role_item.properties:
            auth = {
                'auth_id': auth_item.auth_id,
                'auth_name': auth_item.auth_name,
                'auth_parent': auth_item.auth_parent,
                'auth_path': auth_item.auth_path,
                'auth_desc': auth_item.auth_desc
            }
            if auth_item.auth_parent == '管理员':
                admin_auth.append(auth)
            if auth_item.auth_parent == '用户管理':
                user_auth.append(auth)
            if auth_item.auth_parent == '食材管理':
                ingredient_auth.append(auth)
            if auth_item.auth_parent == '文章管理':
                article_auth.append(auth)
        auth_dict = {
            '管理员': admin_auth,
            '用户管理': user_auth,
            '食材管理': ingredient_auth,
            '文章管理': article_auth
        }
        role = {
            'role_id': role_item.role_id,
            'role_name': role_item.role_name,
            'role_desc': role_item.role_desc,
            'auth_dict': auth_dict
        }
        role_list.append(role)
    response = {
        'data': role_list,
        'meta': {
            'msg': '获取成功',
            'status': 202
        }
    }
    return jsonify(response), response['meta']['status']


@role_view.route('/role_list', methods=['GET'])
@wrapper
def get_role_list():
    """
    :desc
    获取角色列表
    :return:
    """
    role_list = Role.query.all()
    data_list = []
    for item in role_list:
        role = {
            'role_id': item.role_id,
            'role_name': item.role_name
        }
        data_list.append(role)
    response = {
        'data': data_list,
        'meta': {
            'msg': '获取角色成功',
            'status': 202
        }
    }
    return jsonify(response), response['meta']['status']


@role_view.route('/distribute_auth/<int:role_id>/<int:auth_id>', methods=['POST'])
@wrapper
def distribute_auth(role_id, auth_id):
    """
    :desc
    给role_id对应的角色分配auth_id对应的权限
    :param role_id:
    :param auth_id:
    :return:
    """
    role = Role.query.filter(Role.role_id == role_id).first()
    auth = Auth.query.filter(Auth.auth_id == auth_id).first()
    auth.properties.append(role)
    db.session.commit()
    response = {
        'data': {
            'role_id': role_id,
            'auth_id': auth_id
        },
        'meta': {
            'msg': '添加成功',
            'status': 202
        }
    }
    return jsonify(response), response['meta']['status']


@role_view.route('/delete_role_auth/<int:role_id>/<tag>/<content>', methods=['DELETE'])
@wrapper
def delete_role_auth(role_id, tag, content):
    """
    :desc
    删除role_id对应的角色的对应权限
    :param role_id: 角色id
    :param tag:
    当tag==parent时，删除对应整个类别的权限，例如删除有关文章管理的所有权限；
    当tag==children时，删除某个特定的权限，例如删除成员列表这个权限；
    :param content:
    当tag==parent时，content内容与auth_parent对应；
    当tag==children时，content内容与auth_id对应；
    :return:
    """
    role = Role.query.filter(Role.role_id == role_id).first()
    if tag == 'parent':
        delete_list = []
        for item in role.properties:
            if item.auth_parent == content:
                delete_list.append(item)
        for i in range(0, len(delete_list)):
            role.properties.remove(delete_list[i])
        db.session.commit()
        response = {
            'data': {
                'role_id': role_id,
                'auth_parent': content
            },
            'meta': {
                'msg': '取消权限成功',
                'status': 202
            }
        }
    if tag == 'children':
        for item in role.properties:
            if item.auth_id == int(content):
                role.properties.remove(item)
                db.session.commit()
        response = {
            'data': {
                'role_id': role_id,
                'auth_id': int(content)
            },
            'meta': {
                'msg': '取消权限成功',
                'status': 202
            }
        }
    return jsonify(response), response['meta']['status']


class Auth(db.Model):
    __tablename__ = 'auth'
    auth_id = db.Column('auth_id', db.Integer, primary_key=True, autoincrement=True, comment='权限id')
    auth_name = db.Column('auth_name', db.String(10), unique=True, nullable=False, comment='权限名')
    auth_parent = db.Column('auth_parent', db.String(10), unique=False, nullable=True, comment='权限父节点')
    auth_path = db.Column('auth_path', db.String(35), unique=True, nullable=True, comment='权限路径')
    auth_desc = db.Column('auth_desc', db.String(50), nullable=False, comment='权限描述')


auth_view = Blueprint("auth_view", __name__, url_prefix='/auth')


@auth_view.route('/add_auth', methods=['POST'])
def add_auth():
    """
    :param
    {
        'auth_name': '成员列表',
        'auth_parent': '管理员',
        'auth_path': 'admin',
        'auth_desc': '0'  # 权限的等级，0为一级，1为二级
    }
    :return
    """
    # 根据auth_name判断是否有对象存在
    auth_name = Auth.query.filter(Auth.auth_name == request.json['auth_name']).first()
    if auth_name is None:
        # 根据auth_parent判断是否有对象存在
        auth_parent = Auth.query.filter(Auth.auth_parent == request.json['auth_parent']).first()
        if auth_parent is None:
            # 根据auth_path判断是否有对象存在
            auth_path = Auth.query.filter(Auth.auth_path == request.json['auth_path']).first()
            if auth_path is None:
                auth = Auth(auth_name=request.json['auth_name'], auth_parent=request.json['auth_parent'],
                            auth_path=request.json['auth_path'], auth_desc=request.json['auth_desc'])
                db.session.add(auth)
                db.session.commit()
                response = {
                    'data': {
                        'auth_name': request.json['auth_name'],
                        'auth_parent': request.json['auth_parent'],
                        'auth_path': request.json['auth_path'],
                        'auth_desc': request.json['auth_desc']
                    },
                    'meta': {
                        'msg': '权限添加成功',
                        'status': 202
                    }
                }
                return jsonify(response), response['meta']['status']
    response = {
        'data': None,
        'meta': {
            'msg': '该权限已存在',
            'status': 200
        }
    }
    return jsonify(response), response['meta']['status']


@auth_view.route('/auth_list', methods=['GET'])
@wrapper
def get_auth_list():
    """
    :desc
    获取权限列表
    :return:
    """
    auth_list = []
    authority = Auth.query.all()
    for item in authority:
        auth = {
            'auth_id': item.auth_id,
            'auth_name': item.auth_name,
            'auth_parent': item.auth_parent,
            'auth_path': item.auth_path,
            'auth_desc': item.auth_desc
        }
        auth_list.append(auth)
    response = {
        'data': {
            'auth_list': auth_list
        },
        'meta': {
            'msg': '获取成功',
            'status': 202
        }
    }
    return jsonify(response), response['meta']['status']


@auth_view.route('/modify_auth/<int:role_id>', methods=['GET', 'PUT'])
@wrapper
def modify_auth(role_id):
    """
    :desc
    GET请求：
    获取所有权限以及role_id对应角色已拥有的角色
    POST请求：
    {
        'check_list': [2,3,4,5]
    }
    将check_list列表中的auth_id对应的权限分配给role_id对应的角色
    :param role_id:
    :return:
    """
    if request.method == 'GET':
        auth_list = Auth.query.all()
        role = Role.query.filter(Role.role_id == role_id).first()
        properties = []
        for thing in role.properties:
            properties.append(thing.auth_id)
        data = []
        for item in auth_list:
            if item.auth_desc == '0':
                children = []
                for auth in auth_list:
                    if auth.auth_parent == item.auth_name:
                        child = {
                            'auth_id': auth.auth_id,
                            'auth_name': auth.auth_name,
                            'auth_path': auth.auth_path,
                            'auth_parent': auth.auth_parent,
                            'auth_desc': auth.auth_desc
                        }
                        children.append(child)
                parent = {
                    'auth_id': item.auth_id,
                    'auth_name': item.auth_name,
                    'auth_path': item.auth_path,
                    'auth_parent': item.auth_parent,
                    'auth_desc': item.auth_desc,
                    'children': children
                }
                data.append(parent)
        response = {
            'data': {
                'role_id': role_id,
                'data_list': data,
                'properties': properties
            },
            'meta': {
                'msg': '获取成功',
                'status': 202
            }
        }
        return jsonify(response), response['meta']['status']
    if request.method == 'PUT':
        check_list = request.json['check_list']
        role = Role.query.filter(Role.role_id == role_id).first()
        delete_list = []
        # for i in range(0, len(delete_list)):
        #     role.properties.remove(delete_list[i])
        # db.session.commit()
        # 遍历角色的已拥有的所有权限，删除check_list里没有的权限
        for auth in role.properties:
            # 删除列表里没有的权限
            if auth.auth_id not in check_list:
                delete_list.append(auth)
        for i in range(0, len(delete_list)):
            role.properties.remove(delete_list[i])
        db.session.commit()
        add_list = []
        for auth_id in check_list:
            auth = Auth.query.filter(Auth.auth_id == auth_id).first()
            if auth.auth_desc == '1' and auth not in role.properties:
                add_list.append(auth)
        for i in range(0, len(add_list)):
            role.properties.append(add_list[i])
        db.session.commit()
        response = {
            'data': {
                'role_id': role_id,
                'check_list': check_list
            },
            'meta': {
                'msg': '分配权限成功',
                'status': 202
            }
        }
        return jsonify(response), response['meta']['status']


# Admin实体对象
class Admin(db.Model):
    __tablename__ = 'admin'
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True, comment='管理员id')
    username = db.Column('username', db.String(18), unique=True, nullable=False, comment='管理员账号')
    password = db.Column('password', db.String(200), nullable=False, comment='管理员密码')
    email = db.Column('email', db.String(50), unique=True, nullable=False, comment='管理员电子邮箱')
    create_time = db.Column('create_time', db.DateTime, nullable=False, comment='创建时间')
    status = db.Column('status', db.Boolean, default=True, nullable=False, comment='当前用户状态')
    role_id = db.Column(db.Integer, db.ForeignKey('role.role_id'))

    # def __init__(self, username, password, email, create_time, status, role_id):
    #     self.username = username
    #     self.password = password
    #     self.email = email
    #     self.create_time = create_time
    #     self.status = status
    #     self.role_id = role_id

    # 创建admin的方法
    def create_admin(self):
        admin = Admin(username=self.username, password=generate_password_hash(self.password), email=self.email,
                      create_time=datetime.now(), status=True,
                      role_id=self.role_id)
        db.session.add(admin)
        db.session.commit()

    def update_admin(self):
        admin = Admin.query.filter_by(id=self.id).first()
        admin.username = self.username
        admin.password = generate_password_hash(self.password)
        admin.email = self.email
        admin.role_id = self.role_id
        db.session.commit()


admin_view = Blueprint("admin_view", __name__, url_prefix='/admin')


# 注册前验证账号或邮箱是否已被注册
@admin_view.route('/validate/<tag>', methods=['POST'])
def validate(tag):
    """
    :description
    POST请求：验证账号或邮箱是否已被注册
    :param
    tag:为username或email
    {
        'validate': 'a1235life'或'a1235life@gmail.com'
    }
    1.当tag为username时,validate为要验证的账号，此时验证该username是否已被注册
    2.当tag为email时，validate为要验证的邮箱，此时验证该email是否已被注册
    :return:
    1.账号已存在,200
    2.邮箱已被注册,200
    3.账号可供注册,202
    4.邮箱可供注册,202
    """
    # 验证账号
    if tag == 'username':
        admin_username = Admin.query.filter(Admin.username == request.json['validate']).first()
        # 账号存在
        if admin_username is not None:
            response = {
                'data': {
                    'id': admin_username.id,
                    'username': admin_username.username,
                    'email': admin_username.email,
                    'role_id': admin_username.role_id
                },
                'meta': {
                    'msg': '该账号已存在',
                    'status': 200
                }
            }
        # 账号不存在
        else:
            response = {
                'data': None,
                'meta': {
                    'msg': '此账号可供注册',
                    'status': 202
                }
            }
    # 验证邮箱
    if tag == 'email':
        admin_email = Admin.query.filter(Admin.email == request.json['validate']).first()
        # 邮箱已被注册
        if admin_email is not None:
            response = {
                'data': {
                    'id': admin_email.id,
                    'username': admin_email.username,
                    'email': admin_email.email,
                    'role_id': admin_email.role_id
                },
                'meta': {
                    'msg': '此邮箱已被注册',
                    'status': 200
                }
            }
        else:
            response = {
                'data': None,
                'meta': {
                    'msg': '此邮箱可供注册',
                    'status': 202
                }
            }
    return jsonify(response), response['meta']['status']


# 注册接口
@admin_view.route('/register', methods=['POST'])
def register():
    """
    :description
    POST请求：注册一个新admin对象
    :param
    {
        'username': 'a1235life',
        'password': 'lk123456',
        'email': 'a1235life@gmail.com',
        'role_id': ''
    }
    :return
    1.注册成功,201
    """
    admin = dict_to_object(request.json)
    Admin.create_admin(admin)
    response = {
        'data': None,
        'meta': {
            'msg': '注册成功',
            'status': 201
        }
    }
    return jsonify(response), response['meta']['status']


@admin_view.route('/username_login', methods=['POST'])
def username_login():
    """
    :description
    POST请求：通过账号登录管理员
    :param
    {
        'username': 'a1235life',
        'password': 'lk123456'
    }
    :return:
    1.登录成功，202
    2.账号或密码错误，200
    """
    # 判断用户是否存在
    if Admin.query.filter(Admin.username == request.json['username']).count() > 0:
        admin = Admin.query.filter(Admin.username == request.json['username']).first()
        # 判断密码是否正确
        if check_password_hash(admin.password, request.json['password']):
            response = {
                'data': {
                    'id': admin.id,
                    'username': admin.username,
                    'email': admin.email,
                    'role_id': admin.role_id
                },
                'meta': {
                    'msg': '登录成功',
                    'status': 202
                }
            }
            return jsonify(response), response['meta']['status']
    response = {
        'data': None,
        'meta': {
            'msg': '账号或密码错误',
            'status': 200
        }
    }
    return jsonify(response), response['meta']['status']


@admin_view.route('/validate_email', methods=['POST'])
def validate_email():
    """
    :description
    POST请求
    接口功能：向邮箱发送验证码
    适用范围：
    1.注册时用户给定邮箱，向该邮箱发送验证码，以此来完成注册业务
    2.用户使用邮箱登录时给定邮箱， 向该邮箱发送验证码，以此来完成邮箱登录业务
    :param
    {
        'validate': 'a1235life@gmail.com
    }
    :return
    1.验证码已发送到该邮箱中，200
    2.验证码邮件发送失败，403
    """
    verification_code = get_one()
    flag = send_email(request.json['validate'], verification_code['code'])
    if flag == 'success':
        response = {
            'data': {
                'email': request.json['validate'],
                'verification_code': verification_code['code']
            },
            'meta': {
                'msg': '验证码已发送到该邮箱中',
                'status': 200
            }
        }
    else:
        response = {
            'data': None,
            'meta': {
                'msg': '验证码邮件发送失败',
                'status': 403
            }
        }
    return jsonify(response), response['meta']['status']


# session的过期时间与浏览器的生命周期一致
@admin_view.route('/status_manage/<username>', methods=['POST', 'DELETE', 'GET'])
def status_manage(username):
    """
    :description
    管理用户的登录状态，登录状态只有两种情况（登录和注销）
    :return:
    1.用户登录成功,201
    2.用户注销成功,200
    """
    if request.method == 'POST':
        # 将登录的用户的账号加密后存在session里，此时用户的状态为“登录”
        session['username'] = username
        response = {
            'data': {
                'status': 'login'
            },
            'meta': {
                'msg': '用户' + username + '登录成功',
                'status': 201
            }
        }
        return jsonify(response), response['meta']['status']
    if request.method == 'DELETE':
        response = {
            'data': {
                'status': 'logout'
            },
            'meta': {
                'msg': '用户' + str(session.get('username', None)) + '注销成功',
                'status': 200
            }
        }
        if session.get('username', None) is None:
            response['meta']['msg'] = '用户并未登录过'
            return jsonify(response), response['meta']['status']
        else:
            # 将已登录过的用户的session删除，此时用户的状态为“注销“
            session.pop('username')
        return jsonify(response), response['meta']['status']
    if request.method == 'GET':
        # 没登录
        if str(session.get('username', None)) == 'None':
            properties = ['/login', '/email_login', '/register', '/retrieve_password', '/aplus']
            response = {
                'data': {
                    'username': str(session.get('username', None)),
                    'status': 'logout',
                    'properties': properties
                },
                'meta': {
                    'msg': '用户名为' + str(session.get('username', None)),
                    'status': 200
                }
            }
        # 登录了
        else:
            username = str(session.get('username', None))
            admin = Admin.query.filter(Admin.username == username).first()
            role = Role.query.filter(Role.role_id == admin.role_id).first()
            properties = ['/', '/chart', '/login', '/email_login', '/register', '/retrieve_password', '/aplus']
            for item in role.properties:
                auth_path = '/' + item.auth_path
                properties.append(auth_path)
            response = {
                'data': {
                    'username': str(session.get('username', None)),
                    'status': 'login',
                    'properties': properties
                },
                'meta': {
                    'msg': '用户名为' + str(session.get('username', None)),
                    'status': 202
                }
            }
        return jsonify(response), response['meta']['status']


@admin_view.route('/remember_password', methods=['POST', 'DELETE', 'GET'])
def remember_password():
    """
    :param
    {
        'id': 1,
        'username': 'a1235life',
        'password': 'lk123456'
    }
    :return:
    1.账号密码存入cookie，201
    2.cookie删除，200
    """
    if request.method == 'POST':
        data = {
            'data': {
                'id': request.json['id'],
                'username': request.json['username'],
                'password': request.json['password']
            },
            'meta': {
                'msg': '用户的账号及密码已加密并存入cookie，一周后过期',
                'status': 201
            }
        }
        response = make_response(data, 201)
        response.set_cookie('id', str(request.json['id']), path='/',
                            expires=datetime.now() + timedelta(days=7))
        response.set_cookie('username', generate_password_hash(request.json['username']), path='/',
                            expires=datetime.now() + timedelta(days=7))
        response.set_cookie('password', Admin.query.filter(Admin.id == request.json['id']).first().password, path='/',
                            expires=datetime.now() + timedelta(days=7))
        return response
    if request.method == 'DELETE':
        data = {
            'data': None,
            'meta': {
                'msg': '用户的账号及密码的cookie已删除',
                'status': 200
            }
        }
        response = make_response(data, 200)
        response.delete_cookie('id')
        response.delete_cookie('username')
        response.delete_cookie('password')
        return response
    if request.method == 'GET':
        id = request.cookies.get('id', None)
        username = request.cookies.get('username', None)
        password = request.cookies.get('password', None)
        if id and username and password:
            data = {
                'data': {
                    'id': id,
                    'username': username,
                    'password': password
                },
                'meta': {
                    'msg': '获取账号和密码成功',
                    'status': 200
                }
            }
            response = make_response(data, 200)
            return response
        else:
            data = {
                'data': None,
                'meta': {
                    'msg': '账号和密码的cookie不存在',
                    'status': 200
                }
            }
            response = make_response(data, 200)
            return response


@admin_view.route('/modify_password', methods=['PUT'])
def modify_password():
    """
    :param
    {
        'id': 1,
        'username': a1235life,
        'password': 'lk123456'
        'email': a1235life@gmail.com,
        'role_id': null
    }
    :return:
    1.修改成功，202
    """
    Admin.update_admin(dict_to_object(request.json))
    response = {
        'data': {
            'id': request.json['id'],
            'username': request.json['username'],
            'email': request.json['email'],
            'role_id': request.json['role_id']
        },
        'meta': {
            'msg': '修改成功',
            'status': 202
        }
    }
    return jsonify(response), response['meta']['status']


@admin_view.route('/auto_login', methods=['POST'])
def auto_login():
    """
    :description
    POST请求：通过账号登录管理员
    :param
    {
        'id': 1,
        'username': '加密过的用户名，老长一串乱字符',
        'password': '加密过的密码，老长一串乱字符'
    }
    :return:
    1.登录成功，202
    2.账号或密码错误，200
    """
    # 判断用户是否存在
    if Admin.query.filter(Admin.id == request.json['id']).count() > 0:
        admin = Admin.query.filter(Admin.id == request.json['id']).first()
        # 判断密码是否正确
        if check_password_hash(request.json['username'], admin.username) and (
                admin.password == request.json['password']):
            response = {
                'data': {
                    'id': admin.id,
                    'username': admin.username,
                    'email': admin.email,
                    'role_id': admin.role_id
                },
                'meta': {
                    'msg': '登录成功',
                    'status': 202
                }
            }
            return jsonify(response), response['meta']['status']
    response = {
        'data': None,
        'meta': {
            'msg': '账号或密码错误',
            'status': 200
        }
    }
    return jsonify(response), response['meta']['status']


@admin_view.route('/retrieve_admin')
@wrapper
def retrieve_admin():
    # http://localhost:8181/admin/retrieve_admin?query=&page_num=5&page_size=10
    # http://localhost:8181/admin/retrieve_admin?query=gmail&page_num=1&page_size=10
    request_dict = dict(request.args)
    query = request_dict['query']
    page_num = int(request_dict['page_num'])
    page_size = int(request_dict['page_size'])
    if query == '':
        # 不查询东西，将所有数据分页返回
        pagination = Admin.query.paginate(page=page_num, per_page=page_size, error_out=False)
        admin_list = []
        for item in pagination.items:
            admin = {
                'id': item.id,
                'username': item.username,
                'email': item.email,
                'create_time': item.create_time,
                'status': item.status,
                'role_id': item.role_id
            }
            admin_list.append(admin)
        response = {
            'data': {
                'per_page': pagination.per_page,  # 每页多少条数据
                'current_page': pagination.page,  # 当前页码
                'total_pages': pagination.pages,  # 总共多少页
                'total': pagination.total,  # 总记录数
                'admin_list': admin_list
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
            admin_list = []
            # id_list = Admin.query.filter(Admin.id.like('%' + query + '%')).all()
            username_list = Admin.query.filter(Admin.username.like('%' + query + '%')).all()
            email_list = Admin.query.filter(Admin.email.like('%' + query + '%')).all()
            # role_id_list = Admin.query.filter(Admin.role_id.like('%' + query + '%')).all()
            # admin_list += id_list
            admin_list += username_list
            admin_list += email_list
            # admin_list += role_id_list
            admin_set = set(admin_list)
            admin_list.clear()
            for item in admin_set:
                admin = {
                    'id': item.id,
                    'username': item.username,
                    'email': item.email,
                    'create_time': item.create_time,
                    'status': item.status,
                    'role_id': item.role_id
                }
                admin_list.append(admin)
            total_pages, left = divmod(len(admin_list), page_size)
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
                        'total': len(admin_list),
                        'admin_list': admin_list
                    },
                    'meta': {
                        'msg': '获取成功',
                        'status': 200
                    }
                }
                return jsonify(response), response['meta']['status']


@admin_view.route('/delete_admin/<int:id>', methods=['DELETE'])
@wrapper
def delete_admin(id):
    admin = Admin.query.filter(Admin.id == id).first()
    response = {
        'data': None,
        'meta': {
            'msg': '删除成功',
            'status': 202
        }
    }
    if admin is not None:
        db.session.delete(admin)
        db.session.commit()
    else:
        response['meta']['msg'] = '该成员不存在'
        response['meta']['status'] = 200
    return jsonify(response), response['meta']['status']


@admin_view.route('/edit_admin', methods=['PUT'])
@wrapper
def edit_admin():
    admin = Admin.query.filter(Admin.id == request.json['id']).first()
    if admin is not None:
        admin.email = request.json['email']
        admin.status = request.json['status']
        db.session.commit()
        response = {
            'data': {
                'id': admin.id,
                'username': admin.username,
                'email': admin.email,
                'status': admin.status,
                'create_time': admin.create_time,
                'role_id': admin.role_id
            },
            'meta': {
                'msg': '修改成功',
                'status': 202
            }
        }
        return response, response['meta']['status']
    else:
        response = {
            'data': None,
            'meta': {
                'msg': '该成员不存在',
                'status': 200
            }
        }
        return response, response['meta']['status']


@admin_view.route('/change_status/<int:id>', methods=['PUT'])
@wrapper
def change_status(id):
    admin = Admin.query.filter(Admin.id == id).first()
    if admin is not None:
        if admin.status is True:
            admin.status = False
            db.session.commit()
            response = {
                'data': {
                    'id': admin.id,
                    'before_change': True,
                    'changed': False
                },
                'meta': {
                    'msg': 'id为' + str(id) + '的成员的状态已从true改为false',
                    'status': 202
                }
            }
        else:
            admin.status = True
            db.session.commit()
            response = {
                'data': {
                    'id': admin.id,
                    'before_change': False,
                    'changed': True
                },
                'meta': {
                    'msg': 'id为' + str(id) + '的成员的状态已从false改为true',
                    'status': 202
                }
            }
    else:
        response = {
            'data': None,
            'meta': {
                'msg': 'id为' + str(id) + '的成员不存在',
                'status': 200
            }
        }
    return jsonify(response), response['meta']['status']


@admin_view.route('/set_role/<int:id>/<int:role_id>', methods=['PUT'])
@wrapper
def set_role(id, role_id):
    admin = Admin.query.filter(Admin.id == id).first()
    if admin is not None:
        admin.role_id = role_id
        db.session.commit()
        response = {
            'data': {
                'id': admin.id,
                'username': admin.username,
                'role_id': admin.role_id
            },
            'meta': {
                'msg': '角色修改成功',
                'status': 202
            }
        }
    else:
        response = {
            'data': None,
            'meta': {
                'msg': 'id为' + str(id) + '的成员不存在',
                'status': 200
            }
        }
    return jsonify(response), response['meta']['status']
