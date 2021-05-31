from flask import Flask, jsonify, request, abort, make_response, current_app, url_for
from sqlalchemy.exc import IntegrityError
import requests
import os
import re
import operator
import nltk
from collections import Counter
from bs4 import BeautifulSoup
import calendar
import datetime
import locale

# from tinydb import TinyDB, Query
# from .. import redis_client
import redis
import json

from twilio.twiml.messaging_response import MessagingResponse

from ..models import User_catalogue, db, User, Message, User_api_company, User_api_details, User_api_urls, User_catalogue
from . import api
from ..database import get_all, add_instance, delete_instance, edit_instance
from . import AlchemyEncoder

from .holigest import Holigest


redis_url = os.getenv('REDISTOGO_URL', os.environ['REDIS_URL'])
redis_client = redis.from_url(redis_url)
print("redis client connected " + str(redis_client))

class Rentals():
    
    incoming_msg = None
    responded = False
    ans = None
    cl = None
    types = None
    result = None
    stop_words = None
    img1 = None
    img2 = None

    def __init__(self) -> None:
        super().__init__()
        
        self.stop_words = ['i','me','my','myself','we','our','ours','ourselves','you','your','yours','yourself','yourselves','he','him','his','himself','she','her','hers','herself','it','its','itself','they','them','their','theirs','themselves','what','which','who','whom','this','that','these','those','am','is','are','was','were','be','been','being','have','has','had','having','do','does','did','doing','a','an','the','and','but','if','or','because','as','until','while','of','at','by','for','with','about','against','between','into','through','during','before','after','above','below','to','from','up','down','in','out','on','off','over','under','again','further','then','once','here','there','when','where','why','how','all','any','both','each','few','more','most','other','some','such','no','nor','not','only','own','same','so','than','too','very','s','t','can','will','just','don','should','now','id', 'var',
        'function', 'js', 'd', 'script', '\'script', 'fjs', 'document', 'r',
        'b', 'g', 'e', '\'s', 'c', 'f', 'h', 'l', 'k']

        self.resp = MessagingResponse()
        self.msg = self.resp.message()
        self.ans = [str(int) for int in list(range(1, 100))]
        self.cl = ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o')
        self.types = ['room', 'holiday', 'villa', 'accommodation', 'tour', 'hire', 'sicily', 'sea', 'beaches']
        self.first_msg = ['hi', 'hoi', 'help', 'support', 'how']

    def hook(self, user, request_body):
        print(request_body)
        self.incoming_msg = request_body
        self.matched = re.search(r'(\d+/\d+/\d+)', self.incoming_msg)
        self.result = filter(lambda x: self.incoming_msg.find(x) != -1, self.types)
        
        # return jsonify("Welcome from OrderBot hook" + self.incoming_msg), 201
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
        
        # if 'quote' in incoming_msg:
        #     # return a quote
        #     r = requests.get('https://api.quotable.io/random')
        #     if r.status_code == 200:
        #         data = r.json()
        #         quote = f'{data["content"]} ({data["author"]})'
        #     else:
        #         quote = 'I could not retrieve a quote at this time, sorry.'
        #     msg.body(quote)
        #     responded = True
        # if 'cat' in incoming_msg:
        #     # return a cat pic
        #     msg.media('https://cataas.com/cat')
        #     responded = True
        
        if [ele for ele in self.first_msg if(ele in self.incoming_msg)]:
            steps = redis_client.get('steps')
            if steps == None:
                redis_client.set('steps', 1)
                steps = redis_client.get('steps')

            if int(steps) == 1:
                body = user['welcome_msg']
            else:
                body = user['welcome_msg']
            
            self.msg.body(str(body))
            self.responded = True
        elif list(self.result) != [] or 'catalogue' in self.incoming_msg or self.incoming_msg == '#':
            steps = redis_client.get('steps')

            body = ''
            type = ''
            question = ''
            more = ''
            
            if int(steps) < 2 or self.incoming_msg == '#':
                redis_client.set('steps', 2)
                steps = redis_client.get('steps')

            if int(steps) == 2 or self.incoming_msg == '#':
                # it is need to fetch the room type from holigest API
                phone_number_encrypted_redis = redis_client.get('phone_number_encrypted_redis')
                
                # fetch all catalogue and keep in redis
                user_catalogue_redis = redis_client.get('user_catalogue_redis')
                if user_catalogue_redis == None:
                    user_catalogue = User_catalogue.query.filter_by(user_id=user['id']).all()
                    redis_client.set('user_catalogue_redis', json.dumps(user_catalogue, cls=AlchemyEncoder), 3600)
                    user_catalogue_redis = json.loads(redis_client.get('user_catalogue_redis').decode('utf-8'))
                else:
                    user_catalogue_redis = json.loads(redis_client.get('user_catalogue_redis').decode('utf-8'))

                # i = 0
                # for catalogue in user_catalogue_redis:
                #     media_url = self.show_catalogue(catalogue['catalogue_image'])
                #     print(media_url)
                #     if catalogue['currency'] == None:
                #         currency = 'EURO'
                #     else:
                #         currency = catalogue['currency']

                #     body = '\r\n' + chr(ord('a') + i).upper() + ': price per day ' + self.convert_currency_symbol(str(currency)) + str(catalogue['price']) + '\nclick below to see the image and details of property\n' + media_url + '\r\n'
                #     i = i + 1
                #     # self.msg.media(media_url) 
                #     self.msg.body(body)

                i = redis_client.get('i')
                if i == None:
                    i = 0
                    for catalogue in user_catalogue_redis:
                        media_url = self.show_catalogue(catalogue['catalogue_image'])
                        print(media_url)
                        if catalogue['currency'] == None:
                            currency = 'EUR'
                        else:
                            currency = catalogue['currency']

                        type = chr(ord('a') + i).upper()
                        body = '\n\n' + type + ': price per day ' + self.convert_currency_symbol(str(currency)) + str(catalogue['price']) + '\n'
                        i = i + 1
                        redis_client.set('i', i)
                        self.msg.media(media_url) 
                        question = '\nDo you want to book this property? \n[reply ' + type + ']\n'
                        more = '\nIf you want to see more properties? \n[reply #]\n'
                        break
                else:
                    j = 0
                    i = json.loads(redis_client.get('i').decode('utf-8'))
                    print(i)
                    if j <= i:
                        for catalogue in user_catalogue_redis:
                            if j == i:
                                media_url = self.show_catalogue(catalogue['catalogue_image'])
                                print(media_url)
                                if catalogue['currency'] == None:
                                    currency = 'EUR'
                                else:
                                    currency = catalogue['currency']

                                type = chr(ord('a') + i).upper()
                                body = '\n\n' + type + ': price per day ' + self.convert_currency_symbol(str(currency)) + str(catalogue['price']) + '\n'

                                self.msg.media(media_url) 
                                question = '\nDo you want to book this property? \n[reply ' + type + ']\n'
                                more = '\nIf you want to see more properties? \n[reply #]\n'
                                redis_client.set('i', (j + 1))
                                break
                            j = j + 1       
                        else:
                            body = '\nSorry right now no more property available. Kindly select from above list.\n[reply eg. a or b or c ...]\n'                 
                        
            else:
                body = '\n\nKindly start from beginning'
                self.msg.body(body)

            self.msg.body(body + question + more)
            
            self.responded = True
        elif self.incoming_msg in self.cl:
            steps = redis_client.get('steps')
            if int(steps) < 3:
                redis_client.set('steps', 3)
                steps = redis_client.get('steps')

            if int(steps) == 3:
                room_type_redis = redis_client.get('room_type_redis')
                if room_type_redis == None:
                    redis_client.set('room_type_redis', self.incoming_msg)
                    room_type_redis = redis_client.get('room_type_redis')

                # now = datetime.datetime.now()
                # cal = calendar.TextCalendar()
                # current_cal = cal.formatmonth(now.year, now.month)

                body = 'What is expected Check-in date? [format: dd/mm/yyyy] eg. 10/01/2021 \n\nFor your reference \n'
            else:
                body = "\nKindly start from the beginning"

            # phone_number_encrypted_redis = redis_client.get('phone_number_encrypted_redis')
            self.msg.body(body)
            # media_url = request.host_url.strip("/")
            # media_url = media_url.replace('http:', 'https:') + url_for("api.date_selector", phone_number_encrypted=str(phone_number_encrypted_redis.decode('utf-8')))
            # print(media_url)
            # self.msg.media(media_url)
            self.responded = True
        elif self.matched:
            body = None
            steps = redis_client.get('steps')
            if int(steps) < 4:
                redis_client.set('steps', 4)
                steps = redis_client.get('steps')

            if int(steps) == 4:
                check_in_date_redis = redis_client.get('check_in_date_redis')
                if check_in_date_redis == None and self.matched != None:
                    check_in_date_redis = redis_client.set('check_in_date_redis', self.matched.group() + ' 00:00:00')
                    check_in_date_redis = redis_client.get('check_in_date_redis').decode('utf-8')
                    check_in_date_redis_dt = datetime.datetime.strptime(check_in_date_redis, "%d/%m/%Y %H:%M:%S")
                    dt = datetime.datetime.combine(datetime.date.today(), datetime.datetime.min.time())
                    if check_in_date_redis_dt >= dt:
                        body = 'From ' + self.matched.group() + ', how many days would you like to stay? eg. 3'
                    else:
                        body = '\n Wrong date. Must be greater than today.'
            else:
                body = '\nKindly start from the beginning'

            self.msg.body(body)
            self.responded = True
        elif self.incoming_msg in self.ans:
            body = None
            steps = redis_client.get('steps')
            if int(steps) < 5:
                redis_client.set('steps', 5)
                steps = redis_client.get('steps')

            if int(steps) == 5:
                check_in_date_redis = redis_client.get('check_in_date_redis').decode('utf-8')
                check_in_date_redis_dt = datetime.datetime.strptime(check_in_date_redis, "%d/%m/%Y %H:%M:%S")
                check_out_date = (check_in_date_redis_dt + datetime.timedelta(days=int(self.incoming_msg)))
                redis_client.set('check_out_date_redis', str(check_out_date))

                holigest = Holigest()
                payload = {
                        "idAlloggio":5,
                        "dataDal":check_in_date_redis_dt,
                        "dataAl":check_out_date,
                        "consideraChiusi": 2
                    }
                # print(check_in_date_redis_dt)
                # print(check_out_date)
                holiget_response_redis_reservation_list = redis_client.get('holiget_response_redis')
                if holiget_response_redis_reservation_list == None:
                    holiget_response = str(holigest.reservation_list(payload))
                    # keep 10 min
                    redis_client.set('holiget_response_redis_reservation_list', holiget_response, 600)
                    # print(holiget_response)
                    # return redis_client.get('holiget_response_redis')
                    if holiget_response == '[]': 

                        room_type_redis = redis_client.get('room_type_redis').decode('utf-8')
                        room_type = None
                        if room_type_redis == 'a':
                            room_type = 'Sea Facing'
                        elif room_type_redis == 'b':
                            room_type = 'Hills Facing'
                        elif room_type_redis == 'c':
                            room_type = 'Family'

                        check_in_date_redis = redis_client.get('check_in_date_redis').decode('utf-8')
                        check_out_date_redis = redis_client.get('check_out_date_redis').decode('utf=8')
                        body = '\n\nCongratulation. Your room type ' + room_type + ' is booked \nfrom ' + str(check_in_date_redis) + ' to ' + str(check_out_date_redis) + '. \nThank you. Wish you a wonderful stay. \n\nYou can contact any time for OrderBot for your ' + 'business ' + 'https://bizhive.eu ' + 'ph/whatsapp: +917736865411'
                    else:
                        body = 'Sorry rooms are not available on your selected dates'
            else:
                body = '\nKindly start from beginning'
            
            self.msg.body(body)
            self.responded = True
        elif not self.responded and self.incoming_msg == '':
            self.msg.body('I only know about beautiful rooms in Sicily, sorry!')
        else:
            self.msg.body("This is not correct reply. Kindly try again.")
            self.responded = True
            
        return str(self.resp)

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