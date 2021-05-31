#!/usr/bin/env python

import os
from flask import Flask, request, jsonify
# model import is required to set up database correctly
from app.models import User, Message
from app import app, db
from config import base

# from rq import Queue
# from rq.job import Job
# from app.worker import conn

from app.site.routes import site
from app.site.routes import auth
from app.site.routes import message
from app.api.routes import api


# register blueprints
app.register_blueprint(site)
app.register_blueprint(auth)
app.register_blueprint(message)
app.register_blueprint(api, url_prefix='/api/v1')


@app.route("/", methods=['POST'])
def hello():
    info, status_code = check_authorization(request)

    if status_code != 200:
        return info, status_code
    else: 
        status, status_code = check_parameters(request.form)

    if status_code != 200:
        return status, status_code
    else:
        score = main()
        response = {"status": "success", "score": score, "customer_id":(request.form["cust_id"])}

        return jsonify(response), status_code


def check_authorization(request):
    try:
        if not 'Auth-token' in request.headers:
            return jsonify({'error': 'unauthorized access'}), 401
        token = request.headers['Auth-token']
        if token != auth_secret_token:
            return jsonify({'error': 'unauthorized access'}), 401
        return "ok", 200
    except Exception as e:
        return jsonify({'error': 'unauthorized access'}), 401


if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        q = Queue(connection=conn)


        # creates user if one doesn't exist
        # if User.query.filter_by(phone_number='user') is None:
        #     user = User(phone_number='user', password='12345678', email='test@email.com')
        #     db.session.add(user)
        #     db.session.commit()

    app.run(threaded=True, debug=True)
