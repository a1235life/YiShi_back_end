# 导入数据库加实例化对象db
from config.app_config import db
# 导入flask的蓝图和http请求的request
from flask import Blueprint, request, jsonify
# 导入随机数库
import random
# 导入word文档转html文件的工具包
from utils.docx_to_html import docx_transfer_html


# 健康选文Article实体对象
class Article(db.Model):
    __tablename__ = 't_article'
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    location = db.Column('location', db.Unicode)
    weight = db.Column('weight', db.Integer, default=0)
    article_name = db.Column('article_name', db.String(50))
    cover_pic = db.Column('cover_pic', db.String(300))
    mark = db.Column('mark', db.Integer, default=1, comment='评分')
    tag = db.Column('tag', db.String(150), default=None, comment='文章标签')

    def add_article(self):
        db.session.add(self)
        db.session.commit()

    def retrieve_article(self):
        return


article_view = Blueprint("article_view", __name__, url_prefix='/article')


# 上传docx的word文档，转html文件，存入tomcat服务器
@article_view.route('/file_upload', methods=['POST'])
def file_upload():
    file = request.files['file']
    print('上传的文件名：' + file.filename)
    # 1.过滤：仅处理文件扩展名为docx的文件，不允许上传html文件，防止xss攻击
    if file.filename.endswith('.docx'):
        # 2.存储word文档

        # 第一步，对文件名对进行安全过滤或直接重命名文件
        # 安全过滤方法如下：
        # 使用secure_filename过滤文件名，防止文件名内携带路径
        # filename = secure_filename(file.filename)
        # print('安全过滤过后文件名为：' + filename)
        # 重命名文件方法如下：
        filename = 'article_' + str(random.randint(0, 1000)) + '_' + str(random.randint(0, 1000))

        # 第二步，给定存储路径
        # 开发时所用的路径
        upload_location = 'D:/Java/apache-tomcat-8.5.51/webapps/ROOT/ingredients/'
        # 开发时也可用项目根目录下的static文件夹测试是否存储成功
        # upload_location = os.path.abspath('..')+'/flask_demo/static/'+str(filename)
        # 部署时使用tomcat服务器资源路径
        # upload_location = '/usr/local/apache-tomcat-8.5.58/webapps/ROOT/ingredients/article/'

        # 第三步，存储word文件至存储路径,并将filename的值赋给文件名
        file.save(upload_location + filename + '.docx')

        # 3.word文档转为html文件
        docx_transfer_html(upload_location, filename)

        # 4.将文件信息存入数据库
        article = Article(location='http://47.98.201.222:8080/ingredients/article/' + filename + '.html',
                          article_name=file.filename[:-5])
        Article.add_article(article)
        return '上传成功'
    else:
        return '请上传扩展名为.docx的word文档'


@article_view.route('/getArticle', methods=['GET'])
def get_article():
    articles = Article.query.all()
    if len(articles) > 0:
        article_list = []
        for i in range(0, len(articles)):
            tag_list = articles[i].tag.split('@#$')
            one_article = {
                'id': articles[i].id,
                'location': articles[i].location,
                'weight': articles[i].weight,
                'article_name': articles[i].article_name,
                'cover_pic': articles[i].cover_pic,
                'mark': articles[i].mark,
                'tag': tag_list
            }
            article_list.append(one_article)
        result_dict = {
            'result': article_list,
            'msg': 'The query succeeds!'
        }
    else:
        result_dict = {
            'msg': 'The query fails!'
        }
    return jsonify(result_dict)


def find_article_by_id(article_id):
    article = Article.query.filter(Article.id == article_id).first()
    if article is None:
        return '该文章不存在'
    return article
