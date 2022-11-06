from flask import Flask
from flask_restful import Api
from credentials import SECRET_KEY

APP = Flask(__name__)
API = Api(APP)


APP.config['SESSION_TYPE'] = 'memcached'
APP.config['SECRET_KEY'] = SECRET_KEY
