from functools import wraps
from flask import session, redirect


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('is_logged_in') is None:
            return redirect('/login', code=302)
        return f(*args, **kwargs)
    return decorated_function


def logout_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('is_logged_in') is not None:
            return redirect('/incense', code=302)
        return f(*args, **kwargs)
    return decorated_function
