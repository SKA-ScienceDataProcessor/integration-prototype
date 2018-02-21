# -*- coding: utf-8 -*-
"""SIP Master Controller (REST)."""
import os
import signal

import redis
from flask import request
from flask_api import FlaskAPI, status


APP = FlaskAPI(__name__)
DB = redis.Redis(host=os.getenv('DATABASE_HOST'))


@APP.route('/')
def root():
    """."""
    return {
        "message": "Welcome to the SIP Master Controller",
        "_links": {
            "items": [
                {"href": "{}state".format(request.url)}
            ]
        }
    }


@APP.route('/state', methods=['GET', 'PUT'])
def state():

    """Return the SDP State."""

    # These are the states we allowed to rquest
    states = ['OFF', 'STANDBY', 'ON', 'DISABLE']

    if request.method == 'PUT':
        requested_state = request.data.get('state', '').upper()
        if requested_state not in states:
            return ({'error': 'Invalid state: {}'.format(requested_state),
                     'allowed_states': states},
                    status.HTTP_400_BAD_REQUEST)
        response = {'message': 'Accepted state: {}'.format(requested_state)}
        try:
            DB.set('state', requested_state)
        except redis.exceptions.ConnectionError:
            response['error'] = 'Unable to connect to database.'
        if requested_state == 'OFF':
            os.kill(os.getpid(), signal.SIGINT)
        return response

    # GET - if the state in the database is OFF we want to replace it with
    # INIT
    try:
        current_state = DB.get('state')
        if current_state is None or current_state.decode('utf-8') == 'OFF':
            DB.set('state', 'INIT')
            current_state = 'INIT'
        else:
            current_state = current_state.decode('utf-8')
        return {'state': '{}'.format(current_state)}
    except redis.exceptions.ConnectionError:
        return {'state': 'UNKNOWN',
                'error': 'Unable to connect to database.'}
