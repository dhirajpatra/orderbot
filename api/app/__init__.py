from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow
from config import base


bootstrap = Bootstrap()


# create app instance
app = Flask(__name__)

# add configuration
app.config.from_object(base)

# register extensions
bootstrap.init_app(app)

# init db
db = SQLAlchemy(app)
db.init_app(app)
db.create_all()
# init ma
ma = Marshmallow(app)
# init migration
migrate = Migrate(app, db)


"""
first, import db to setup app context
from run import db

then, import model to use it with queries
from app.models import User
"""
