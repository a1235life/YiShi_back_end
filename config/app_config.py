from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import db_config

app = Flask(__name__)
app.config.from_object(db_config)
db = SQLAlchemy(app)
# 用户会话状态要用到的密钥
app.secret_key = 'anything_you_want'
