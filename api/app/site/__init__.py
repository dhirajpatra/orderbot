from flask import Blueprint



site = Blueprint('site', __name__, template_folder='templates')
auth = Blueprint('auth', __name__, template_folder='templates')
message = Blueprint('message', __name__, template_folder='templates/blog')
