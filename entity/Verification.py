# 数据库实例化对象db
from config.app_config import db
# 从flask导入蓝图，http请求工具，json工具
from flask import Blueprint, request, jsonify
# 导入验证码生成工具
from utils.verification_code_generator import generate_captcha_image
import random

# smtplib 用于邮件的发信动作
import smtplib

# 用于构建邮件内容
from email.mime.text import MIMEText
from email.utils import formataddr


class Verification(db.Model):
    __tablename__ = 'verification'
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    code = db.Column('code', db.String(10))
    location = db.Column('location', db.String(300))

    def create_one(self):
        db.session.add(self)
        db.session.commit()


# 实例化视图
verification_view = Blueprint("verification_view", __name__, url_prefix='/verification')


# 获取一条验证码
def get_one():
    verifications = Verification.query.all()
    verification = verifications[random.randint(0, len(verifications) - 1)]
    verification_dict = {
        'id': verification.id,
        'code': verification.code,
        'location': verification.location
    }
    return verification_dict


# 获取一条验证码接口
@verification_view.route('/get_one', methods=['GET'])
def get_one_verification_code():
    # 将所有验证码装入列表
    verifications = Verification.query.all()
    # 若列表大小为0，返回验证码未生成
    if len(verifications) == 0:
        return '验证码暂未生成'
    # 若列表中存在验证码，通过random函数随机获取列表中的验证码
    verification = verifications[random.randint(0, len(verifications) - 1)]
    # 将验证码封装成字典
    verification_dict = {
        'id': verification.id,
        'code': verification.code,
        'location': verification.location
    }
    return jsonify(verification_dict)


# 生成验证码接口，发送的json实例如下：
# {
#     'number':10,#生成的验证码的数量，类型为int
#     'digit':1#验证码的位数，类型为int
# }
@verification_view.route('/generate', methods=['POST'])
def generate_one_verification_code():
    # POST请求
    # 获取http请求中的json数据中的number，即生成的验证码数量
    for i in range(request.json['number']):
        # digit即生成的验证码的位数
        # code为验证码的具体内容
        code = generate_captcha_image(request.json['digit'])
        # location为验证码图片的url
        location = 'http://47.98.201.222:8080/ingredients/verification/' + code + '.png'
        # 封装成验证码实体
        verification = Verification(code=code, location=location)
        # 将验证码保存到数据库中
        Verification.create_one(verification)
    return '生成' + str(request.json['number']) + '条验证码，每条验证码的位数为' + str(request.json['digit']) + '位'


# epqz qzcs yvtd bjfb
# SMTP（Simple Mail Transfer Protocol）简单邮件传输协议
def send_email(my_user, code):  # 收件人邮箱账号(可以发送给自己)
    my_sender = '422768891@qq.com'  # 发件人邮箱账号
    my_pass = 'epqzqzcsyvtdbjfb'  # 发件人邮箱授权码
    ret = True
    try:
        text = '益食安全验证，您的验证码为' + code + '，不要告诉别人哦！！'
        msg = MIMEText(text, 'plain', 'utf-8')
        msg['From'] = formataddr(("益食", my_sender))  # 括号里的对应发件人邮箱昵称、发件人邮箱账号
        msg['To'] = formataddr(("亲爱的用户", my_user))  # 括号里的对应收件人邮箱昵称、收件人邮箱账号
        msg['Subject'] = "益食安全验证"  # 邮件的主题，也可以说是标题

        server = smtplib.SMTP_SSL("smtp.qq.com", 465)  # QQ邮箱SMTP服务器地址：smtp.qq.com，ssl 端口：465。
        server.login(my_sender, my_pass)  # 括号中对应的是发件人邮箱账号、邮箱密码
        server.sendmail(my_sender, my_user, msg.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
        server.quit()  # 关闭连接
    except smtplib.SMTPException:  # 如果 try 中的语句没有执行，则会执行下面的 ret=False
        ret = False
    if ret:
        print("邮件发送成功")
        return 'success'
    else:
        print("邮件发送失败")
        return 'failure'


# epqz qzcs yvtd bjfb
# SMTP（Simple Mail Transfer Protocol）简单邮件传输协议
@verification_view.route('/send_email', methods=['POST'])
def admin_send_email():  # 收件人邮箱账号(可以发送给自己)
    receiver = request.json['receiver']
    email_content = request.json['email_content']
    my_sender = '422768891@qq.com'  # 发件人邮箱账号
    my_pass = 'epqzqzcsyvtdbjfb'  # 发件人邮箱授权码
    ret = True
    try:
        text = email_content
        msg = MIMEText(text, 'plain', 'utf-8')
        msg['From'] = formataddr(("益食", my_sender))  # 括号里的对应发件人邮箱昵称、发件人邮箱账号
        msg['To'] = formataddr(("亲爱的用户", receiver))  # 括号里的对应收件人邮箱昵称、收件人邮箱账号
        msg['Subject'] = "益食"  # 邮件的主题，也可以说是标题
        server = smtplib.SMTP_SSL("smtp.qq.com", 465)  # QQ邮箱SMTP服务器地址：smtp.qq.com，ssl 端口：465。
        server.login(my_sender, my_pass)  # 括号中对应的是发件人邮箱账号、邮箱密码
        server.sendmail(my_sender, receiver, msg.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
        server.quit()  # 关闭连接
    except smtplib.SMTPException:  # 如果 try 中的语句没有执行，则会执行下面的 ret=False
        ret = False
    if ret:
        response = {
            'data': {
                'sender': '422768891@qq.com',
                'receiver': receiver,
                'email_content': email_content
            },
            'meta': {
                'msg': '邮件发送成功',
                'status': 202
            }
        }
    else:
        response = {
            'data': {
                'sender': '422768891@qq.com',
                'receiver': receiver,
                'email_content': email_content
            },
            'meta': {
                'msg': '邮件发送失败',
                'status': 200
            }
        }
    return jsonify(response), response['meta']['status']