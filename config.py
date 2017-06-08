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

