import datetime
from app import db, lm, whooshee
from flask_login import UserMixin, AnonymousUserMixin
from flask import current_app
from hashlib import md5
from werkzeug.security import generate_password_hash, check_password_hash
from markdown import markdown
import bleach


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
            
实现了关注和被关注的多对多数据模型，followed和followers关系都定义为单独的一对多关系。
必须使用可选参数foreign_keys指定的外键，用来消除外键简的歧义。
db.backref()参数并非指定这两个关系之间的引用关系，而是回引Follow模型。回引的lazy参数为joined。
cascade参数的值是一组由逗号分隔的层叠选项，all表示除了dalete-orphan之外的所有层叠选项。
意思是启用所有默认层叠选项，而且还要删除孤记录。
is_following()方法和is_followed_by()方法分别在左右两边的一对多关系中搜索指定用户，如果找到就返回True

获取关注用户的文章：
    db.session.query(Post)指明这个查询要返回Post对象
    select_from(Follow)的意思是这个查询从Follow模型开始
    filter_by(follower_id=self.id)使用关注用户过滤follows表
    join(Post, Follow.followed_id==Post.author_id)联结filter_by()得到的结果和Post对象

角色模型的permissions字段的值是一个整数，表示位标志。各操作都对应一个位位置，能执行某项操作的角色，其位会被设为1
程序权限：
    关注用户：0x01  
    发表评论：0x02
    发表文章或提问：0x04
    管理他人评论：0x08
    管理员：0x80
用户角色：
    游客：0x00 未登录的用户，只有阅读权限
    用户：0x07 具有发布文章，提问，评论和关注用户的权限，默认角色
    小管家：0x0f 审查不当评论的权限
    管理员：0xff 有所有权限，包括修改用户角色权限
创建数据库后，需要创建用户角色,先更新数据库，然后：
使用python manage.py shell
>>> Role.insert_roles()
>>> Role.query.all()

Comment模型和Post模型的属性一样，但是多了个disabled字段。这是个布尔值字段，作者可以通过这个字段查禁不当评论。
Post模型也添加disabled字段。

会话模型中，lazy='joined'指明加载记录，使用联结，primaryjoin明确指定两个模型之间使用的联结条件。
为了消除外键之间的歧义，定义关系时必须使用可选参数 foreign_keys 指定的外键。
cascade 参数的值是一组有逗号分隔的层叠选项，all 表示除了 delete-orphan 之外的所有层叠选项。
all,delete-orphan 的意思是启用所有默认层叠选项，而且还要删除孤儿记录。
"""

# 关注关联表
class Follow(db.Model):
    __tablename__ = 'follows'
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    unread = db.Column(db.Boolean, default=True)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    # messages = db.relationship('Message', backref='follow', uselist=False)

class User(UserMixin,db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    # 关联
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    # post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    likes = db.relationship('Like', backref='user', lazy='dynamic')
    comments = db.relationship('Comment', backref='author', lazy='dynamic')
    # reply_comments = db.relationship('Reply', backref='author', lazy='dynamic')
    # 个人资料
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime)
    # 关注，被关注
    followed = db.relationship('Follow',
                                foreign_keys = [Follow.follower_id],
                                backref = db.backref('follower', lazy='joined'),
                                lazy = 'dynamic',
                                cascade = 'all, delete-orphan')
    followers = db.relationship('Follow',
                                foreign_keys=[Follow.followed_id],
                                backref=db.backref('followed', lazy='joined'),
                                lazy='dynamic',
                                cascade='all, delete-orphan')

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['ADMINMAIL']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()

    # 检查用户是否有指定权限
    def operation(self, permissions):
        return self.role is not None and \
               (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.operation(Permission.ADMINISTER)

    # 关注
    def follow(self, user):
        if not self.is_following(user):
            follower = Follow(follower=self, followed=user)
            db.session.add(follower)
    # 取消关注
    def unfollow(self, user):
        follower =self.followed.filter_by(followed_id=user.id).first()
        if follower:
            db.session.delete(follower)
    # 做了一个followed关系查询，这个查询返回所有当前用户作为关注者的(follower, followed)对
    def is_following(self, user):
        return self.followed.filter_by(followed_id=user.id).first() is not None
    def is_followed_by(self, user):
        return self.followers.filter_by(follower_id=user.id).first() is not None

    # 获取关注者文章
    @staticmethod
    def followed_posts(self):
        return Post.query.join(Follow, Follow.followed_id==Post.author_id.filter(
            Follow.follower_id==self.id))

    # python内置装饰器，把一个方法变为属性调用
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    # Gravatar提供用户头像
    def gravatar(self, size):
        return 'http://www.gravatar.com/avatar/' + md5(self.email.encode('utf-8')).hexdigest() + '?d=mm&s=' + str(size)

    def __repr__(self):
        return '<User %r>' % (self.nickname)

@lm.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)

    users = db.relationship('User', backref = 'role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.FOLLOW |
                     Permission.COMMENT |
                     Permission.WRITE_ARTICLES, True),
            'Moderator': (Permission.FOLLOW |
                          Permission.COMMENT |
                          Permission.WRITE_ARTICLES |
                          Permission.MODERATE_COMMENTS, False),
            'Administrator': (0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role %r>' % (self.name)

class Permission:
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINISTER = 0x80

@whooshee.register_model('title','body')
class Post(db.Model):
    __tablename__ = 'posts'
    # __searchable__ = ['body']
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(64))
    body = db.Column(db.Text)
    disabled = db.Column(db.Boolean)
    view_num = db.Column(db.Integer, default=0)
    body_html = db.Column(db.Text)
    draft = db.Column(db.Boolean, default=False)
    # like_num = db.Column(db.Integer, default=0)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.datetime.utcnow)

    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    like_num = db.relationship('Like', backref='post', lazy='dynamic')
    comments = db.relationship('Comment', backref='post', lazy='dynamic')
    # reply_comments = db.relationship('Reply', backref='post', lazy='dynamic')

    @staticmethod
    def preview_body(target, value, oldvalue, initiator):
        allowed_tags = [
            'a', 'abbr', 'acronym', 'b', 'img', 'blockquote', 'code',
            'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul', 'h1', 'h2',
            'h3', 'p'
        ]
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True)
        )

    def __repr__(self):
        return '<Post %r>' % (self.body)
db.event.listen(Post.body, 'set', Post.preview_body)

# 检验用户权限对应的类
class AnonymousUser(AnonymousUserMixin):
    def operation(self, permissions):
        return False

    def is_administrator(self):
        return False

lm.anonymous_user = AnonymousUser

# 点赞
class Like(db.Model):
    __tablename__ = 'likes'
    id = db.Column(db.Integer, primary_key=True)
    unread = db.Column(db.Boolean, default=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.datetime.utcnow())

    liker_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))

class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.datetime.utcnow())
    disabled = db.Column(db.Boolean)
    comment_type = db.Column(db.String(64), default='comment')
    reply_to = db.Column(db.String(128), default='notReply')
    unread = db.Column(db.Boolean)

    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = [
            'a', 'abbr', 'acronym', 'b', 'code', 'em', 'img', 'i', 'strong'
        ]
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True
        ))
db.event.listen(Comment.body, 'set', Comment.on_changed_body)

# 会话
class Conversation(db.Model):
    __tablename__ = 'conversations'
    id = db.Column(db.Integer, primary_key=True)
    from_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    to_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    letter = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.datetime.utcnow())
    unread = db.Column(db.Boolean, default=True)

    to_user = db.relationship('User', lazy='joined', foreign_keys=[to_user_id])
    from_user = db.relationship('User', lazy='joined', foreign_keys=[from_user_id])

# 管理
class Admin(db.Model):
    __tablename__ = 'admin'
    id = db.Column(db.Integer, primary_key=True)
    notice = db.Column(db.String(25))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.datetime.utcnow())

    def __repr__(self):
        return '<Admin %r>' % (self.notice)
