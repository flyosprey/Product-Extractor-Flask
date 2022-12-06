from flask import request, render_template, make_response
from flask_api import status
from flask_restful import Resource
from flask_app.scrapy_side import ScrapySide
from flask_app.database_dispatcher import DatabaseDispatcher
from flask import session
from flask_app.decorators import login_required


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
