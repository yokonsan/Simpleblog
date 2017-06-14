from functools import wraps
from flask import abort
from flask_login import current_user
from .models import Permission

"""
自己定义两个装饰器，使用Python内置的functools库。
如果用户不具有指定permission权限，返回403错误码，禁止访问
"""

def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.operation(permission):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    return permission_required(Permission.ADMINISTER)(f)