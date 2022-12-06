from flask import request, render_template, make_response
from flask_api import status
from flask_restful import Resource
from flask import redirect, url_for, session
from flask_app.models import Users
from flask_app.decorators import logout_required


class SignUpPage(Resource):
    DEFAULT_HEADERS = {'Content-Type': 'text/html'}

    @logout_required
    def get(self):
        rendered_result = render_template("signup.html", result={})
        return make_response(rendered_result, status.HTTP_200_OK, self.DEFAULT_HEADERS)

    @logout_required
    def post(self):
        log_in_args = request.form
        result = Users().create_user(log_in_args)
        if result.get("error"):
            rendered_result = render_template("signup.html", result=result)
            return make_response(rendered_result, status.HTTP_403_FORBIDDEN, self.DEFAULT_HEADERS)
        else:
            session["is_logged_in"] = True
            session["user_id"] = result["user_id"]
            return redirect(url_for("incense"), code=status.HTTP_302_FOUND)