# A+实验室阿里云服务器数据库配置
DIALECT = 'mysql'
DRIVER = 'pymysql'
USERNAME = 'root'
PASSWORD = 'aplus'
HOST = '47.98.201.222'
PORT = '3306'
DATABASE = 'ingredient'
SQLALCHEMY_DATABASE_URI = "{}+{}://{}:{}@{}:{}/{}?charset=utf8".format(DIALECT, DRIVER, USERNAME, PASSWORD, HOST, PORT,
                                                                       DATABASE)
SQLALCHEMY_TRACK_MODIFICATIONS = True
# 输出SQLAlchemy查询的输出语句配置
# SQLALCHEMY_ECHO= True

# A+实验室校内服务器
# DIALECT='mysql'
# DRIVER='pymysql'
# USERNAME='root'
# PASSWORD='root'
# HOST='222.22.91.94'
# PORT='3306'
# DATABASE='ingredient'
# SQLALCHEMY_DATABASE_URI = "{}+{}://{}:{}@{}:{}/{}?charset=utf8".format(DIALECT,DRIVER,USERNAME,PASSWORD,HOST,PORT,DATABASE)
# SQLALCHEMY_TRACK_MODIFICATIONS = True
