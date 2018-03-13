# -*- coding: utf-8 -*-
"""SIP Master Controller (REST)."""
import os
import signal

import redis
from flask import request
from flask_api import FlaskAPI, status

APP = FlaskAPI(__name__)

if 'UNIT_TESTING' in os.environ:
    from .mock_config_db_client import put_target_state
    from .mock_config_db_client import get_tango_state
    from .mock_config_db_client import check_timestamp
else:
    from .config_db_client import put_target_state
    from .config_db_client import get_tango_state
    from .config_db_client import check_timestamp

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

    if request.method == 'PUT':
        requested_state = request.data.get('state', '').upper()
        if requested_state not in states:
            return ({'error': 'Invalid state: {}'.format(requested_state),
                     'allowed_states': states},
                    status.HTTP_400_BAD_REQUEST)
        response = {'message': 'Accepted state: {}'.format(requested_state)}
        try:
            put_target_state(requested_state)
        except redis.exceptions.ConnectionError:
            response['error'] = 'Unable to connect to database.'
        if requested_state == 'OFF':
            os.kill(os.getpid(), signal.SIGINT)
        return response

    # GET - if the state in the database is OFF we want to replace it with
    # INIT
    try:
        current_state = get_tango_state()
        if current_state == None:
            return {'state': 'UNKNOWN',
                    'error': 'database not initialised.'}

        # Check the timestamp to be sure that the watchdog is alive
        if check_timestamp():
            if current_state == 'OFF':
                current_state = 'INIT'
            return {'state': current_state}
        else:
            return {'state': 'UNKNOWN',
                    'error': 'services watchdog has died.'}
    except redis.exceptions.ConnectionError:
        return {'state': 'UNKNOWN',
                'error': 'Unable to connect to database.'}
