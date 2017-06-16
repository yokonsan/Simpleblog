import os
basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
    'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')
SQLALCHEMY_COMMIT_ON_TEARDOWN = True
SQLALCHEMY_TRACK_MODIFICATIONS  = False

DEBUG = True

CSRF_ENABLED = True
SECRET_KEY = 'you-guess'

BABEL_DEFAULT_LOCALE = 'zh_Hans_CN'

# 邮件支持
MAIL_SERVER = 'smtp.163.com'
MAIL_PORT = 25
MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
# 管理员邮箱
ADMINS = os.environ.get('ADMINS_MAIL')

# 分页
POSTS_PER_PAGE = 3