from flask import Flask
from flask_babel import Babel
from flask_sqlalchemy import SQLAlchemy

from flask_login import LoginManager
from flask_pagedown import PageDown
from flask_moment import Moment

app = Flask(__name__)
app.config.from_object('config')
babel = Babel(app)
db = SQLAlchemy(app)

lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'

pagedown = PageDown()
pagedown.init_app(app)

moment = Moment()
moment.init_app(app)

if not app.debug:
    import logging
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler('tmp/microblog.log', 'a',
                                       1 * 1024 * 1024, 10)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
app.logger.info('microblog startup')

from app import views, models