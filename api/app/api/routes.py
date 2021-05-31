from flask import Flask, jsonify, request, abort, make_response, current_app, render_template, url_for
from sqlalchemy.exc import IntegrityError
import requests
import os
import json
import re
import operator
import nltk
from collections import Counter
from bs4 import BeautifulSoup
import calendar

# from tinydb import TinyDB, Query
# from .. import redis_client
import redis

from ..models import db, User, Message, User_api_company, User_api_details, User_api_urls, User_catalogue
from . import api
from ..database import get_all, add_instance, delete_instance, edit_instance
from . import AlchemyEncoder

from .rentals import Rentals
from .telegram_rentals import TelegramRentals
# from chatterbot import ChatBot
# from chatterbot.trainers import ChatterBotCorpusTrainer


redis_url = os.getenv('REDISTOGO_URL', os.environ['REDIS_URL'])
redis_client = redis.from_url(redis_url)
print("redis client connected " + str(redis_client))

# english_bot = ChatBot("English Bot", database_uri = os.environ['SQLALCHEMY_DATABASE_URI'])
# trainer = ChatterBotCorpusTrainer(english_bot)
# trainer.train("chatterbot.corpus.english")

# signal definition
def log_request(sender, user, **extra):
    if request.method == 'POST':
        message = 'user is created: id {}'.format(user.id)
    elif request.method == 'PUT':
        message = 'user is updated: id {}'.format(user.id)
    else:
        message = 'user is deleted: id {}'.format(user.id)
    sender.logger.info(message)

# custom 404 error handler
@api.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'detail': 'Not found'}), 404)


# custom 400 error handler
@api.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'detail': 'Bad request'}), 400)

# hook for whatsapp this is work as a API gateway for all hooks
# it will match with individualt phone_number_encrypted for each business client
@api.route('/twilio_hook/<phone_number_encrypted>', methods=['POST'])
def twilio_hook(phone_number_encrypted):
    response = None

    # first check and find out which method need to call for a business
    user = redis_client.get('user_' + phone_number_encrypted)
    api_details = redis_client.get('api_details_' + phone_number_encrypted)
    if user == None or api_details == None:
        user = User.query.filter_by(phone_number_encrypted = phone_number_encrypted).first()
        api_details = User_api_details.query.filter_by(user_id=user.id).first()
        redis_client.set('user_' + phone_number_encrypted, json.dumps(user, cls=AlchemyEncoder), 600)
        redis_client.set('api_details_' + phone_number_encrypted, json.dumps(api_details, cls=AlchemyEncoder), 600)
    user = json.loads(redis_client.get('user_' + phone_number_encrypted).decode('utf-8'))
    api_details = json.loads(redis_client.get('api_details_' + phone_number_encrypted).decode('utf-8'))
#     {"api_company_id": 1, "host": "https://hiresicily.holigest.it/", "id": 1, "key": "testapikey", "password":
# "ARP_x5_21-@", "query": null, "query_class": null, "serialize": null, "user_id": 1, "username": "GioApi"}
    
    #categorically call to different class
    switcher = {
        1: "rental", 
        2: "food",
        3: "service" 
    } 

    company_type = switcher.get(str(api_details['api_company_id']), "rentals")
    
    if company_type == 'rentals':
        rentals = Rentals()    
        return rentals.hook(user, request) 

# hook for telegram this is work as a API gateway for all hooks
# it will match with individualt phone_number_encrypted for each business client
# eg. https://api.telegram.org/bot1554105343:AAFf1o2h9nhzholCwQjhFKhIBdAFMlt0of8/setWebhook?url=https://aab6292c4194.ngrok.io/api/v1/telegram_hook/37470c9583a8de5932b3f944391edb54
@api.route('/telegram_hook/<phone_number_encrypted>', methods=['POST'])
def telegram_hook(phone_number_encrypted):
    response = None
    # print(phone_number_encrypted)
    # first check and find out which method need to call for a business
    user = redis_client.get('user_' + phone_number_encrypted)
    api_details = redis_client.get('api_details_' + phone_number_encrypted)
    if user == None or api_details == None:
        user = User.query.filter_by(phone_number_encrypted = phone_number_encrypted).first()
        api_details = User_api_details.query.filter_by(user_id=user.id).first()
        redis_client.set('user_' + phone_number_encrypted, json.dumps(user, cls=AlchemyEncoder), 600)
        redis_client.set('api_details_' + phone_number_encrypted, json.dumps(api_details, cls=AlchemyEncoder), 600)
    user = json.loads(redis_client.get('user_' + phone_number_encrypted).decode('utf-8'))
    api_details = json.loads(redis_client.get('api_details_' + phone_number_encrypted).decode('utf-8'))
    # print(api_details)
#     {"api_company_id": 1, "host": "https://hiresicily.holigest.it/", "id": 1, "key": "testapikey", "password":
# "ARP_x5_21-@", "query": null, "query_class": null, "serialize": null, "user_id": 1, "username": "GioApi"}
    
    #categorically call to different class
    switcher = {
        1: "rental", 
        2: "food",
        3: "service" 
    } 
    
    company_type = switcher.get(str(api_details['api_company_id']), "rentals")
    
    if company_type == 'rentals':
        rentals = TelegramRentals()    
        return rentals.hook(user, request) 

@api.route('/users', methods=['GET'])
def list_users():
    users = User.query.all()
    return jsonify(users=[i.serialize() for i in users])


@api.route('/users', methods=['POST'])
def create_user():
    try:
        new_user = User(
            name=request.json.get('name'),
            description=request.json.get('description'))
        db.session.add(new_user)
        db.session.commit()
        user = User.query.filter_by(name=request.json.get('name')).first()
        # signal using
        log_request(current_app._get_current_object(), user)
        return jsonify(user=user.serialize()), 201
    except IntegrityError:
        return abort(400)


@api.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    id = request.view_args.get('id')
    user = User.query.get_or_404(id)
    return jsonify(user=[user.serialize()])


@api.route('/users/<int:id>', methods=['PUT'])
def update_user(id):
    try:
        id = request.view_args.get('id')
        user = User.query.get_or_404(id)
        user.name = request.json.get('name')
        user.description = request.json.get('description')
        db.session.commit()
        updated_user = User.query.filter_by(name=user.name).first()
        # signal using
        log_request(current_app._get_current_object(), user)
        return jsonify(user=updated_user.serialize())
    except IntegrityError:
        return abort(400)


@api.route('/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    id = request.view_args.get('id')
    user = User.query.get_or_404(id)
    User.query.filter_by(id=id).delete()
    # signal using
    log_request(current_app._get_current_object(), user)
    db.session.commit()
    return jsonify({}), 204


@api.route('/date_selector/<phone_number_encrypted>', methods=['GET'])
def date_selector(phone_number_encrypted):
    error = None
    return render_template("date_selector.html", error=error) 

@api.route("/chatterbot")
def home():
    return render_template("bot.html")

@api.route("/chatterbot_test")
def get_bot_response():
    userText = request.args.get('msg')
    return str(english_bot.get_response(userText))

