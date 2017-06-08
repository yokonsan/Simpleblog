from app import db, lm
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


"""
generate_password_hash(password, method=pbkdf2:sha1, salt_length=8):这个函数将原始密码作为输入，
以字符串形式输出密码的散列值，输出的值可保存在用户数据库中，
method和salt_length的默认值就能满足大多数需求。

check_password_hash(hash, password):这个函数的参数是从数据库中取回的密码散列值和用户输入的密码。
返回值为True表明密码正确。

flask_login的UserMixin类，实现了用户方法：
            is_authenticated：如果用户已经登录，必须返回True，否则返回False
            is_active：如果允许用户登录，必须返回True，否则返回False。如果要禁用账户，可以返回False
            is_anonymous：对普通用户必须返回False
            fet_id()：必须返回用户的唯一标识符，使用Unicode编码字符串
"""


class User(UserMixin,db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    # posts = db.relationship('Post', backref='author', lazy='dynamic')

    # python内置装饰器，把一个方法变为属性调用
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User %r>' % (self.nickname)

@lm.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)

    users = db.relationship('User', backref = 'role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % (self.name)



# class Post(db.Model):
#     id = db.Column(db.Integer, primary_key = True)
#     body = db.Column(db.String(140))
#     timestamp = db.Column(db.DateTime)
#
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
#
#     def __repr__(self):
#         return '<Post %r>' % (self.body)

