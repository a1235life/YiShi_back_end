# 从app_config文件中导入实例化的SQLAlchemy对象db
from config.app_config import db

from flask import Blueprint, request, jsonify


class Likes(db.Model):
    __tablename__ = 'likes'
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True, comment='喜好id')
    gender = db.Column('gender', db.String(10), comment='性别')
    province = db.Column('province', db.String(10), comment='省份')
    interests = db.Column('interests', db.String(100), comment='用户兴趣')
    fruits = db.Column('fruits', db.String(100), comment='用户喜欢的水果')
    sort = db.Column('sort', db.String(30), comment='文章类别')
    heat = db.Column('heat', db.Integer, comment='热度')
    time = db.Column('time', db.Integer, comment='阅读文章时间')
    collect = db.Column('collect', db.Integer, comment='是否收藏')
    thumbs_up = db.Column('thumbs_up', db.Integer, comment='是否点赞')


likes_view = Blueprint("likes_view", __name__, url_prefix='/likes')


@likes_view.route('/record_likes', methods=['POST'])
def record_likes():
    likes = Likes(gender=request.json['gender'], province=request.json['province'], interests=request.json['interests'],
                  fruits=request.json['fruits'], sort=request.json['sort'],
                  heat=request.json['heat'], time=request.json['time'],
                  collect=request.json['collect'], thumbs_up=request.json['thumbs_up'])
    db.session.add(likes)
    db.session.commit()
    response = {
        'data': None,
        'meta': {
            'msg': '记录成功',
            'status': 202
        }
    }
    return jsonify(response), response['meta']['status']
