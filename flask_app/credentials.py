import os
from decouple import config


HOSTNAME = os.getenv('POSTGRES_HOST')
USERNAME = os.getenv('POSTGRES_USER')
PASSWORD = os.getenv('POSTGRES_PASSWORD')
DATABASE = os.getenv('POSTGRES_DB')
PORT = os.getenv('POSTGRES_PORT')
SECRET_KEY = config('SECRET_KEY')
