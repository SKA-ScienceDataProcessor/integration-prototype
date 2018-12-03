# -*- coding: utf-8 -*-
"""Demo alarm hander."""

import logging
import time
import json
from flask import request
from flask_api import FlaskAPI
from kafka import KafkaProducer

APP = FlaskAPI(__name__)

logging.basicConfig(level=logging.INFO)

# This sleep is needed to give kafka time to start up.
time.sleep(2)
producer = KafkaProducer(bootstrap_servers='kafka:9092')

@APP.route('/')
def root():
    """."""
    return {
        "message": "The demo alarm handler says hi",
        "_links": {
            "items": [
                {"href": "{}".format(request.url)}
            ]
        }
    }


@APP.route('/', methods=['POST'])
def alarm():
    """."""
    if request.method == 'POST':
        response = {'message': 'POST Accepted'}
        logging.info('alarm POSTED!')
        data = request.data
        logging.info(data)
        string = json.dumps(data)
        producer.send('SIP-alarms', string.encode())
        return response
    return ""
