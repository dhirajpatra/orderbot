
from flask import Flask, jsonify, request, abort, make_response, current_app, url_for
from sqlalchemy.exc import IntegrityError
import requests
import os
import re
import operator

from werkzeug.wrappers import ResponseStream
import nltk
from collections import Counter
from bs4 import BeautifulSoup
import calendar
import datetime
import locale
import decimal

# from tinydb import TinyDB, Query
# from .. import redis_client
import redis
import json

import telegram
from .orderbot_telegram import OrderbotTelegram

from ..models import User_catalogue, db, User, Message, User_api_company, User_api_details, User_api_urls, User_catalogue
from . import api
from ..database import get_all, add_instance, delete_instance, edit_instance
from . import AlchemyEncoder

# from chatterbot import ChatBot
# from chatterbot.trainers import ChatterBotCorpusTrainer


redis_url = os.getenv('REDISTOGO_URL', os.environ['REDIS_URL'])
redis_client = redis.from_url(redis_url)
print("redis client connected " + str(redis_client))


class TelegramRentals():
    
    incoming_msg = None
    responded = False
    from_phone_number = None
    to_phone_number = None
    steps = 0
    sender_redis = None
    sender_redis_payload = None
    ans = None
    cl = None
    types = None
    result = None
    stop_words = None
    img1 = None
    img2 = None
    person = 0
    selected = False
    holigest = None
    language = 'EN'
    checked = False
    customer_details = None
    payment_method = None
    payment_methods = None
    open_street_map_url = None
    chat_id = None # same as from_phone_number
    order_bot = None
    message_id = None
    cache_time = 300

    def __init__(self) -> None:
        super().__init__()
        
        self.stop_words = ['i','me','my','myself','we','our','ours','ourselves','you','your','yours','yourself','yourselves','he','him','his','himself','she','her','hers','herself','it','its','itself','they','them','their','theirs','themselves','what','which','who','whom','this','that','these','those','am','is','are','was','were','be','been','being','have','has','had','having','do','does','did','doing','a','an','the','and','but','if','or','because','as','until','while','of','at','by','for','with','about','against','between','into','through','during','before','after','above','below','to','from','up','down','in','out','on','off','over','under','again','further','then','once','here','there','when','where','why','how','all','any','both','each','few','more','most','other','some','such','no','nor','not','only','own','same','so','than','too','very','s','t','can','will','just','don','should','now','id', 'var',
        'function', 'js', 'd', 'script', '\'script', 'fjs', 'document', '\'s']
        
        # need to send sid and token as per business account / client account
        account_sid = os.getenv('TWILIO_ACCOUNT_SID', None)
        auth_token = os.getenv('TELEGRAM_BOT_TOKEN', None)

        self.bot = OrderbotTelegram(auth_token)
        # print(self.bot)
        self.ans = [str(int) for int in list(range(1, 100))]
        self.types = ['room', 'holiday', 'villa', 'accommodation', 'tour', 'hire', 'sicily', 'sea', 'beaches']
        self.first_msg = ['/start', 'start', 'hi', 'hoi', 'help', 'support', 'how']
        self.checked = False
        self.payment_methods = {'A':'Crypto', 'B': 'Paypal'}

        

    def hook(self, user, request):
        # print(request.get_json(force=True))
        # {'update_id': 156970521, 'message': {'message_id': 102, 'from': {'id': 1478327466, 'is_bot': False, 'first_name': 'Dhiraj', 'last_name': 'Patra', 'username': 'dhirajpatra', 'language_code': 'en'}, 'chat': {'id': 1478327466, 'first_name': 'Dhiraj', 'last_name': 'Patra', 'username': 'dhirajpatra', 'type': 'private'}, 'date': 1614134734, 'text': 'hi'}}

        updates = request.json
        # print(updates)
        if updates:
            try:
                update_id = updates["update_id"]
                self.message_id = updates["message"]["message_id"]
                message = updates["message"]["text"]
            except:
                updates = None
                self.message_id = None
                message = None

            from_ = updates["message"]["from"]["id"]
            # reply = self.make_reply(message)
            # self.bot.msg_resp(reply, from_)

            # for testing from rest api client
            # end user's phone number
            self.from_phone_number = from_
            self.chat_id = from_
            # business's phone number
            self.to_phone_number = 'bizorderbot'

            self.incoming_msg = message
            print('user id')
            print(self.from_phone_number)
            print('incoming msg')
            print(self.incoming_msg)

            try:
                # check in date matching   
                self.matched = re.search(r'(\d{1,2}/\d{1,2}/\d{4})', self.incoming_msg)
                
                # how many person
                result_person = re.search(r'(\d{1,2})', self.incoming_msg)
                if result_person:
                    self.person = result_person.group(0)

                self.result = filter(lambda x: self.incoming_msg.find(x) != -1, self.types)
                self.open_street_map_url = "https://www.openstreetmap.org/#map="
                # print(self.incoming_msg.isdigit())

                # check the cache for this user to maintain a session like process
                self.sender_redis = redis_client.get(self.from_phone_number)
                # print(self.sender_redis)
                # first or start from the beginning 
                if self.sender_redis == None or [ele for ele in self.first_msg if(ele == self.incoming_msg.lower())]:
                    self.sender_redis_payload = {
                        'steps':0, 
                        'last_incoming_msg':self.incoming_msg,
                        'last_reply':'',
                        'check_in_date':'',
                        'check_out_date': '',
                        'persons': self.person,
                        'children': 0,
                        'days':0,
                        'selected':'',
                        'total_price':0,
                        'matched_properties':'',
                        'i': 0,
                        'customer_details': '',
                        'customer_registration_details': '',
                        'customer_payment_details': '',
                        'last_update':datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                    self.sender_redis_payload = json.dumps(self.sender_redis_payload)
                    # set cache for 10 min
                    redis_client.set(self.from_phone_number, self.sender_redis_payload, self.cache_time)
                    self.sender_redis = json.loads(redis_client.get(self.from_phone_number))
                    self.steps = 0
                else:
                    self.sender_redis = json.loads(redis_client.get(self.from_phone_number))
                    self.steps = self.sender_redis['steps']
                print('steps ' + str(self.steps))

                # payment
                if len(self.incoming_msg) == 1 and int(self.steps) == 6:
                    check = re.search('[a-zA-Z]?', self.incoming_msg)
                    if check.group(0) != '':
                        self.checked = True

                # make the selction of property
                if len(self.incoming_msg) == 1 and int(self.steps) == 4:
                    check = re.search('[a-zA-Z]?', self.incoming_msg)
                    if check.group(0) != '':
                        self.checked = True
                    elif int(self.incoming_msg) != 0:
                        self.bot.body(self.chat_id, "\n 🚫 Worng answer, kindly send <b>only 0 to see more</b> or <b>single alphabet character to select eg. a or b</b>", self.message_id)
                        return "ok"
                
                # get the customer details
                elif int(self.steps) == 5:
                    self.incoming_msg = self.incoming_msg.replace(" ", "")
                    result  = re.search(r'\w*,\w*,[\w.-]+@[\w.-]+', self.incoming_msg)
                    if result.group() == self.incoming_msg:
                        self.customer_details = self.incoming_msg.split(',')
                    else:
                        self.bot.body(self.chat_id, "\n 🏁 <b>Wrong email, kindly send the details again in first_name,last_name,email format</b>", self.message_id)

                # select payment method
                elif len(self.incoming_msg) == 1 and int(self.steps) == 6:
                    check = re.search('[a-zA-Z]?', self.incoming_msg)
                    if check.group(0) != '':
                        self.payment_method = self.payment_methods[self.incoming_msg.upper()]

                # verify the current input and give user a chance to fix
                elif int(self.steps) == 1 and self.matched == None:
                    self.bot.body(self.chat_id, "\n 🚫 Wrong date or format, kindly send checkin date in <b>dd/mm/yyyy</b> format only", self.message_id)
                    return "ok"
                # person can be 1 or more
                elif ((int(self.steps) == 2 or int(self.steps) == 3) and self.incoming_msg not in self.ans):
                    self.bot.body(self.chat_id, "\n 🚫 Wrong number, kindly send <b>only number eg. 5</b>", self.message_id)
                    return "ok"
                # # child can be 0 or more
                # elif (int(self.steps) == 4 and not self.incoming_msg.isdigit()):
                #     self.bot.body(self.chat_id, "\n 🚫 Wrong number, kindly send <b>only number eg. 0 or more</b>", self.message_id)
                #     return "ok"

                # elif int(self.steps) == 4 and int(self.incoming_msg) != 0 and self.checked == False:
                #     self.bot.body(self.chat_id, "\n 🚫 Worng answer, kindly send <b>only 0 to see more</b> or <b>single alphabet character to select eg. a or b</b>", self.message_id)
                #     return "ok"
               
            except:
                # self.bot.body("\n 🏁 *Kindly start from the beginning. You can start with say 'hi'*", self.chat_id)
                self.bot.body(self.chat_id, "\n 🏁 <b>Kindly start from the beginning. You can start with say 'hi'</b>", self.message_id)
            
            # fetch the details 
            
            # AI NLP processing
            # nltk.data.path.append('./nltk_data/')  # set the path
            # tokens = nltk.word_tokenize(holiget_response)
            # text = nltk.Text(tokens)
            # # remove punctuation, count raw words
            # nonPunct = re.compile('.*[A-Za-z].*')
            # raw_words = [w for w in text if nonPunct.match(w)]
            # raw_word_count = Counter(raw_words)
            # # stop words
            # no_stop_words = [w for w in raw_words if w.lower() not in stop_words]
            # no_stop_words_count = Counter(no_stop_words)
            # # save the results
            # results = sorted(
            #     no_stop_words_count.items(),
            #     key=operator.itemgetter(1),
            #     reverse=True
            # )

            if [ele for ele in self.first_msg if(ele == self.incoming_msg.lower())] and int(self.sender_redis['steps']) == 0:
                body1 = None
                body2 = None
                body3 = None
                calendar_path = None
                
                body1 = '🇮🇹 🏘️ ' + user['welcome_msg'].replace("\n", " \n ")
                now = datetime.datetime.now()
                # current_cal = calendar.calendar(now.year)
                # current_cal = calendar.month(now.year, now.month)
                calendar_path = request.host_url.strip("/") + url_for('static', filename='images/'+ str(now.year) + '_calendar.png')
                calendar_path = calendar_path.replace("http:", "https:")

                room_type_redis = redis_client.get('room_type_redis')
                if room_type_redis == None:
                    redis_client.set('room_type_redis', self.incoming_msg, self.cache_time)
                    room_type_redis = redis_client.get('room_type_redis')

                    body2 = '\n _For reference_ \n'
                    body3 = '\n <b>What is your expected 🛬 Check-in date?</b> [format: <b>dd/mm/yyyy</b>] eg. 10/01/2021\n'
                else:
                    body2 = '\n _For reference_ \n'
                    body3 = '\n <b>What is your expected 🛬 Check-in date?</b> [format: <b>dd/mm/yyyy</b>] eg. 10/01/2021\n'
                
                body = body1 + body2 + body3
                # self.bot.media(self.chat_id, calendar_path, "Calendar 2021", self.message_id)
                self.bot.media(self.chat_id, "https://cdn.pixabay.com/photo/2020/10/02/10/39/calendar-5620762_1280.png", "Calendar 2021", self.message_id)
                self.bot.body(self.chat_id, body, self.message_id)

                # update the redis cache for this customer/sender
                self.sender_redis_payload = {
                    'steps': 1, 
                    'last_incoming_msg':self.incoming_msg,
                    'last_reply': body3,
                    'check_in_date':'',
                    'check_out_date': '',
                    'check_in_date_redis_dt':'',
                    'check_out_date_redis_dt':'',
                    'persons': 0,
                    'children': 0,
                    'days':0,
                    'selected':'',
                    'total_price':0,
                    'matched_properties':'',
                    'i': 0,
                    'customer_details': '',
                    'customer_registration_details': '',
                    'customer_payment_details': '',
                    'last_update':datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                self.sender_redis_payload = json.dumps(self.sender_redis_payload)
                redis_client.set(self.from_phone_number, self.sender_redis_payload, self.cache_time)
                
                # self.resp.append(self.msg)
                # self.bot.respond(True)

            elif self.matched and int(self.steps) == 1:
                body = None
                check_in_date_redis =  None
                self.steps = int(self.steps) + 1
                if int(self.steps) == 2:                
                    check_in_date_redis = self.sender_redis['check_in_date']
                    if check_in_date_redis == '' and self.matched != None:
                        check_in_date_redis = self.matched.group() + ' 00:00:00'
                        check_in_date_redis_dt = datetime.datetime.strptime(check_in_date_redis, "%d/%m/%Y %H:%M:%S")
                        dt = datetime.datetime.combine(datetime.date.today(), datetime.datetime.min.time())
                        
                        if check_in_date_redis_dt >= dt:
                            body = 'From ' + self.matched.group() + ', 🛫 <b>how many days would you like to stay?</b> [reply only number eg. 7]'
                        else:
                            body = '\n 🙁 <b>Wrong date. Must be greater than today.</b>'
                else:
                    body = '\n 💡 <b>Kindly start from the beginning</b>'

                self.bot.body(self.chat_id, body, self.message_id)

                # update the redis cache for this customer/sender
                self.sender_redis_payload = {
                    'steps': self.steps, 
                    'last_incoming_msg':self.incoming_msg,
                    'last_reply': body,
                    'check_in_date': str(check_in_date_redis),
                    'check_out_date': '',
                    'check_in_date_redis_dt':'',
                    'check_out_date_redis_dt':'',
                    'persons':0,
                    'children': 0,
                    'days':0,
                    'selected':'',
                    'total_price':0,
                    'matched_properties':'',
                    'i': 0,
                    'customer_details': '',
                    'customer_registration_details': '',
                    'customer_payment_details': '',
                    'last_update':datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                self.sender_redis_payload = json.dumps(self.sender_redis_payload)
                redis_client.set(self.from_phone_number, self.sender_redis_payload, self.cache_time)

            #     self.bot.respond(True)

        return "ok"

    def show_catalogue(self, catalogue_image):
        path = request.host_url.strip("/") + url_for('static', filename='images/'+ catalogue_image)
        path = path.replace('http:', 'https:') 
        # resp = make_response(open(path).read())
        # resp.content_type = "image/jpeg"
        return path

    # EUR return €
    def convert_currency_symbol(self, c):
        locales=('en_AU.utf8', 'en_BW.utf8', 'en_CA.utf8', 'en_DK.utf8', 'en_GB.utf8', 'en_HK.utf8', 'en_IE.utf8', 'en_IN', 'en_NG', 'en_PH.utf8', 'en_US.utf8', 'en_ZA.utf8', 'en_ZW.utf8', 'ja_JP.utf8')

        for l in locales:
            locale.setlocale(locale.LC_ALL, l)
            conv=locale.localeconv()
            # print('{ics} ==> {s}'.format(ics=conv['int_curr_symbol'],s=conv['currency_symbol']))
            if c == conv['int_curr_symbol']:
                return conv['currency_symbol']

        return '€'

    # to find out the prices as per check_in and check_out date and response from tariff api date price ranges
    def get_tariff_date_range(self, check_in_date_redis, check_out_date_redis, response_preleva_tariffe_alloggi):
        check_in_date_redis = datetime.datetime.strptime(check_in_date_redis[:10], '%Y-%m-%d')
        check_out_date_redis = datetime.datetime.strptime(check_out_date_redis[:10], '%Y-%m-%d')
        
        for response in response_preleva_tariffe_alloggi:
            response['dal'] = datetime.datetime.strptime(response['dal'][:10], '%Y-%m-%d')
            response['al'] = datetime.datetime.strptime(response['al'][:10], '%Y-%m-%d')

            if check_in_date_redis >= response['dal'] and check_out_date_redis <= response['al']:
                return response['prezzoalgiorno']

        return '\nPrice not found for this check in and checkout date range\n'

    # to find out the weekly prices as per check_in and check_out date and response from tariff api date price ranges if checkout - checkin more >= week
    def get_weekly_tariff_date_range(self, check_in_date_redis, check_out_date_redis, response_preleva_tariffe_alloggi):
        check_in_date_redis = datetime.datetime.strptime(check_in_date_redis[:10], '%Y-%m-%d')
        check_out_date_redis = datetime.datetime.strptime(check_out_date_redis[:10], '%Y-%m-%d')

        for response in response_preleva_tariffe_alloggi:
            if check_in_date_redis >= response['dal'] and check_out_date_redis <= response['al']:
                # dd = int(str(check_out_date_redis - check_in_date_redis)[:2].strip())
                # if dd > 6:
                return response['prezzosettimana']
                # return response['prezzoalgiorno'] 

        return '\nPrice not found for this check in and checkout date range\n'

    def show_key_values_selection(self, dict):
        result = ''
        for k, v in dict.items():
            result += '\n<b>' + k + '</b>: ' + v + '\n'        
        return result