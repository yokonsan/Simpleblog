from flask import Flask
from flask_babel import Babel
from flask_sqlalchemy import SQLAlchemy

from flask_login import LoginManager
from flask_pagedown import PageDown
from flask_moment import Moment
from flask_whooshee import Whooshee
from config import config

babel = Babel()
db = SQLAlchemy()

lm = LoginManager()
lm.login_view = 'auth.login'

pagedown = PageDown()
moment = Moment()
whooshee = Whooshee()

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    # config[config_name].init_app(app)
    moment.init_app(app)
    db.init_app(app)
    lm.init_app(app)
    pagedown.init_app(app)
    whooshee.init_app(app)

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

    from .user import user as user_blueprint
    from .auth import auth as auth_blueprint
    from .admin import admin as admin_blueprint
    from .message import message as message_blueprint
    from .api_1_0 import api as api_1_0_blueprint

    app.register_blueprint(user_blueprint)
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    app.register_blueprint(admin_blueprint, url_prefix='/admin')
    app.register_blueprint(message_blueprint, url_prefix='/message')
    app.register_blueprint(api_1_0_blueprint, url_prefix='/api/v1.0')

    return app
