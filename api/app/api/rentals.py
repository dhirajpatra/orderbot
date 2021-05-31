
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

from .orderbot_twilio import OrderbotTwilio

from ..models import User_catalogue, db, User, Message, User_api_company, User_api_details, User_api_urls, User_catalogue
from . import api
from ..database import get_all, add_instance, delete_instance, edit_instance
from . import AlchemyEncoder

from .holigest import Holigest
# from chatterbot import ChatBot
# from chatterbot.trainers import ChatterBotCorpusTrainer


redis_url = os.getenv('REDISTOGO_URL', os.environ['REDIS_URL'])
redis_client = redis.from_url(redis_url)
print("redis client connected " + str(redis_client))


class Rentals():
    
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
    language = 'en'
    checked = False
    customer_details = None
    payment_method = None
    payment_methods = None
    open_street_map_url = None
    cache_time = 300

    def __init__(self) -> None:
        super().__init__()
        
        self.stop_words = ['i','me','my','myself','we','our','ours','ourselves','you','your','yours','yourself','yourselves','he','him','his','himself','she','her','hers','herself','it','its','itself','they','them','their','theirs','themselves','what','which','who','whom','this','that','these','those','am','is','are','was','were','be','been','being','have','has','had','having','do','does','did','doing','a','an','the','and','but','if','or','because','as','until','while','of','at','by','for','with','about','against','between','into','through','during','before','after','above','below','to','from','up','down','in','out','on','off','over','under','again','further','then','once','here','there','when','where','why','how','all','any','both','each','few','more','most','other','some','such','no','nor','not','only','own','same','so','than','too','very','s','t','can','will','just','don','should','now','id', 'var',
        'function', 'js', 'd', 'script', '\'script', 'fjs', 'document', '\'s']
        
        # need to send sid and token as per business account / client account
        account_sid = os.environ['TWILIO_ACCOUNT_SID']
        auth_token = os.environ['TWILIO_AUTH_TOKEN']

        self.msg = OrderbotTwilio(account_sid, auth_token)
        self.msg.respond(False)
        
        self.ans = [str(int) for int in list(range(1, 100))]
        self.types = ['room', 'holiday', 'villa', 'accommodation', 'tour', 'hire', 'sicily', 'sea', 'beaches']
        self.first_msg = ['hi', 'hoi', 'help', 'support', 'how']
        if self.holigest == None:
            self.holigest = Holigest()
        self.checked = False
        self.payment_methods = {'A':'Crypto', 'B': 'Paypal'}
        

    def hook(self, user, request):
        request_body = request.values.get('Body', '').lower()  
        if request.values.get('From', '') == None or request.values.get('From', '') == '':
            # for testing from rest api client
            # end user's phone number
            self.from_phone_number = '+917893273022' + '_' + user['phone_number_encrypted']
            # business's phone number
            self.to_phone_number = '+917893273022'
        else:
            self.from_phone_number = request.values.get('From', '').split(':')
            self.from_phone_number = self.from_phone_number[1] + '_' + user['phone_number_encrypted']
            self.to_phone_number = request.values.get('To', '').split(':')
            self.to_phone_number = self.to_phone_number[1]

        self.incoming_msg = request_body
        print(self.from_phone_number)
        print('incoming msg')
        print(self.incoming_msg)

        # save msg
        self.save_message(user['id'], str(self.from_phone_number[1]), self.incoming_msg)

        try:
            # check in date matching   
            self.matched = re.search(r'(\d{1,2}/\d{1,2}/\d{4})', self.incoming_msg)
            
            # how many person 
            result_person = re.search(r'(\d{1,2})', self.incoming_msg)
            if result_person:
                self.person = result_person.group(0)

            self.result = filter(lambda x: self.incoming_msg.find(x) != -1, self.types)

            self.open_street_map_url = "https://www.openstreetmap.org/#map="

            # check the cache for this user to maintain a session like process
            self.sender_redis = redis_client.get(self.from_phone_number)
            # print(self.sender_redis)
            # first or start from the beginning 
            if self.sender_redis == None or [ele for ele in self.first_msg if(ele == self.incoming_msg)]:
                self.sender_redis_payload = {
                    'language': self.language,
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
                redis_client.set(self.from_phone_number, self.sender_redis_payload, 120)
                self.sender_redis = json.loads(redis_client.get(self.from_phone_number))
                self.steps = 0
            else:
                self.sender_redis = json.loads(redis_client.get(self.from_phone_number))
                self.steps = self.sender_redis['steps']
            print('steps ' + str(self.steps))

            # payment
            if len(self.incoming_msg) == 1 and int(self.steps) == 7:
                check = re.search('[a-zA-Z]?', self.incoming_msg)
                if check.group(0) != '':
                    self.checked = True

            # make the selction of property
            if len(self.incoming_msg) == 1 and int(self.steps) == 5:
                check = re.search('[a-zA-Z]?', self.incoming_msg)
                if check.group(0) != '':
            
                    if (97 + int(self.sender_redis['i']) - 1) < ord(self.incoming_msg.lower()):
                        self.save_message(user['id'], str(self.from_phone_number[1]), "\n 🚫 Worng answer, kindly send <b>only 0 to see more</b> or <b>single alphabet character to select eg. a or b</b>")
                        self.bot.body(self.chat_id, "\n 🚫 " + self.language_conversion.translate('en', self.language,"Wrong answer, kindly send <b>only 0 to see more</b> or <b>single alphabet character to select eg. a or b</b>"), self.message_id)
                        return "ok"
                    else:
                        self.checked = True
                elif int(self.incoming_msg) != 0:
                        self.save_message(user['id'], str(self.from_phone_number[1]), "\n 🚫 Worng answer, kindly send <b>only 0 to see more</b> or <b>single alphabet character to select eg. a or b</b>")
                        self.bot.body(self.chat_id, "\n 🚫 " + self.language_conversion.translate('en', self.language,"Wrong answer, kindly send <b>only 0 to see more</b> or <b>single alphabet character to select eg. a or b</b>"), self.message_id)
                        return "ok"
        
            # get the customer details
            elif int(self.steps) == 6:
                self.incoming_msg = self.incoming_msg.replace(" ", "")
                result  = re.search(r'\w*,\w*,[\w.-]+@[\w.-]+', self.incoming_msg)
                if result != None and result.group() == self.incoming_msg:
                    self.customer_details = self.incoming_msg.split(',')
                else:
                    self.save_message(user['id'], str(self.from_phone_number[1]), "\n 🏁 <b>Wrong email, kindly send the details again in first_name,last_name,email format</b>")
                    self.bot.body(self.chat_id, "\n 🏁 <b>" + self.language_conversion.translate('en', self.language, "Wrong email, kindly send the details again in first_name,last_name,email format</b>"), self.message_id)

            # select payment method
            elif len(self.incoming_msg) == 1 and int(self.steps) == 7:
                check = re.search('[a-zA-Z]?', self.incoming_msg)
                if check.group(0) != '':
                    self.payment_method = self.payment_methods[self.incoming_msg.upper()]

            # verify the current input and give user a chance to fix
            elif int(self.steps) == 2 and self.matched == None:
                # save msg
                self.save_message(user['id'], str(self.from_phone_number[1]), "\n 🚫 Wrong date or format, kindly send checkin date in <b>dd/mm/yyyy</b> format only")
                self.bot.body(self.chat_id, "\n 🚫 " + self.language_conversion.translate('en', self.language, "Wrong date or format, kindly send checkin date in <b>dd/mm/yyyy</b> format only"), self.message_id)
                return "ok"
            # person can be 1 or more
            elif ((int(self.steps) == 3 or int(self.steps) == 4) and self.incoming_msg not in self.ans):
                self.save_message(user['id'], str(self.from_phone_number[1]), "\n 🚫 Wrong number, kindly send <b>only number eg. 5</b>")
                self.bot.body(self.chat_id, "\n 🚫 " + self.language_conversion.translate('en', self.language, "Wrong number, kindly send <b>only number eg. 5</b>"), self.message_id)
                return "ok"
            # # child can be 0 or more
            # elif (int(self.steps) == 4 and not self.incoming_msg.isdigit()):
            #     self.bot.body(self.chat_id, "\n 🚫 Wrong number, kindly send *only number eg. 0 or more*", self.message_id)
            #     return "ok"

            # elif int(self.steps) == 5 and (int(self.incoming_msg) != 0 or self.checked != True):
            #     self.bot.body(self.chat_id, "\n 🚫 Worng answer, kindly send *only 0 to see more* or *single alphabet character to select eg. a or b*", self.message_id)
            #     return "ok"
                    
        except:
            self.save_message(user['id'], str(self.from_phone_number[1]), "\n 🏁 <b>Kindly start from the beginning. You can start with say 'hi'</b>")
            self.msg.body("\n 🏁 *" + self.language_conversion.translate('en', self.language, "Kindly start from the beginning. You can start with say 'hi'") + "*")
            self.msg.respond(True)

        

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
        
        if [ele for ele in self.first_msg if(ele == self.incoming_msg.lower())] and int(self.steps) == 0:
            self.steps = int(self.steps) + 1

            body = "Kindly select your language:\nA: 🇬🇧 English\nB: 🇮🇹 Italian"
            
            self.save_message(user['id'], str(self.from_phone_number[1]), body)
            self.bot.body(self.chat_id, body, self.message_id)

            # update the redis cache for this customer/sender
            self.sender_redis_payload = {
                'language': self.language,
                'steps': self.steps, 
                'last_incoming_msg':self.incoming_msg,
                'last_reply': body,
                'check_in_date': '',
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

        elif int(self.sender_redis['steps']) == 1:
            body1 = None
            body2 = None
            body3 = None
            calendar_path = None
            
            body1 = '🇮🇹 🏘️ ' + user['welcome_msg'].replace("\\n", " ")
            now = datetime.datetime.now()
            # current_cal = calendar.calendar(now.year)
            # current_cal = calendar.month(now.year, now.month)
            calendar_path = request.host_url.strip("/") + url_for('static', filename='images/'+ str(now.year) + '_calendar.jpg')
            room_type_redis = redis_client.get('room_type_redis')
            if room_type_redis == None:
                redis_client.set('room_type_redis', self.incoming_msg, 120)
                room_type_redis = redis_client.get('room_type_redis')

                body2 = '\n _' + self.language_conversion.translate('en', self.language, 'For reference') + '_ \n'
                body3 = '\n *' + self.language_conversion.translate('en', self.language, 'What is your expected') + ' 🛬 ' + self.language_conversion.translate('en', self.language, 'Check-in date?') + '* [' + self.language_conversion.translate('en', self.language, 'format') + ': *dd/mm/yyyy*] ' + self.language_conversion.translate('en', self.language, 'eg.') + ' 10/01/2021\n'
            else:
                body2 = '\n _' + self.language_conversion.translate('en', self.language, 'For reference') + '_ \n'
                body3 = '\n *' + self.language_conversion.translate('en', self.language, 'What is your expected') + ' 🛬 ' + self.language_conversion.translate('en', self.language, 'Check-in date?') + '* [' + self.language_conversion.translate('en', self.language, 'format') + ': *dd/mm/yyyy*] ' + self.language_conversion.translate('en', self.language, 'eg.') + ' 10/01/2021\n'
            
            self.save_message(user['id'], str(self.from_phone_number[1]), "https://cdn.pixabay.com/photo/2020/10/02/10/39/calendar-5620762_1280.png")
            self.msg.media(calendar_path)
            self.save_message(user['id'], str(self.from_phone_number[1]), body1+body2+body3)
            self.msg.body(body1 + body2 + body3)

            # update the redis cache for this customer/sender
            self.sender_redis_payload = {
                'language': self.language,
                'steps': 1, 
                'last_incoming_msg':self.incoming_msg,
                'last_reply': body3,
                'check_in_date':'',
                'check_out_date': '',
                'check_in_date_redis_dt':'',
                'check_out_date_redis_dt':'',
                'persons': 0,
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
            redis_client.set(self.from_phone_number, self.sender_redis_payload, 120)
            
            # self.resp.append(self.msg)
            self.msg.respond(True)

        elif self.matched and int(self.steps) == 2:
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
                        body = self.language_conversion.translate('en', self.sender_redis['language'], 'From') + ' ' + self.matched.group() + ', 🛫 *' + self.language_conversion.translate('en', self.sender_redis['language'], 'how many days would you like to stay?') + '* [' + self.language_conversion.translate('en', self.sender_redis['language'], 'reply only number eg. 7') + ']'
                    else:
                        self.steps = int(self.steps) - 1
                        check_in_date_redis = ''
                        body = '\n 🙁 *' + self.language_conversion.translate('en', self.sender_redis['language'], 'Wrong date. Must be greater than today.') + '*'
            else:
                body = '\n 💡 *' + self.language_conversion.translate('en', self.sender_redis['language'], 'Kindly start from the beginning') + '*'

            self.save_message(user['id'], str(self.from_phone_number[1]), body)
            self.msg.body(body)

            # update the redis cache for this customer/sender
            self.sender_redis_payload = {
                'language': self.sender_redis['language'],
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
            redis_client.set(self.from_phone_number, self.sender_redis_payload, 120)

            self.msg.respond(True)

        elif self.incoming_msg in self.ans and self.sender_redis['check_in_date'] != '' and int(self.steps) == 3:
            body = ''
            self.steps = int(self.steps) + 1

            if int(self.steps) == 4:
                check_in_date_redis = self.sender_redis['check_in_date']
                check_in_date_redis_dt = datetime.datetime.strptime(check_in_date_redis, "%d/%m/%Y %H:%M:%S")
                check_out_date = (check_in_date_redis_dt + datetime.timedelta(days=(int(self.incoming_msg))))

                body = "\n 👨‍👨‍👦‍👦 *" + self.language_conversion.translate('en', self.sender_redis['language'], "How many persons [adults and children, please exclude babies] will stay?") + "* \n[" + self.language_conversion.translate('en', self.sender_redis['language'], "reply only number eg. 9") + "]\n"
                self.save_message(user['id'], str(self.from_phone_number[1]), body)
                self.msg.body(body)

                # update the redis cache for this customer/sender
                sender_redis_payload = {
                    'language': self.sender_redis['language'],
                    'phone_number': self.from_phone_number, 
                    'steps': self.steps, 
                    'last_incoming_msg':self.incoming_msg,
                    'last_reply': body,
                    'check_in_date': str(check_in_date_redis),
                    'check_out_date': str(check_out_date),
                    'check_in_date_redis_dt': str(check_in_date_redis_dt),
                    'check_out_date_redis_dt': str(check_out_date),
                    'persons': 0,
                    'children': 0,
                    'days': int(self.incoming_msg),
                    'selected':'',
                    'total_price':0,
                    'matched_properties':'',
                    'i': 0,
                    'customer_details': '',
                    'customer_registration_details': '',
                    'customer_payment_details': '',
                    'last_update': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                sender_redis_payload = json.dumps(sender_redis_payload)
                redis_client.set(self.from_phone_number, sender_redis_payload, 240)
                
                self.msg.respond(True)

        # elif self.incoming_msg in self.ans and self.sender_redis['check_in_date'] != '' and int(self.steps) == 3:
        #     body = ''
        #     self.steps = int(self.steps) + 1

        #     check_in_date_redis = self.sender_redis['check_in_date']
        #     check_in_date_redis_dt = datetime.datetime.strptime(check_in_date_redis, "%d/%m/%Y %H:%M:%S")
        #     check_out_date = (check_in_date_redis_dt + datetime.timedelta(days=(int(self.incoming_msg))))

        #     body = "\n 👨‍👨‍👦‍👦 *How many children [below 12 yrs age] will stay?* \n[reply only number eg. 2]\n"

        #     self.bot.body(self.chat_id, body, self.message_id)

        #     # update the redis cache for this customer/sender
        #     sender_redis_payload = {
        #         'phone_number': self.from_phone_number, 
        #         'steps': self.steps, 
        #         'last_incoming_msg':self.incoming_msg,
        #         'last_reply': body,
        #         'check_in_date': str(check_in_date_redis),
        #         'check_out_date': str(check_out_date),
        #         'check_in_date_redis_dt': str(check_in_date_redis_dt),
        #         'check_out_date_redis_dt': str(check_out_date),
        #         'persons': int(self.incoming_msg),
        #         'children': 0,
        #         'days': self.sender_redis['days'],
        #         'selected':'',
        #         'total_price':0,
        #         'matched_properties':'',
        #         'i': 0,
        #         'customer_details': '',
        #         'customer_registration_details': '',
        #         'customer_payment_details': '',
        #         'last_update': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        #         }
        #     sender_redis_payload = json.dumps(sender_redis_payload)
        #     redis_client.set(self.from_phone_number, sender_redis_payload, self.cache_time)
                
        # #         self.bot.respond(True)

        # first property
        elif self.incoming_msg in self.ans and self.sender_redis['check_in_date'] != '' and self.sender_redis['days'] != 0 and int(self.steps) == 4:
            body = None
            link = None
            response = None
            self.steps = int(self.steps) + 1
            i = self.sender_redis['i']    
            check_in_date_redis = self.sender_redis['check_in_date_redis_dt']
            check_out_date_redis = self.sender_redis['check_out_date_redis_dt']
            matched_properties = []

            # call API PRELEVA LISTA ALLOGGI
            payload = {
                "filtro":"",
                "filtro_dotazioni":"",
                "filtro_dotazioniTipo":"0",
                "filtro_tipiAlloggi":"",
                "filtro_numeroCamere":"0",
                "filtro_nomeAlloggio":"",
                "filtro_persone": str(self.incoming_msg),
                "filtro_personeTipoCalcolo":"1",
                "filtro_numeroBagni":"0",
                "filtro_inPrimoPiano":"0",
                "filtro_idGruppo":"0",
                "filtro_idCategoria":"0",
                "idAlloggio":"0", # need to provide id if want details of a specific property
                "zonaGeografica_tipo":"0",
                "zonaGeografica_id":[],
                "lingua": self.sender_redis['language'],
                "LimitStart":"0",
                "LimitEnd":"100",
                "checkDisp_CI": check_in_date_redis[:10],
                "checkDisp_CO": check_out_date_redis[:10],
                "checkDisp_PERSONE":"0",
                "checkDisp_PERSONETIPORICERCA":"1",
                "checkDisp_Errori":"1",
                "checkDisp_FORZAVISUALIZZAZIONE":"False",
                "checkDisp_PERIODICHIUSI":"1",
                "mostraSoltantoVisibiliSuSitoWeb":"True",
                "nascondiNonPrenotabiliSuSitoWeb":"False",
                "orderListaAlloggi":"ordine_visualizzazione",
                "loadFotoPrincipale":"True",
                "loadPrezzoAlGiorno":"True",
                "rangePrezzoFrom":"0",
                "rangePrezzoTo":"0",
                "rangePrezzoOrder":"0",
                "calcolaDisponibilitaAlloggioRappresentanza":"False",
                "idTariffa":"",
                "nomeTariffa":"",
                "dettaglio_prezzo":"",
                "totale":"",
                "totale_netto":"",
                "totale_prezzoFinito":"",
                "totale_netto_conSconto":"",
                "sconto":"",
                "nomePromo":"",
                "totale_sovrapprezzo_persone":"",
                "percCaparra":""
            }
            response = self.holigest.get_list_of_accomodations(payload)
            response = json.loads(response)
            
            # business user catalogue this also need for specific business user data
            user_catalogue_redis = redis_client.get('user_catalogue_redis')
            if user_catalogue_redis == None:
                user_catalogue = User_catalogue.query.filter_by(user_id=user['id']).all()
                redis_client.set('user_catalogue_redis', json.dumps(user_catalogue, cls=AlchemyEncoder), 120)
                user_catalogue_redis = json.loads(redis_client.get('user_catalogue_redis').decode('utf-8'))
            else:
                user_catalogue_redis = json.loads(redis_client.get('user_catalogue_redis').decode('utf-8'))
            # print(user_catalogue_redis)
            # print(check_in_date_redis)
            # print(check_out_date_redis)
            matched_properties = response
            # print(matched_properties)
            # for property in response:
            #     matched_properties.append({'id': property['id'], 'titolo': property['titolo'], 'descrizioneRidotta': property['descrizioneRidotta']})
            # print('count ')
            count = len(matched_properties)
            # print(count)
            # get the catalogue
            for property in response:
                body = '\n *' + property['titolo'] + '* \n' + property['descrizioneRidotta'] + ' ' + property['localita'] + '\n'

                # call LISTA PRENOTAZIONI
                payload_list_prenotazioni = {
                    "idAlloggio": int(property['id']),
                    "dataDal": str(check_in_date_redis),
                    "dataAl": str(check_out_date_redis),
                    "consideraChiusi": 2
                }
                response_lista = self.holigest.reservation_list(payload_list_prenotazioni)
                response_lista = json.loads(response_lista)
                
                # if that property available for that specific dates and persons
                if response_lista == []:
                    for cat in user_catalogue_redis:
                        if cat['property_id'] == int(property['id']):
                            # print(property)  
                            # call PRELEVA TARIFFE ALLOGGI
                            payload_preleva_tariffe_alloggi = {
                                "idAlloggio": int(property['id']),
                                "lingua": self.language,
                                "dataDal": str(check_in_date_redis),
                                "dataAl": int(self.sender_redis['days'])
                            }
                            response_preleva_tariffe_alloggi = self.holigest.collect_accomodation_rate(payload_preleva_tariffe_alloggi)
                            response_preleva_tariffe_alloggi = json.loads(response_preleva_tariffe_alloggi)
                                
                            if response_preleva_tariffe_alloggi != []:
                                # process check_in and check_out date range is in the response then find the pricess if in different date zone
                                prices = self.get_tariff_date_range(check_in_date_redis, check_out_date_redis, response_preleva_tariffe_alloggi) 
                                weekly_price_str = ''
                                weekly_price = 0
                                # get weekly price
                                if self.sender_redis['days'] <= 7:
                                    weekly_price = self.get_weekly_tariff_date_range(check_in_date_redis, check_out_date_redis, response_preleva_tariffe_alloggi)
                                elif self.sender_redis['days'] > 7:
                                    additional_days_week = self.sender_redis['days'] - 7
                                    weekly_price = self.get_weekly_tariff_date_range(check_in_date_redis, check_out_date_redis, response_preleva_tariffe_alloggi)
                                    each_day_price_as_week = int(weekly_price) / 7
                                    weekly_price = int(weekly_price) + (additional_days_week * each_day_price_as_week)

                                weekly_price_str = '\n *' + self.language_conversion.translate('en', self.sender_redis['language'], 'Weekly price') + ' ' + self.convert_currency_symbol('EUR') + str("{:.2f}".format(int(weekly_price))) + '* '
                                
                                # image for the property
                                # link = request.host_url.strip("/") + url_for('static', filename='images/'+ cat['catalogue_image'])
                                link = property['fotoPrincipale500']   
                                rooms = int(property['cameresingole']) + int(property['camerematrimoniali']) + int(property['cameredoppie']) + int(property['cameretriple']) + int(property['camerequadruple']) + int(property['camereStaff'])                             
                                body = '\n' + body + '\n 🛏️ *' + str(rooms)  + ' ' + self.language_conversion.translate('en', self.sender_redis['language'], 'rooms') + '* \n 🛀 *'+ str(property['bagnin']) +' ' + self.language_conversion.translate('en', self.sender_redis['language'], 'bath') + '* \n 🧑🏻‍🤝‍🧑🏻 *'+ str(property['personeideale']) +'/' + str(property['personemax']) + ' ' + self.language_conversion.translate('en', self.sender_redis['language'], 'Min/Max Guests') + '* \n\n 🎞️ *' + self.language_conversion.translate('en', self.sender_redis['language'], 'For more details* kindly click') + ' ' + str(cat['link']) +'\n 🏘️ ' + str(cat['property_name']) + '\n 💶 *' + self.language_conversion.translate('en', self.sender_redis['language'], 'Price per night') + ' ' + self.convert_currency_symbol('EUR') + str("{:.2f}".format(float(prices))) + '*' + weekly_price_str  + '\n' + self.language_conversion.translate('en', self.sender_redis['language'], 'You will get') + ' *' + property['CK_nomepromo'] + '* \n'

                                self.save_message(user['id'], str(self.from_phone_number[1]), link)
                                self.msg.media(link)
                                tbody = body + '\n 👉 *' + self.language_conversion.translate('en', self.sender_redis['language'], 'Do you want to book this property?') + '* \n[' + self.language_conversion.translate('en', self.sender_redis['language'], 'reply') + ' *' + chr(65 + i) + '*]\n'
                                if i < count:
                                    tbody = tbody + '\n 🤏 *' + self.language_conversion.translate('en', self.sender_redis['language'], 'If you want to see more properties?') + '* \n[' + self.language_conversion.translate('en', self.sender_redis['language'], 'reply') + ' *0*]\n'
                                else:
                                    tbody = tbody + '\n 🙋‍♀️ *' + self.language_conversion.translate('en', self.sender_redis['language'], 'Sorry right now no more property available as per your search.') + '\n' + self.language_conversion.translate('en', self.sender_redis['language'], 'To make a selection') + ' 👇 ' + self.language_conversion.translate('en', self.sender_redis['language'], 'Kindly reply') + ' 👉 a or A* \n'
                                self.save_message(user['id'], str(self.from_phone_number[1]), tbody)
                                self.msg.body(tbody)

                    break
            
            # update the redis cache for this customer/sender
            sender_redis_payload = {
                'language': self.sender_redis['language'],
                'phone_number': self.from_phone_number, 
                'steps': self.steps, 
                'last_incoming_msg':self.incoming_msg,
                'last_reply': body,
                'check_in_date': self.sender_redis['check_in_date'],
                'check_out_date': self.sender_redis['check_out_date'],
                'check_in_date_redis_dt': self.sender_redis['check_in_date_redis_dt'],
                'check_out_date_redis_dt': self.sender_redis['check_out_date'],
                'persons': self.sender_redis['persons'],
                'children': int(self.incoming_msg),
                'days': self.sender_redis['days'],
                'selected':'',
                'total_price':0,
                'i': i + 1,
                'customer_details': '',
                'customer_registration_details': '',
                'customer_payment_details': '',
                'matched_properties': matched_properties,
                'last_update': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            
            sender_redis_payload = json.dumps(sender_redis_payload)
            redis_client.set(self.from_phone_number, sender_redis_payload, 240)

            # self.resp.append(self.msg)
            self.msg.respond(True)

        elif self.incoming_msg == '0' and int(self.steps) == 5:
            body = ''
            response = self.sender_redis['matched_properties']
            # fetch all catalogue and keep in redis
            i = self.sender_redis['i']
            print('i '+str(i))  

            check_in_date_redis = self.sender_redis['check_in_date_redis_dt']
            check_out_date_redis = self.sender_redis['check_out_date_redis_dt']
            
            # business user catalogue this also need for specific business user data
            user_catalogue_redis = redis_client.get('user_catalogue_redis')
            if user_catalogue_redis == None:
                user_catalogue = User_catalogue.query.filter_by(user_id=user['id']).all()
                redis_client.set('user_catalogue_redis', json.dumps(user_catalogue, cls=AlchemyEncoder), 120)
                user_catalogue_redis = json.loads(redis_client.get('user_catalogue_redis').decode('utf-8'))
            else:
                user_catalogue_redis = json.loads(redis_client.get('user_catalogue_redis').decode('utf-8'))
            # print(user_catalogue_redis)
            # print(check_in_date_redis)
            # print(check_out_date_redis)
            # print(response)
            # get the catalogue
            if user_catalogue_redis != None and response != '':
                count = len(response)
                print('count ' + str(count))
                if i < count:
                    j = 0
                    for property in response:
                        print('j '+str(j))
                        if j == i:
                            body = '\n' + property['titolo'] + '\n' + property['descrizioneRidotta'] + ' ' + property['localita'] + '\n'
                            # print(property)
                            # call LISTA PRENOTAZIONI
                            payload_list_prenotazioni = {
                                "idAlloggio": int(property['id']),
                                "dataDal": str(check_in_date_redis),
                                "dataAl": str(check_out_date_redis),
                                "consideraChiusi": 2
                            }
                            response_lista = self.holigest.reservation_list(payload_list_prenotazioni)
                            response_lista = json.loads(response_lista)
                            print(response_lista)
                            # if that property available for that specific dates and persons
                            if response_lista == []:
                                for cat in user_catalogue_redis:
                                    if cat['property_id'] == int(property['id']):
                                        # call PRELEVA TARIFFE ALLOGGI
                                        payload_preleva_tariffe_alloggi = {
                                            "idAlloggio": int(property['id']),
                                            "lingua": self.language,
                                            "dataDal": str(check_in_date_redis),
                                            "dataAl":""
                                        }
                                        response_preleva_tariffe_alloggi = self.holigest.collect_accomodation_rate(payload_preleva_tariffe_alloggi)
                                        response_preleva_tariffe_alloggi = json.loads(response_preleva_tariffe_alloggi)
                                            
                                        if response_preleva_tariffe_alloggi != []:
                                            # process check_in and check_out date range is in the response then find the pricess if in different zones
                                            prices = self.get_tariff_date_range(check_in_date_redis, check_out_date_redis, response_preleva_tariffe_alloggi) 
                                            weekly_price_str = ''
                                            weekly_price = 0
                                            # get weekly price
                                            if self.sender_redis['days'] <= 7:
                                                weekly_price = self.get_weekly_tariff_date_range(check_in_date_redis, check_out_date_redis, response_preleva_tariffe_alloggi)
                                            elif self.sender_redis['days'] > 7:
                                                additional_days_week = self.sender_redis['days'] - 7
                                                weekly_price = self.get_weekly_tariff_date_range(check_in_date_redis, check_out_date_redis, response_preleva_tariffe_alloggi)
                                                each_day_price_as_week = weekly_price / 7
                                                weekly_price = weekly_price + (additional_days_week * each_day_price_as_week)
                                                
                                            weekly_price_str = '\n *' + self.language_conversion.translate('en', self.sender_redis['language'], 'Weekly price') + ' ' + self.convert_currency_symbol('EUR') + str("{:.2f}".format(int(weekly_price))) + '* '
                                            
                                            # image for the property
                                            # link = request.host_url.strip("/") + url_for('static', filename='images/'+ cat['catalogue_image'])   
                                            link = property['fotoPrincipale500']   
                                            rooms = int(property['cameresingole']) + int(property['camerematrimoniali']) + int(property['cameredoppie']) + int(property['cameretriple']) + int(property['camerequadruple']) + int(property['camereStaff'])                           
                                            body = '\n' + body + '\n 🛏️ *' + str(rooms)  + ' ' + self.language_conversion.translate('en', self.sender_redis['language'], 'rooms') + '* \n 🛀 *'+ str(property['bagnin']) +' ' + self.language_conversion.translate('en', self.sender_redis['language'], 'bath') + '* \n 🧑🏻‍🤝‍🧑🏻 *'+ str(property['personeideale']) +'/' + str(property['personemax']) + ' ' + self.language_conversion.translate('en', self.sender_redis['language'], 'Min/Max Guests') + '* \n\n 🎞️ *' + self.language_conversion.translate('en', self.sender_redis['language'], 'For more details') + '* ' + self.language_conversion.translate('en', self.sender_redis['language'], 'kindly click') + ' ' + str(cat['link']) +'\n 🏘️ ' + str(property['nome']) + '\n 💶 *' + self.language_conversion.translate('en', self.sender_redis['language'], 'Price per night') + ' ' + self.convert_currency_symbol('EUR') + str("{:.2f}".format(float(prices))) + '*' + weekly_price_str  + '\n' + self.language_conversion.translate('en', self.sender_redis['language'], 'You will get') + ' *' + property['CK_nomepromo'] + '* \n'

                                            self.save_message(user['id'], str(self.from_phone_number[1]), link)
                                            self.msg.media(link)
                                            self.save_message(user['id'], str(self.from_phone_number[1]), body + '\n 👉 *' + self.language_conversion.translate('en', self.sender_redis['language'], 'Do you want to book this property?') + '* \n[' + self.language_conversion.translate('en', self.sender_redis['language'], 'reply') + ' *' + chr(65 + i) + '*]\n' + '\n 🤏 *' + self.language_conversion.translate('en', self.sender_redis['language'], 'If you want to see more properties?') + '* \n[' + self.language_conversion.translate('en', self.sender_redis['language'], 'reply') + ' *0*]\n')
                                            self.msg.body(body + '\n 👉 *' + self.language_conversion.translate('en', self.sender_redis['language'], 'Do you want to book this property?') + '* \n[' + self.language_conversion.translate('en', self.sender_redis['language'], 'reply') + ' *' + chr(65 + i) + '*]\n' + '\n 🤏 *' + self.language_conversion.translate('en', self.sender_redis['language'], 'If you want to see more properties?') + '* \n[' + self.language_conversion.translate('en', self.sender_redis['language'], 'reply') + ' *0*]\n')

                                            break
                            else:
                                body = '\n 🙋‍♀️ *' + self.language_conversion.translate('en', self.sender_redis['language'], 'Sorry right now no more property available as per your search.') + '\n' + self.language_conversion.translate('en', self.sender_redis['language'], 'To make a selection') + ' 👇 ' + self.language_conversion.translate('en', self.sender_redis['language'], 'Kindly select from above list.') + '\n[' + self.language_conversion.translate('en', self.sender_redis['language'], 'reply') + ' 👉 ' + self.language_conversion.translate('en', self.sender_redis['language'], 'eg.') + ' a or b or c ...]* \n'
                                self.save_message(user['id'], str(self.from_phone_number[1]), body)
                                self.msg.body(body) 
                        j = j + 1

                else:
                    body = '\n 🙋‍♀️ *' + self.language_conversion.translate('en', self.sender_redis['language'], 'Sorry right now no more property available as per your search.') + '\n' + self.language_conversion.translate('en', self.sender_redis['language'], 'To make a selection') + ' 👇 ' + self.language_conversion.translate('en', self.sender_redis['language'], 'Kindly select from above list.') + '\n[' + self.language_conversion.translate('en', self.sender_redis['language'], 'reply') + ' 👉 ' + self.language_conversion.translate('en', self.sender_redis['language'], 'eg.') + ' a or b or c ...]* \n'
                    self.save_message(user['id'], str(self.from_phone_number[1]), body)
                    self.msg.body(body) 
            else:
                body = "\n 🏁 *" + self.language_conversion.translate('en', self.sender_redis['language'], "Kindly start from the beginning. Type Support to view the Mobile Services menu. You can start with say 'hi'") + "* \n" 
                self.save_message(user['id'], str(self.from_phone_number[1]), body)
                self.msg.body(body)   
            
            # update the redis cache for this customer/sender
            sender_redis_payload = {
                'language': self.sender_redis['language'],
                'phone_number': self.from_phone_number, 
                'steps': self.steps, 
                'last_incoming_msg':self.incoming_msg,
                'last_reply': body,
                'check_in_date': self.sender_redis['check_in_date'],
                'check_out_date': self.sender_redis['check_out_date'],
                'check_in_date_redis_dt': self.sender_redis['check_in_date_redis_dt'],
                'check_out_date_redis_dt': self.sender_redis['check_out_date'],
                'persons': self.sender_redis['persons'],
                'children': self.sender_redis['children'],
                'days': self.sender_redis['days'],
                'selected':'',
                'total_price':0,
                'i': i + 1,
                'customer_details': '',
                'customer_registration_details': '',
                'customer_payment_details': '',
                'matched_properties': self.sender_redis['matched_properties'],
                'last_update': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            
            sender_redis_payload = json.dumps(sender_redis_payload)
            redis_client.set(self.from_phone_number, sender_redis_payload, 120)

            # self.resp.append(self.msg)
            self.msg.respond(True)

        elif int(self.steps) == 5 and self.checked:
            body = None
            self.steps = int(self.steps) + 1
            i = self.sender_redis['i']
            property_id = 0
            # calculate alphabet to int and then sub by 97 to get the value of matched property's index
            propery_index = ord(self.incoming_msg.upper()) - 65
            # matched result from holiget API
            matched_properties = self.sender_redis['matched_properties']
            # this business user have these propertise saved into orderbot database
            user_catalogue_redis = json.loads(redis_client.get('user_catalogue_redis'))

            if user_catalogue_redis != None and matched_properties != '':
                count = len(matched_properties)

                j = 0
                for p in matched_properties:
                    if count >= j and j == propery_index:
                        self.save_message(user['id'], str(self.from_phone_number[1]), p['fotoPrincipale500']) 
                        self.msg.media(p['fotoPrincipale500'])
                        # self.msg.media(self.open_street_map_url + str(p['ordine_visualizzazione']) + '/' + str(p['coordinatelat']) + '/' + str(p['coordinatelon']))
                        details = '*' + p['titolo'] + '* \n' + '\n' + p['localita'] + ', ' + p['regione'] + '\n' + self.open_street_map_url + '14/' + str(p['coordinatelat']) + '/' + str(p['coordinatelon']) + '\n'

                        t = '\n\n 👍 *' + self.language_conversion.translate('en', self.sender_redis['language'], 'Congratulation you have selected this property') + '* \n 👉 ' + details + '\n'

                        #extra person calculation
                        extra_person = 0
                        extra_person_fee = 0
                        if self.sender_redis['persons'] > int(p['personeideale']):
                            extra_person = int(self.sender_redis['persons']) - int(p['personeideale'])
                            extra_person_fee = ((decimal.Decimal(p['personeSovrapprezzo']) / 100) * int(p['CK_prezzo'])) * int(extra_person)

                        # mandotory fees
                        cleaning_fee = 0
                        tourist_tax = 0                        
                        for m_fees in p['sovrapprezzi']:
                            if int(m_fees['id']) == 42: 
                                # it is cleaning fees
                                cleaning_fee = int(m_fees['prezzoCalcolato']) if int(m_fees['prezzoCalcolato']) != 0 else (int(m_fees['valore']) * int(m_fees['tipoCalcolo']))

                            if int(m_fees['id']) == 3: 
                                # it is tourist tax
                                tourist_tax = int(m_fees['prezzoCalcolato']) if int(m_fees['prezzoCalcolato']) != 0 else (int(m_fees['valore']) * int(self.sender_redis['persons']) * int(self.sender_redis['days']))

                        mandatory_fees = int(cleaning_fee) + int(tourist_tax)

                        if p['CK_prezzo_netto_conSconto'] < p['CK_prezzo_netto']:
                            net_price_after_discount = p['CK_prezzo_netto_conSconto'] + float(extra_person_fee)
                        else:
                            net_price_after_discount = p['CK_prezzo_netto'] + float(extra_person_fee)

                        total = (net_price_after_discount + float(mandatory_fees)) 
                        # if self.sender_redis['days'] >= 7 else int(net_price_after_discount + float(extra_person_fee) + float(mandatory_fees))
                        
                
                        # calcualte total and how many % will be deposite and balance
                        deposite =  total - (total * (int(p['percentualeCaparra']) / 100)) 
                        balance = total - deposite
                        
                        price = '\n *Price* \n' + ('-' * 45) + '\n *' + self.convert_currency_symbol('EUR') + ' ' + str("{:.2f}".format(total)) + '* \n' + self.language_conversion.translate('en', self.sender_redis['language'], 'standard') + '\n'
                        
                        reservation_details = '\n *' + self.language_conversion.translate('en', self.sender_redis['language'], 'Reservation details') + '* \n' + ('-' * 45) + '\n' + self.language_conversion.translate('en', self.sender_redis['language'], 'From') + ' ' + (' ' * 10) + self.sender_redis['check_in_date_redis_dt'][:10] + '\n' + self.language_conversion.translate('en', self.sender_redis['language'], 'To') + ' ' + (' ' * 10) + self.sender_redis['check_out_date_redis_dt'][:10] + '\n' + self.language_conversion.translate('en', self.sender_redis['language'], 'Nights') + ' ' + (' ' * 10) + str(self.sender_redis['days']) + '\n' + self.language_conversion.translate('en', self.sender_redis['language'], 'Adults') + ' ' + (' ' * 10) + str(self.sender_redis['persons']) + '\n' + self.language_conversion.translate('en', self.sender_redis['language'], 'Children') + ' ' + (' ' * 10) + '0'
                        
                        price_details = '\n\n *' + self.language_conversion.translate('en', self.sender_redis['language'], 'Total amount') + '*[_' + self.language_conversion.translate('en', self.sender_redis['language'], 'after discount and charges') + '_] \n' + ('-' * 45) + '\n' + self.language_conversion.translate('en', self.sender_redis['language'], 'Discounted Price') + ' ' + (' ' * 10) + self.convert_currency_symbol('EUR') + ' ' + str("{:.2f}".format(net_price_after_discount)) + ' (' + self.language_conversion.translate('en', self.sender_redis['language'], 'including Extra person charges') + ' '+ self.convert_currency_symbol('EUR') + ' ' + str("{:.2f}".format(extra_person_fee)) +')\n' + self.language_conversion.translate('en', self.sender_redis['language'], 'Mandatory services') + ' ' + (' ' * 10) + self.convert_currency_symbol('EUR') + ' ' + str("{:.2f}".format(mandatory_fees)) + ' (' + self.language_conversion.translate('en', self.sender_redis['language'], 'cleaning and tourist tax') + ')\n' + self.language_conversion.translate('en', self.sender_redis['language'], 'Optional services') + ' ' + self.convert_currency_symbol('EUR') + ' ' + '0.00 \n*' + self.language_conversion.translate('en', self.sender_redis['language'], 'Total') + ' ' + (' ' * 10) + self.convert_currency_symbol('EUR') + ' ' + str("{:.2f}".format(total)) + '*\n' + self.language_conversion.translate('en', self.sender_redis['language'], 'Deposit to pay now') + ' ' + (' ' * 10) + self.convert_currency_symbol('EUR') + ' *' + str("{:.2f}".format(deposite)) + '*\n*' + self.language_conversion.translate('en', self.sender_redis['language'], 'Balance') + ' ' + (' ' * 10) + self.convert_currency_symbol('EUR') + ' ' + str("{:.2f}".format(balance)) 
                        # + '\nExtra person charge ' + self.convert_currency_symbol('EUR') + ' ' + str("{:.2f}".format(extra_person_fee))
                        property_id = p['id']
                        your_details = "\n\n" + self.language_conversion.translate('en', self.sender_redis['language'], "To complete the booking we need") + " *" + self.language_conversion.translate('en', self.sender_redis['language'], "Your Details") + "*\n"
                        form = self.language_conversion.translate('en', self.sender_redis['language'], "Kindly reply your") + " *" + self.language_conversion.translate('en', self.sender_redis['language'], "Full Name and Email") + "* " + self.language_conversion.translate('en', self.sender_redis['language'], "in following format and no space") + ":\n\n" + self.language_conversion.translate('en', self.sender_redis['language'], "First Name,Last Name,Email") + "\n"
                        self.save_message(user['id'], str(self.from_phone_number[1]), t + price + reservation_details + price_details + your_details + form)
                        self.msg.body(t + price + reservation_details + price_details + your_details + form)

                        # self.msg.create(self.from_phone_number, self.to_phone_number, p['localita'], p['coordinatelat'], p['coordinatelon'], p['localita'] + ' ' + p['regione'])
                        
                        # self.msg.media(request.host_url.strip("/") + url_for('static', filename='pdf/rental_booking_form_hiresicily.pdf'))
                        break
                    j = j + 1
    
            # update the redis cache for this customer/sender
            sender_redis_payload = {
                'language': self.sender_redis['language'],
                'phone_number': self.from_phone_number, 
                'steps': self.steps, 
                'last_incoming_msg':self.incoming_msg,
                'last_reply': t + price + reservation_details + price_details + your_details + form,
                'check_in_date': self.sender_redis['check_in_date'],
                'check_out_date': self.sender_redis['check_out_date'],
                'check_in_date_redis_dt': self.sender_redis['check_in_date_redis_dt'],
                'check_out_date_redis_dt': self.sender_redis['check_out_date'],
                'persons': self.sender_redis['persons'],
                'children': self.sender_redis['children'],
                'days': self.sender_redis['days'],
                'selected': property_id,
                'total_price': t + price + reservation_details + price_details,
                'i': i + 1,
                'customer_details': '',
                'customer_registration_details': '',
                'customer_payment_details': '',
                'matched_properties': self.sender_redis['matched_properties'],
                'last_update': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            sender_redis_payload = json.dumps(sender_redis_payload)
            redis_client.set(self.from_phone_number, sender_redis_payload, 120)

            # self.resp.append(self.msg)
            self.msg.respond(True)

        elif self.customer_details != None and self.steps == 6:
            # need to call holigest customer registration API to save customer details
            # call API INSERISCI RICHIESTA
            payload = {
                "nome": self.customer_details[0],
                "cognome": self.customer_details[1],
                "email": self.customer_details[2],
                "telefono": self.from_phone_number,
                "messaggio": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "adulti": self.sender_redis['persons'],
                "bambini":0,
                "alloggio": self.sender_redis['selected'],
                "animali":"N",
                "paese":"Italia",
                "citta":"Milano",
                "indirizzo":"Via monte napoleone",
                "checkin": self.sender_redis['check_in_date_redis_dt'][:10],
                "checkout": self.sender_redis['check_out_date_redis_dt'][:10]
                }
            # print(payload)
            response = self.holigest.customer_request_registration(payload)
            response = json.loads(response)
            # print(response)
            self.save_message(user['id'], str(self.from_phone_number[1]), "\nCongratulation your booking request has been registered. Your can login here " + response['urlRichiesta'] + "\n\nHow do you want to pay? [reply a or b]\n" + self.show_key_values_selection(self.payment_methods) + "\n")
            self.bot.body(self.chat_id, "\n" + self.language_conversion.translate('en', self.sender_redis['language'], "Congratulation your booking request has been registered. Your can login here") + " " + response['urlRichiesta'] + "\n\n" + self.language_conversion.translate('en', self.sender_redis['language'], "How do you want to pay?") + " [" + self.language_conversion.translate('en', self.sender_redis['language'], "reply") + " a or b]\n" + self.show_key_values_selection(self.payment_methods) + "\n", self.message_id)

            self.steps = int(self.steps) + 1

            # update the redis cache for this customer/sender
            sender_redis_payload = {
                'language': self.sender_redis['language'],
                'phone_number': self.from_phone_number, 
                'steps': self.steps, 
                'last_incoming_msg':self.incoming_msg,
                'last_reply': "\nHow do you want to pay? [reply a or b]\n\n*A*. Crypto\n*B*. Paypal\n",
                'check_in_date': self.sender_redis['check_in_date'],
                'check_out_date': self.sender_redis['check_out_date'],
                'check_in_date_redis_dt': self.sender_redis['check_in_date_redis_dt'],
                'check_out_date_redis_dt': self.sender_redis['check_out_date'],
                'persons': self.sender_redis['persons'],
                'days': self.sender_redis['days'],
                'selected': self.sender_redis['selected'],
                'total_price': self.sender_redis['total_price'],
                'i': self.sender_redis['i'],
                'customer_details': self.customer_details,
                'customer_registration_details': response,
                'customer_payment_details': '',
                'matched_properties': self.sender_redis['matched_properties'],
                'last_update': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            sender_redis_payload = json.dumps(sender_redis_payload)
            redis_client.set(self.from_phone_number, sender_redis_payload, 120)

            # self.resp.append(self.msg)
            self.msg.respond(True)

        # send to hiresicily payment user details page
        elif int(self.steps) == 7 and self.checked:
            # process the auto fill
            property_url = self.sender_redis['matched_properties'][0]['titoloUrlFriendly'] + '-' + self.sender_redis['matched_properties'][0]['id']
            hiresicily_url = "https://www.hiresicily.com/book/" +  property_url + "/rate-0"
            self.save_message(user['id'], str(self.from_phone_number[1]), "To complete booking click this url 👉 " + hiresicily_url + "\n")
            self.bot.body(self.chat_id, self.language_conversion.translate('en', self.sender_redis['language'], "To complete booking click this url") + " 👉 " + hiresicily_url + "\n", self.message_id)

            self.steps = int(self.steps) + 1

            # update the redis cache for this customer/sender
            sender_redis_payload = {
                'language': self.sender_redis['language'],
                'phone_number': self.from_phone_number, 
                'steps': self.steps, 
                'last_incoming_msg':self.incoming_msg,
                'last_reply': "\nHow do you want to pay? [reply a or b]\n\n*A*. Crypto\n*B*. Paypal\n",
                'check_in_date': self.sender_redis['check_in_date'],
                'check_out_date': self.sender_redis['check_out_date'],
                'check_in_date_redis_dt': self.sender_redis['check_in_date_redis_dt'],
                'check_out_date_redis_dt': self.sender_redis['check_out_date'],
                'persons': self.sender_redis['persons'],
                'children':0,
                'days': self.sender_redis['days'],
                'selected': self.sender_redis['selected'],
                'total_price': self.sender_redis['total_price'],
                'i': self.sender_redis['i'],
                'customer_details': self.customer_details,
                'customer_registration_details': self.sender_redis['customer_registration_details'],
                'customer_payment_details': '',
                'matched_properties': self.sender_redis['matched_properties'],
                'last_update': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            sender_redis_payload = json.dumps(sender_redis_payload)
            redis_client.set(self.from_phone_number, sender_redis_payload, self.cache_time)
            # print(sender_redis_payload)
            # self.resp.append(self.msg)
            # self.bot.respond(True)

        elif not self.responded and self.incoming_msg == '':
            self.save_message(user['id'], str(self.from_phone_number[1]), '😱 *I only know about beautiful rooms in Sicily, sorry!*')
            self.msg.body('😱 *' + self.language_conversion.translate('en', self.sender_redis['language'], 'I only know about beautiful rooms in Sicily, sorry!') + '*')
        else: # if no matched found
            self.save_message(user['id'], str(self.from_phone_number[1]), "\n 🏁 *Kindly start from the beginning. You can start with say 'hi'*")
            self.msg.body("\n 🏁 *" + self.language_conversion.translate('en', self.sender_redis['language'], "Kindly start from the beginning. You can start with say 'hi'") + "*")
            
        self.msg.respond(True)
            
        return str(self.msg.msg_resp())


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
            result += '\n*' + k + '*: ' + v + '\n'        
        return result

    # this method will save each msg for every business users
    def save_message(self, user_id, from_, msg):
        new_msg = Message(user_id=user_id, phone=from_, body=msg[:100])
        db.session.add(new_msg)
        db.session.commit()
        return True