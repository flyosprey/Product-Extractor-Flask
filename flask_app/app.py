from flask import request, render_template, make_response
from flask_api import status
from flask_restful import Resource
from flask_app.settings import APP, API
from flask_app.scrapy_side import ScrapySide
from flask_app.database_dispatcher import DatabaseDispatcher


class MainPage(Resource):
    DEFAULT_HEADERS = {'Content-Type': 'text/html'}

    def get(self):
        rendered_result = render_template("home_page.html")
        return make_response(rendered_result, status.HTTP_200_OK, self.DEFAULT_HEADERS)

    def post(self):
        extract_args = request.form if "url" in request.form else None
        show_args = request.form if "limit" in request.form else None
        if extract_args:
            table_name = "Таблиця щойно зібраних товарів"
            result = ScrapySide().parse_data(extract_args["url"])
            rendered_result = render_template("home_page.html", result=result, table_name=table_name)
            return make_response(rendered_result, status.HTTP_200_OK, self.DEFAULT_HEADERS)
        elif show_args:
            table_name = "Таблиця вже наявних товарів"
            result = DatabaseDispatcher().get_exist_data(show_args)
            rendered_result = render_template("home_page.html", result=result, table_name=table_name)
            return make_response(rendered_result, status.HTTP_200_OK, self.DEFAULT_HEADERS)
        else:
            return {"result": "BAD REQUEST!"}, status.HTTP_400_BAD_REQUEST


API.add_resource(MainPage, "/incense")


if __name__ == "__main__":
    APP.run(debug=True)
