from flask import Blueprint

message = Blueprint('message', __name__)

from . import views