from flask.views import MethodView
from flask import Flask, jsonify, request, abort, make_response, current_app
import requests
import json
import os

from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client


class OrderbotTwilio():
    """ Twilio API process """
    
    resp = None
    msg = None
    twilio_client = None
    
    def __init__(self, account_sid, auth_token) -> None:
        super().__init__()
        # Your Account Sid and Auth Token from twilio.com/console
        # and set the environment variables. See http://twil.io/secure
        self.twilio_client = Client(account_sid, auth_token)

        self.resp = MessagingResponse()
        self.msg = self.resp.message()
        self.responded = False

    # return resp 
    def msg_resp(self):
        return self.resp

    # to send text msg 
    def body(self, msg):
        self.msg.body(msg)

    # to send media msg
    def media(self, path):
        self.msg.media(path)

    # it just make responded to true or false
    def respond(self, state):
        self.responded = state

    # create a geo map
    def create(self, from_, to, body, lat, lon, label=''):
        message = self.twilio_client.messages.create(
            to='whatsapp:' + to,
            body=body,
            persistent_action=['geo:' + lat + ',' + lon + '|' + label + '']
        )
        return message
