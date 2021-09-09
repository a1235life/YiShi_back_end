# 导入Swagger包
from flasgger import Swagger
# 导入跨域配置
from flask_cors import CORS
# 实体导入
from entity import Admin, User, Food, Article, Rate, Verification, Likes
# 导入Flask对象的实例对象app
from config.app_config import app

# 注册User实体的蓝图，以此注入User的视图函数
app.register_blueprint(User.user_view)
# 注册Admin实体的蓝图，以此注入Admin的视图函数
app.register_blueprint(Admin.admin_view)
# 注册Food实体的蓝图，以此注入Food的视图函数
app.register_blueprint(Food.food_view)
# 注册Article实体的蓝图，以此注入Article的视图函数
app.register_blueprint(Article.article_view)
# 注册Rate实体的蓝图，以此注入Rate的视图函数
app.register_blueprint(Rate.rate_view)
# 注册Verification实体的蓝图，以此注入Verification的视图函数
app.register_blueprint(Verification.verification_view)
# 注册Likes实体的蓝图，以此注入Likes的视图函数
app.register_blueprint(Likes.likes_view)
app.register_blueprint(Admin.role_view)
app.register_blueprint(Admin.auth_view)
# 实例化swagger
swagger = Swagger(app)

CORS(app, resources=r'/*', supports_credentials=True)


@app.route('/')
def index():
    # return redirect('/login')
    # print(url_for('user',id='123'))
    # print(url_for('food',id='46'))
    return '益食项目后端根目录'


# 开发时在8181端口使用debug模式
if __name__ == '__main__':
    app.run(debug=True, port=8181)

# 部署时
# if __name__ == '__main__':
#     app.run(debug=False)
