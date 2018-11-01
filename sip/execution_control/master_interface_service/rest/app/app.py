# -*- coding: utf-8 -*-
"""
    SIP Master Interface Service, Restful version.
"""
from datetime import datetime
import redis
import json
import logging.config

from flask import request
from flask_api import FlaskAPI, status
from config_db.master_client import MasterDbClient as masterClient


logConfigAsJSON = '''{
   "version": 1,
   "formatters":
   {
      "default":
      {
         "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
      },
      "flask_style":
      {
         "format":
    "[%(asctime)s] [%(process)s] [%(levelname)s] in %(module)s: %(message)s",
         "datefmt": "%Y-%m-%d %H:%M:%S %z"
      }
   },
   "handlers":
   {
      "wsgi":
      {
         "class": "logging.StreamHandler",
         "stream": "ext://flask.logging.wsgi_errors_stream",
         "formatter": "flask_style"
      }
   },
   "root":
   {
      "level": "DEBUG",
      "handlers": ["wsgi"]
   }
}
'''
logging.config.dictConfig(json.loads(logConfigAsJSON))

APP = FlaskAPI(__name__)


MC = 'master_controller'
PC = 'processing_controller'
LOG = 'logging'


@APP.route('/')
def root():
    """Home page of this Flask."""

    # logging
    APP.logger.debug("debugging information on")
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
    states = ('OFF', 'STANDBY', 'ON', 'DISABLE')
    APP.logger.debug(states)

    # it could be that this is not necessary as a query for another
    # item may simply go through another route
    request_keys = ('state',)

    db = masterClient()
    if request.method == 'PUT':

        # Has the user used unknown keys in the query?
        unk_kys = [ky for ky in request.data.keys() if ky not in request_keys]

        # unk_kys should be empty
        if unk_kys:
            APP.logger.debug('Unrecognised keys in data')
            return ({'error': 'Invalid request key(s) ({})'.
                    format(','.join(unk_kys)),
                     'allowed_request_keys': request_keys},
                    status.HTTP_400_BAD_REQUEST)
        requested_state = request.data.get('state', '').upper()
        if requested_state not in states:
            return ({'error': 'Invalid state: {}'.format(requested_state),
                     'allowed_states': states},
                    status.HTTP_400_BAD_REQUEST)
        response = {'message': 'Accepted state: {}'.format(requested_state)}
        try:
            APP.logger.debug('updating state')

            # Get SDP state.
            sdp_state = db.get_value(MC, 'SDP_state')
            APP.logger.debug('SDP_state is {}'.format(sdp_state))

            # If different then update target state
            if sdp_state != requested_state:
                db.update_target_state('Target_state', requested_state)
        except redis.exceptions.ConnectionError:
            APP.logger.debug('failed to connect to DB')
            response['error'] = 'Unable to connect to database.'

        # if requested_state == 'OFF':
        # Do we really want to do this?
        # Also, do we really want to put OFF into the database?
        # os.kill(os.getpid(), signal.SIGINT)
        return response

    # GET - if the state in the database is OFF we want to replace it with
    # INIT
    try:
        APP.logger.debug('getting current state')
        current_state = db.get_value(MC, 'SDP_state')
        if current_state is None:
            APP.logger.debug('current state set to none')
            return {'state': 'UNKNOWN',
                    'reason': 'database not initialised.'}
        if current_state == 'OFF':
            APP.logger.debug('current state off - set to init')
            current_state = 'INIT'

        # Check the timestamp to be sure that the watchdog is alive
        APP.logger.debug('getting timestamp')
        state_tmstmp = db.get_value(MC, 'State_timestamp')
        target_tmstmp = db.get_value(MC, 'Target_timestamp')
        if state_tmstmp is None or target_tmstmp is None:
            APP.logger.warning('Timestamp not available')
            return {'state': 'UNKNOWN',
                    'reason': 'Master Controller Services may have died.'}
        else:
            APP.logger.debug("State timestamp: {}".format(state_tmstmp))
            APP.logger.debug("Target timestamp: {}".format(target_tmstmp))
            state_tmstmp = datetime.strptime(state_tmstmp,
                                             '%Y/%m/%d %H:%M:%S.%f')
            target_tmstmp = datetime.strptime(target_tmstmp,
                                              '%Y/%m/%d %H:%M:%S.%f')
            if target_tmstmp < state_tmstmp:
                APP.logger.debug('timestamp okay')
                return {'state': current_state}
            else:
                APP.logger.warning(
                        'Timestamp for Master Controller Services is stale')
                return {'state': 'UNKNOWN',
                        'reason': 'Master Controller Services may have died.'}
    except redis.exceptions.ConnectionError:
        APP.logger.debug('error connecting to DB')
        return {'state': 'UNKNOWN',
                'reason': 'Unable to connect to database.'}
