# from typing import ChainMap
from flask.views import MethodView
from flask import Flask, jsonify, request, abort, make_response, current_app
import requests
import json
import os
import telegram


class OrderbotTelegram():
    """ Telegram API process """
    
    resp = None
    msg = None
    telegram_token = None
    telegram_client = None
    telegram_base_url = None
    time_out = 100
    bot = None
    telegram = None
    
    def __init__(self, auth_token) -> None:
        super().__init__()
        self.telegram_token = auth_token
        self.telegram_base_url = "https://api.telegram.org/bot{}/".format(self.telegram_token)
        self.telegram = telegram
        self.bot = self.telegram.Bot(token=auth_token)

    # set webhook
    # https://api.telegram.org/bot1616238596:AAFvtdMGyHVBGEWb_omiuB0D0QGCVCUS5w0/setWebhook?url=https://1c53586b2708.ngrok.io/api/v1/telegram_hook/37470c9583a8de5932b3f944391edb54
    def set_webhook(self, hook):
        # we use the bot object to link the bot to our app which live
        # in the link provided by URL
        s = self.bot.setWebhook('{URL}/setWebhook?url={HOOK}'.format(URL=self.telegram_base_url, HOOK=hook))
        # something to let us know things work
        if s:
            return "webhook setup ok"
        else:
            return "webhook setup failed"

    # get web hook info
    def get_webhook(self, hook):
        s = self.bot.getWebhookInfo(self, '{URL}/setWebhook?url={HOOK}'.format(URL=self.telegram_base_url, HOOK=hook))
        return s


    # only when webhook not using
    def get_updates(self, offset=None):
        # url = self.telegram_base_url + "getUpdates?timeout=" + str(self.time_out)
        # print(url)
        # if offset:
        #     url = url + "&offset={}".format(offset + 1)
        # r = requests.get(url)
        return self.bot.getUpdates()
        # return json.loads(r.content)

    # return resp 
    def msg_resp(self, chat_id, msg):
        url = self.telegram_base_url + "sendMessage?chat_id={}&text={}".format(chat_id, msg)
        if chat_id is not None and msg is not None:
            requests.get(url)

    # create ReplyKeyboardMarkup object
    def ReplyKeyboardMarkup(self, keyboard, resize_keyboard = True, one_time_keyboard = False):
        # create keybaordbutton obj
        # buttons = []
        # for row in keyboard:
        #     for key in row:
        #         buttons.append(self.telegram.KeyboardButton({'text': key}))
        return self.telegram.ReplyKeyboardMarkup(keyboard)

    # to send text msg 
    def body(self, chat_id, msg, message_id, reply_markup = None):
        # self.telegram.ReplyKeyboardRemove(remove_keyboard = True, selective = False)
        # self.bot.ReplyKeyboardRemove(remove_keyboard = True, selective = False)
        # self.telegram.ReplyKeyboardRemove(True)
        # url = self.telegram_base_url + "sendMessage?chat_id={}&text={}".format(chat_id, msg)
        if chat_id is not None and msg is not None:
        #     requests.get(url)
            if reply_markup != None:
                return self.bot.sendMessage(chat_id, text=msg, parse_mode="HTML", reply_to_message_id=message_id, disable_web_page_preview="true", reply_markup=reply_markup)
            else:
                return self.bot.sendMessage(chat_id, text=msg, parse_mode="HTML", reply_to_message_id=message_id, disable_web_page_preview="true", reply_markup=self.telegram.ReplyKeyboardRemove(remove_keyboard = True, selective = False))

    def local_media(self, chat_id, msg, message_id):
        if chat_id is not None and msg is not None:
            url = self.telegram_base_url + "sendMessage?chat_id={}&text={}&reply_to_message_id={}&disable_web_page_preview=false".format(chat_id, msg, message_id)

    # to send media msg
    def media(self, chat_id, msg, caption, message_id):
   
        # url = self.telegram_base_url + "sendMessage?chat_id={}&text={}&disable_web_page_preview=false".format(chat_id, msg)
        url = self.telegram_base_url + "sendPhoto?chat_id={}&photo={}&caption={}".format(chat_id, msg, caption)
        if chat_id is not None and msg is not None:
            return requests.get(url)
            # return self.bot.sendPhoto(chat_id, photo=msg, caption=caption, reply_to_message_id=message_id)

    def location(self, chat_id, lat, lon, message_id):
        if chat_id is not None and lat is not None and lon is not None:
            return self.bot.sendLocation(chat_id, latitude=lat, longitude=lon, reply_to_message_id=message_id)

    def video(self, chat_id, video, message_id):
        if chat_id is not None and video is not None:
            return self.bot.sendVideo(chat_id, video=video, reply_to_message_id=message_id)
        
    # send chat action
    def action(self, chat_id, action="typing"):
        if chat_id is not None:
            return self.bot.sendChatAction(chat_id, action=action)

    def document(self, chat_id, url, name, message_id):
        if chat_id is not None and url is not None and name is not None:
            return self.bot.sendDocument(chat_id, document=(url, name), reply_to_message_id=message_id)

    # get the chat location of the
    def get_location(self, chat_id):
        if chat_id is not None:
            return {
                chat_id.location.latitude,
                chat_id.location.longitude
            }

    # # it just make responded to true or false
    # def respond(self, state):
    #     self.responded = state

    # # create a geo map
    # def create(self, from_, to, body, lat, lon, label=''):
    #     message = self.twilio_client.messages.create(
    #         to='whatsapp:' + to,
    #         body=body,
    #         persistent_action=['geo:' + lat + ',' + lon + '|' + label + '']
    #     )
    #     return message
