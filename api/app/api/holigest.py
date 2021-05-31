from flask.views import MethodView
from flask import Flask, jsonify, request, abort, make_response, current_app
import requests
import json
import os


class Holigest():
    """ Holigest API process """
    
    headers = None
    x_what = None
    x_action = None
    # need to change later 
    x_user = 'GioApi'
    x_pass = 'ARP_x5_21-@'
    
    def __init__(self) -> None:
        super().__init__()

    # LISTA PRENOTAZIONI
    def reservation_list(self, payload):

        url = "https://hiresicily.holigest.it/api"

        self.x_what = 'DISPONIBILITA_ALLOGGIO'
        self.x_action = 'GET'

        self.headers = {
            'X-USER': self.x_user,
            'X-PASS': self.x_pass,
            'X-WHAT': self.x_what,
            'X-ACTION': self.x_action,
            'Content-Type': 'application/json'
        }

        response = requests.post(url, headers=self.headers, data=json.dumps(payload, indent = 4, sort_keys=True, default=str))

        return response.text

    # PRELEVA LISTA ALLOGGI
    # get property list as per the requirement exclude date
    def get_list_of_accomodations(self, payload):
        url = "https://hiresicily.holigest.it/api"

        self.x_what = 'ALLOGGILIST'
        self.x_action = 'GET'

        self.headers = {
            'X-USER': self.x_user,
            'X-PASS': self.x_pass,
            'X-WHAT': self.x_what,
            'X-ACTION': self.x_action,
            'Content-Type': 'application/json'
        }
        
        response = requests.post(url, headers=self.headers, data=json.dumps(payload, indent = 4, sort_keys=True, default=str))

        return response.text

    # PRELEVA TARIFFE ALLOGGI
    def collect_accomodation_rate(self, payload):
        url = "https://hiresicily.holigest.it/api"

        self.x_what = 'TARIFFE'
        self.x_action = 'GET'

        self.headers = {
            'X-USER': self.x_user,
            'X-PASS': self.x_pass,
            'X-WHAT': self.x_what,
            'X-ACTION': self.x_action,
            'Content-Type': 'application/json'
        }

        response = requests.post(url, headers=self.headers, data=json.dumps(payload, indent = 4, sort_keys=True, default=str))

        return response.text

    # INSERISCI DISPONIBILITA
    def enter_availability(self, payload):
        url = "https://hiresicily.holigest.it/api"

        self.x_what = 'DISPONIBILITA_ALLOGGIO'
        self.x_action = 'GET'

        self.headers = {
            'X-USER': self.x_user,
            'X-PASS': self.x_pass,
            'X-WHAT': self.x_what,
            'X-ACTION': self.x_action,
            'Content-Type': 'application/json'
        }

        response = requests.post(url, headers=self.headers, data=json.dumps(payload, indent = 4, sort_keys=True, default=str))

        return response.text

    # INSERISCI RICHIESTA
    def customer_request_registration(self, payload):

        url = "https://hiresicily.holigest.it/api"

        self.x_what = 'RICHIESTE'
        self.x_action = 'POST'

        self.headers = {
            'X-USER': self.x_user,
            'X-PASS': self.x_pass,
            'X-WHAT': self.x_what,
            'X-ACTION': self.x_action,
            'Content-Type': 'application/json'
        }

        response = requests.post(url, headers=self.headers, data=json.dumps(payload, indent = 4, sort_keys=True, default=str))

        return response.text
