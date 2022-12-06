from flask import request, render_template, make_response
from flask_api import status
from flask_restful import Resource
from flask_app.settings import APP, API
from flask_app.scrapy_side import ScrapySide
from flask_app.database_dispatcher import DatabaseDispatcher
from flask_app.models import Users
from flask import redirect, url_for, session
from decorators import logout_required, login_required


@APP.errorhandler(status.HTTP_404_NOT_FOUND)
def resource_not_found(request):
    return redirect(url_for("incense"), code=status.HTTP_302_FOUND)


class MainPage(Resource):
    DEFAULT_HEADERS = {'Content-Type': 'text/html'}

    @login_required
    def get(self):
        rendered_result = render_template("home_page.html")
        return make_response(rendered_result, status.HTTP_200_OK, self.DEFAULT_HEADERS)

    @login_required
    def post(self):
        user_id = session["user_id"]
        extract_args = request.form if "url" in request.form else None
        show_args = request.form if "limit" in request.form else None
        if extract_args:
            table_name = "Table of extracted data"
            result = ScrapySide().parse_data(extract_args["url"], user_id)
            rendered_result = render_template("home_page.html", result=result, table_name=table_name)
            return make_response(rendered_result, status.HTTP_200_OK, self.DEFAULT_HEADERS)
        elif show_args:
            table_name = "Table of already existing data"
            result = DatabaseDispatcher().get_exist_data(show_args, user_id)
            rendered_result = render_template("home_page.html", result=result, table_name=table_name)
            return make_response(rendered_result, status.HTTP_200_OK, self.DEFAULT_HEADERS)
        else:
            return {"result": "BAD REQUEST!"}, status.HTTP_400_BAD_REQUEST


class SignUpPage(Resource):
    DEFAULT_HEADERS = {'Content-Type': 'text/html'}

    @logout_required
    def get(self):
        rendered_result = render_template("signup_page.html", result={})
        return make_response(rendered_result, status.HTTP_200_OK, self.DEFAULT_HEADERS)

    @logout_required
    def post(self):
        log_in_args = request.form
        result = Users().create_user(log_in_args)
        if result.get("error"):
            rendered_result = render_template("signup_page.html", result=result)
            return make_response(rendered_result, status.HTTP_403_FORBIDDEN, self.DEFAULT_HEADERS)
        else:
            session["is_logged_in"] = True
            session["user_id"] = result["user_id"]
            return redirect(url_for("incense"), code=status.HTTP_302_FOUND)


class LoginPage(Resource):
    DEFAULT_HEADERS = {'Content-Type': 'text/html'}

    @logout_required
    def get(self):
        rendered_result = render_template("login_page.html", result={})
        return make_response(rendered_result, status.HTTP_200_OK, self.DEFAULT_HEADERS)

    @logout_required
    def post(self):
        log_in_args = request.form
        result = DatabaseDispatcher().get_user(log_in_args)
        if result.get("error"):
            result = {"error": {"message": "Credentials are wrong"}}
            rendered_result = render_template("login_page.html", result=result)
            return make_response(rendered_result, status.HTTP_401_UNAUTHORIZED, self.DEFAULT_HEADERS)
        else:
            session["is_logged_in"] = True
            session["user_id"] = result["user_id"]
            return redirect(url_for("incense"), code=status.HTTP_302_FOUND)


class LogoutPage(Resource):
    DEFAULT_HEADERS = {'Content-Type': 'text/html'}

    @login_required
    def get(self):
        session.clear()
        return redirect(url_for("login"), code=status.HTTP_302_FOUND)


API.add_resource(MainPage, "/incense", endpoint="incense")
API.add_resource(SignUpPage, "/signup", endpoint="signup")
API.add_resource(LoginPage, "/login", endpoint="login")
API.add_resource(LogoutPage, "/logout", endpoint="logout")


if __name__ == "__main__":
    APP.run(debug=True)
