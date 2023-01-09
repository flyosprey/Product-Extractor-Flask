from flask_api import status
from settings import APP, API
from flask import redirect, url_for
from controllers.login import LoginPage
from controllers.logout import LogoutPage
from controllers.signup import SignUpPage
from controllers.incense import Incense

@APP.errorhandler(status.HTTP_404_NOT_FOUND)
def resource_not_found(request):
    return redirect(url_for("incense"), code=status.HTTP_302_FOUND)


API.add_resource(Incense, "/incense", endpoint="incense")
API.add_resource(SignUpPage, "/signup", endpoint="signup")
API.add_resource(LoginPage, "/login", endpoint="login")
API.add_resource(LogoutPage, "/logout", endpoint="logout")


if __name__ == "__main__":
    APP.run(host='0.0.0.0')
