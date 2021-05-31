# flake8: noqa
import os

basedir = os.path.abspath(os.path.dirname(__file__))

DEBUG = os.getenv('DEBUG', False)
SECRET_KEY = os.getenv('SECRET_KEY')
SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI', "sqlite://")
SQLALCHEMY_TRACK_MODIFICATIONS = False
REDIS_URL = os.getenv('REDIS_URL')
REDIS_HOST = os.getenv('REDIS_HOST')
REDIS_PORT = os.getenv('REDIS_PORT')
REDIS_DB = os.getenv('REDIS_DB')
UPLOAD_FOLDER = '/static/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
MAX_CONTENT_LENGTH = 3 * 1000 * 1000 # upto 3 MB
