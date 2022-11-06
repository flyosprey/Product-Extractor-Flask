from functools import wraps
from flask import session, redirect
from flask_api import status


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('is_logged_in') is False:
            return redirect('/login', code=status.HTTP_302_FOUND)
        return f(*args, **kwargs)
    return decorated_function


def logout_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('is_logged_in') is True:
            return redirect('/incense', code=status.HTTP_302_FOUND)
        return f(*args, **kwargs)
    return decorated_function
