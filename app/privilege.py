from functools import wraps
from flask_login import current_user
from flask import abort


def admin(f):
    @wraps(f)
    def decorator_function(*args, **kwargs):
        if current_user.role_id == 1:
            return f(*args, **kwargs)
        else:
            return abort(403)
    return decorator_function


def employee(f):
    @wraps(f)
    def decorator_function(*args, **kwargs):
        if current_user.role_id == 2 or current_user.role_id == 1:
            return f(*args, **kwargs)
        else:
            return abort(403)
    return decorator_function

#
# def user(f):
#     @wraps(f)
#     def decorator_function(*args, **kwargs):
#         if current_user.role_id == 3 or current_user.role_id == 2 or current_user.role_id == 1:
#             return f(*args, **kwargs)
#     return decorator_function
