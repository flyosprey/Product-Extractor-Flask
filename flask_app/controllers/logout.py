from flask_api import status
from flask_restful import Resource
from flask import redirect, url_for, session
from flask_app.decorators import login_required


class LogoutPage(Resource):
    DEFAULT_HEADERS = {'Content-Type': 'text/html'}

    @login_required
    def get(self):
        session.clear()
        return redirect(url_for("login"), code=status.HTTP_302_FOUND)