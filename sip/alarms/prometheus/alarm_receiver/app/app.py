# -*- coding: utf-8 -*-
"""Demo alarm handler."""

import logging
from flask import request
from flask_api import FlaskAPI
from .alarm_client import AlarmDbClient

APP = FlaskAPI(__name__)

logging.basicConfig(level=logging.INFO)

DB = AlarmDbClient()


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
        DB.update_value(data)
        return response
    return ""
