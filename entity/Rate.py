from config.app_config import db

from flask import Blueprint


class Rate(db.Model):
    __tablename__ = 't_rate'
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    recognition_times = db.Column('recognition_times', db.Integer, autoincrement=True)
    success_times = db.Column('success_times', db.Integer, autoincrement=True)
    rate = db.Column('rate', db.Float)
    model_name = db.Column('model_name', db.String(50), nullable=True, comment='模型名')


rate_view = Blueprint("rate_view", __name__, url_prefix='/rate')


@rate_view.route('/statistics/<int:id>', methods=['PUT'])
def rate_statistics(id):
    rate = Rate.query.filter(Rate.id == id).first()
    rate.success_times = rate.success_times + 1
    rate.rate = rate.success_times / rate.recognition_times
    if rate.rate > 1:
        rate.rate = 1
    db.session.commit()
    return 'statistics!'


def recognition_times_plus(id):
    rate = Rate.query.filter(Rate.id == id).first()
    rate.recognition_times = rate.recognition_times + 1
    rate.rate = rate.success_times / rate.recognition_times
    db.session.commit()
