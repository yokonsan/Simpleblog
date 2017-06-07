from flask import Flask
from flask_babel import Babel

app = Flask(__name__)
babel = Babel(app)
app.config.from_object('config')

from app import views