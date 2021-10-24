# Imports
from functools import wraps
from flask_login import current_user
from flask import abort


# Admin privileges
def admin(f):
    @wraps(f)
    def decorator_function(*args, **kwargs):
        if current_user.role_id == 1:
            return f(*args, **kwargs)
        else:
            return abort(403)
    return decorator_function


# Employee privileges
def employee(f):
    @wraps(f)
    def decorator_function(*args, **kwargs):
        if current_user.role_id == 2 or current_user.role_id == 1:
            return f(*args, **kwargs)
        else:
            return abort(403)
    return decorator_function
