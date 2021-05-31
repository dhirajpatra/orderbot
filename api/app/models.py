
import datetime
import hashlib
from app import db, ma
from sqlalchemy.orm import validates


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    phone_number = db.Column(db.String(12))
    phone_number_encrypted = db.Column(db.String(256))
    password = db.Column(db.String(256))
    email = db.Column(db.String(256), unique=True, nullable=False)
    hook = db.Column(db.String(256), unique=True, nullable=False, server_default=None)
    bot_token = db.Column(db.Text())
    welcome_msg = db.Column(db.Text()) # it will show when customer say Hi
    type_of_business = db.Column(db.Integer, nullable=False, server_default='1') # 1 = room booking 2 = food 3 = service
    created_at = db.Column(db.DateTime, default=datetime.datetime.now())

    def __init__(self, phone_number, phone_number_encrypted, password, email, hook, bot_token, type_of_business, welcome_msg):
        self.phone_number = phone_number
        self.phone_number_encrypted = phone_number_encrypted
        self.password = password
        self.email = email
        self.hook = hook
        self.bot_token = bot_token
        self.type_of_business = type_of_business
        self.welcome_msg = welcome_msg

    def __repr__(self):
        return f"<User {self.phone_number, self.phone_number_encrypted, self.hook, self.bot_token, self.email, self.type_of_business, self.welcome_msg}>"

    def serialize(self):
        """
        Custom method used within api to serialize database objects into
        JSON.
        """
        return {
            'id': self.id,
            'phone_number': self.phone_number,
            'phone_number_encrypted': self.phone_number_encrypted,
            'password': self.password,
            'email': self.email,
            'hook': self.hook,
            'bot_token': self.bot_token,
            'type_of_business': self.type_of_business,
            'welcome_msg': self.welcome_msg
        }

# user catalogue details 
class User_catalogue(db.Model):
    __tablename__ = "user_catalogues"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    property_id = db.Column(db.Integer)
    property_name = db.Column(db.String(256))
    catalogue_image = db.Column(db.String(256))
    price = db.Column(db.String(20))
    currency = db.Column(db.String(20))
    id_ru = db.Column(db.Integer)
    link = db.Column(db.Text)


    def __init__(self, user_id, property_id, property_name, catalogue_image, price, currency, id_ru, link):
        self.user_id = user_id
        self.property_id = property_id
        self.property_name = property_name
        self.catalogue_image = catalogue_image
        self.price = price
        self.currency = currency
        self.id_ru = id_ru
        self.link = link

    def __repr__(self):
        return f"<User Catalogue {self.user_id, self.property_id, self.property_name, self.catalogue_image, self.price, self.currency, self.id_ru, self.link}>"

    def serialize(self):
        """
        Custom method used within api to serialize database objects into
        JSON.
        """
        return {
            'id': self.id,
            'property_id': self.property_id,
            'property_name': self.property_name,
            'catalogue_image': self.catalogue_image,
            'price': self.price,
            'currencey': self.currency,
            'id_ru': self.id_ru,
            'link': self.link
        }

# api companies
class User_api_company(db.Model):
    __tablename__ = "user_api_companies"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    comapny_name = db.Column(db.String(256))

    def __init__(self, company_name):
        self.comapny_name = company_name

    def __repr__(self):
        return f"<API Company {self.id, self.comapny_name}>"

    def serialize(self):
        """
        Custom method used within api to serialize database objects into
        JSON.
        """
        return {
            'id': self.id,
            'company_name': self.comapny_name
            }

# to connect client's business database using their API
class User_api_details(db.Model):
    __tablename__ = "user_api_details"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    key = db.Column(db.String(256))
    host = db.Column(db.String(256), unique=True, nullable=False)
    username = db.Column(db.String(256))
    password = db.Column(db.String(256))
    api_company_id = db.Column(db.Integer, db.ForeignKey('user_api_companies.id'), nullable=False)

    def __init__(self, user_id, key, host, username, password, api_company_id):
        self.user_id = user_id
        self.key = key
        self.host = host
        self.username = username
        self.password = password
        self.api_company_id = api_company_id

    def __repr__(self):
        return f"<User_api_details {self.user_id, self.key, self.host, self.username, self.password, self.api_company_id}>"

    def serialize(self):
        """
        Custom method used within api to serialize database objects into
        JSON.
        """
        return {
            'id': self.id,
            'user_id': self.user_id,
            'key': self.key,
            'host': self.host,
            'username': self.username,
            'password': self.password,
            'api_company_id': self.api_company_id
        }

# client's API all requsts details
class User_api_urls(db.Model):
    __tablename__ = "user_api_urls"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    api_name = db.Column(db.String(256))
    method = db.Column(db.String(10))
    requirement_header = db.Column(db.Text())
    requirement_body = db.Column(db.Text())
    requirement_response = db.Column(db.Text())

    def __init__(self, user_id, api_name, method, requirement_header, requirement_body, requirement_response):
        self.user_id = user_id
        self.api_name = api_name
        self.method = method
        self.requirement_header = requirement_header
        self.requirement_body = requirement_body
        self.requirement_response = requirement_response

    def __repr__(self):
        return f"<User_api_urls {self.user_id, self.user, self.api_name, self.method, self.requirement_header, self.requirement_body, self.requirement_response}>"

    def serialize(self):
        """
        Custom method used within api to serialize database objects into
        JSON.
        """
        return {
            'id': self.id,
            'user_id': self.user_id,
            'api_name': self.api_name,
            'method': self.method,
            'requirement_header': self.requirement_header,
            'requirement_body': self.requirement_body,
            'requirement_response': self.requirement_response
        }

# all messages from user for each client
class Message(db.Model):
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    phone = db.Column(db.String(15))
    body = db.Column(db.Text(), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now())

    def __init__(self, user_id, phone, body):
        self.user_id = user_id
        self.phone = phone
        self.body = body 

    def __repr__(self):
        return f"<Message {self.user_id, self.phone, self.body}"

    def serialize(self):
        """
        Custom method used within api to serialize database objects into
        JSON.
        """
        return {
            'id': self.id,
            'user_id': self.user_id,
            'phone': self.phone,
            'body': self.body
        }
