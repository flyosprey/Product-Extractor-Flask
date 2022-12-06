from flask import request, render_template, make_response
from flask_api import status
from flask_restful import Resource
from flask_app.scrapy_trigger import ScrapyTrigger
from flask_app.database_dispatcher import DatabaseDispatcher
from flask import session
from flask_app.decorators import login_required
from flask_app.user_input_validator import UserInputValidator


class Incense(Resource):
    __slots__ = ("DEFAULT_HEADERS",)

    def __init__(self):
        self.DEFAULT_HEADERS = {'Content-Type': 'text/html'}

    @login_required
    def get(self):
        rendered_result = render_template("incense.html")
        return make_response(rendered_result, status.HTTP_200_OK, self.DEFAULT_HEADERS)

    @login_required
    def post(self):
        user_id, form_args = session["user_id"], request.form
        is_extract_args_valid, is_show_args_args_valid = self._put_through_validator(form_args)
        if is_extract_args_valid:
            table_name, scrape = "Table of extracted data", ScrapyTrigger()
            result = scrape.parse_data(form_args["url"], user_id)
            rendered_result = render_template("incense.html", result=result, table_name=table_name)
            return make_response(rendered_result, status.HTTP_200_OK, self.DEFAULT_HEADERS)
        elif is_show_args_args_valid:
            table_name, dispatcher = "Table of already existing data", DatabaseDispatcher()
            result = dispatcher.get_exist_data(form_args, user_id)
            rendered_result = render_template("incense.html", result=result, table_name=table_name)
            return make_response(rendered_result, status.HTTP_200_OK, self.DEFAULT_HEADERS)
        else:
            return {"result": "BAD REQUEST!"}, status.HTTP_400_BAD_REQUEST

    @staticmethod
    def _put_through_validator(form_args):
        validator = UserInputValidator()
        is_extract_args_valid, is_show_args_args_valid = validator.valid_extract_args(form_args), False
        if not is_extract_args_valid:
            is_show_args_args_valid = validator.valid_show_args(form_args)
        return is_extract_args_valid, is_show_args_args_valid
