from flask import Flask
from flask_babel import Babel
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('config')
babel = Babel(app)
db = SQLAlchemy(app)

from app import views, models