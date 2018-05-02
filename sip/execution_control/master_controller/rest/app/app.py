# -*- coding: utf-8 -*-
"""SIP Master Controller (REST)."""
from datetime import datetime
import os
import redis
import signal

from flask import request
from flask_api import FlaskAPI, status


APP = FlaskAPI(__name__)

from .master_client import masterClient

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

    # These are the states we allowed to request
    states = ['OFF', 'STANDBY', 'ON', 'DISABLE']

    db = masterClient()
    if request.method == 'PUT':
        requested_state = request.data.get('state', '').upper()
        if requested_state not in states:
            return ({'error': 'Invalid state: {}'.format(requested_state),
                     'allowed_states': states},
                    status.HTTP_400_BAD_REQUEST)
        response = {'message': 'Accepted state: {}'.format(requested_state)}
        try:
            db.update_value('execution_control:master_controller',
                    'target_state', requested_state)
        except redis.exceptions.ConnectionError:
            response['error'] = 'Unable to connect to database.'
        if requested_state == 'OFF':
            os.kill(os.getpid(), signal.SIGINT)
        return response

    # GET - if the state in the database is OFF we want to replace it with
    # INIT
    try:
        current_state = db.get_value('execution_control:master_controller',
                'TANGO_state')
        if current_state == None:
            return {'state': 'UNKNOWN',
                    'reason': 'database not initialised.'}
        if current_state == 'OFF':
            current_state = 'INIT'

        # Check the timestamp to be sure that the watchdog is alive
        timestamp = db.get_value('execution_control:master_controller',
                'state_timestamp')
        if timestamp == None:
            return {'state': 'UNKNOWN',
                    'reason': 'services watchdog has died.'}
        else:
            timestamp = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S.%f')
            if (datetime.now() - timestamp).seconds < 10:
                return {'state': current_state}
            else:
                return {'state': 'UNKNOWN',
                        'reason': 'services watchdog has died.'}
    except redis.exceptions.ConnectionError:
        return {'state': 'UNKNOWN',
                'reason': 'Unable to connect to database.'}
