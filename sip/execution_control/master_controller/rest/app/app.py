# -*- coding: utf-8 -*-
"""SIP Master Controller (REST)."""
from datetime import datetime
import os
import redis
import signal
import json
import logging.config

from flask import request
from flask_api import FlaskAPI, status


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
         "format": "[%(asctime)s] [%(process)s] [%(levelname)s] in %(module)s: %(message)s",
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
      "level": "INFO",
      "handlers": ["wsgi"]
   }
}
'''
logging.config.dictConfig(json.loads(logConfigAsJSON))
#~ logging.config.dictConfig({
    #~ 'version': 1,
    #~ 'formatters': {'default': {
        #~ 'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    #~ }},
    #~ 'handlers': {'wsgi': {
        #~ 'class': 'logging.StreamHandler',
        #~ 'stream': 'ext://flask.logging.wsgi_errors_stream',
        #~ 'formatter': 'default'
    #~ }},
    #~ 'root': {
        #~ 'level': 'INFO',
        #~ 'handlers': ['wsgi']
    #~ }
#~ })

APP = FlaskAPI(__name__)

from .master_client import masterClient

@APP.route('/')
def root():
    """."""

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
    states = ['OFF', 'STANDBY', 'ON', 'DISABLE']
    APP.logger.debug(states)

    db = masterClient()
    if request.method == 'PUT':
        requested_state = request.data.get('state', '').upper()
        if requested_state not in states:
            return ({'error': 'Invalid state: {}'.format(requested_state),
                     'allowed_states': states},
                    status.HTTP_400_BAD_REQUEST)
        response = {'message': 'Accepted state: {}'.format(requested_state)}
        try:
            APP.logger.debug('updating state')
            db.update_value('execution_control:master_controller',
                    'target_state', requested_state)
        except redis.exceptions.ConnectionError:
            APP.logger.debug('failed to connect to DB')
            response['error'] = 'Unable to connect to database.'
        if requested_state == 'OFF':
            os.kill(os.getpid(), signal.SIGINT)
        return response

    # GET - if the state in the database is OFF we want to replace it with
    # INIT
    try:
        APP.logger.debug('getting current state')
        current_state = db.get_value('execution_control:master_controller',
                'TANGO_state')
        if current_state == None:
            APP.logger.debug('current state set to none')
            return {'state': 'UNKNOWN',
                    'reason': 'database not initialised.'}
        if current_state == 'OFF':
            APP.logger.debug('current state off - set to init')
            current_state = 'INIT'

        # Check the timestamp to be sure that the watchdog is alive
        APP.logger.debug('getting timestamp')
        timestamp = db.get_value('execution_control:master_controller',
                'state_timestamp')
        if timestamp == None:
            APP.logger.debug('no timestamp')
            return {'state': 'UNKNOWN',
                    'reason': 'services watchdog has died.'}
        else:
            APP.logger.debug("timestamp in DB: {}".format(timestamp))
            APP.logger.debug("current time:    {}".format(datetime.utcnow()))
            timestamp = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S.%f')
            if (datetime.utcnow() - timestamp).seconds < 10:
                APP.logger.debug('timestamp okay')
                return {'state': current_state}
            else:
                APP.logger.warning('timestamp stale')
                return {'state': 'UNKNOWN',
                        'reason': 'services watchdog has died.'}
    except redis.exceptions.ConnectionError:
        APP.logger.debug('error connecting to DB')
        return {'state': 'UNKNOWN',
                'reason': 'Unable to connect to database.'}