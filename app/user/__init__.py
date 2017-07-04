from flask import Blueprint

user = Blueprint('user', __name__)

from . import views, errors
from ..models import Permission

@user.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)