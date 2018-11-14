# -*- coding: utf-8 -*-
"""
    SIP Master Interface Service, Restful version.
    
    Changes to the REDIS DB
    from config_db.sdp_state import SDPState
    from config_db.service_state import ServiceState
    sdp_state = SDPState()
    event_queue = sdp_state.subscripe(...)
    state = sdp_state.current_state
    state = sdp_state.target_state
    timestamp = sdp_state.current_timestamp
    timestamp = sdp_state.target_timestamp
    timestamp = sdp_state.update_target_state(state)
    timestamp = sdp_state.update_current_state(state)
    sdp_state.publish(event_type[,event_data])
    
    other_state = ServiceState(subsystem, name, version)
    Methods are as above.
    Services are defined as "subsystem.name.version"
    and currently defined services are:
        "ExecutionControl.MasterController.test",
        "ExecutionControl.ProcessingController.test",
        "ExecutionControl.ProcessingBlockController.test",
        "ExecutionControl.Alerts.test",
        "TangoControl.SDPMaster.test",
        "TangoControl.ProcessingInterface.test"
    so assuming we are not allowed to use the TangoControl subsystem
    we have the following available for "play"
    mc = ServiceState("ExecutionControl", "MasterController", "test")
    pc = ServiceState("ExecutionControl", "ProcessingController", "test")
    pbc = ServiceState("ExecutionControl", "ProcessingBlockController", "test")
    al = ServiceState("ExecutionControl", "Alerts", "test")
"""
from datetime import datetime
import redis
import json
import logging.config

from flask import request
from flask_api import FlaskAPI, status
#~ from config_db.master_client import MasterDbClient as masterClient
from config_db.sdp_state import SDPState


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
VERSION = '0.0.1' # must move out of this file ... ?

MC = 'master_controller'
PC = 'processing_controller'
LOG = 'logging'


@APP.route('/')
def root():
    """Home page of this Flask."""

    # logging
    APP.logger.debug("debugging information on")
    return {
        "message": "Welcome to the SIP Master Controller (flask variant)",
        "_links": {
            "items": [
                {"Link":"Version", "href": "{}version".format(request.url)}
                ,{"Link":"State", "href": "{}state".format(request.url)}
                ,{"Link":"SchedulingBlockInstances", "href": "{}SchedBlock".format(request.url)}
                ,{"Link":"ProcessingBlocks-all", "href": "{}ProcBlock/all".format(request.url)}
                ,{"Link":"ProcessingBlocks-offline", "href": "{}ProcBlock/offline".format(request.url)}
                ,{"Link":"ProcessingBlocks-realtime", "href": "{}ProcBlock/realtime".format(request.url)}
            ]
        }
    }


@APP.route('/ProcBlock/all')
def ProcessingBlocks():
    from config_db.pb import ProcessingBlock
    from config_db.sbi import SchedulingBlockInstance
    from config_db.sbi_list import SchedulingBlockInstanceList
    # apparently use pb not pb_list
    pb_ids = list()
    for sbi in (SchedulingBlockInstance(sbi) for sbi in SchedulingBlockInstanceList().active):
        pb_ids += sbi.get_pb_ids()
    pb_list = pb_ids
    return {
            'message':'This is the Processing Block Instance List',
            'num_instances':len(pb_list),
            'instances':pb_list
    }
    return { "message" : "Processing Blocks under construction" }


@APP.route('/ProcBlock/offline')
def offlineProcessingBlocks():
    return { "message" : "Processing Blocks under construction" }


@APP.route('/ProcBlock/realtime')
def realtimeProcessingBlocks():
    return { "message" : "Processing Blocks under construction" }


@APP.route('/SchedBlock')
def SchedulingBlocks():
    from config_db.sbi_list import DB, SchedulingBlockInstanceList
    sbi_list = SchedulingBlockInstanceList()
    return {
            'message':'This is the Scheduling Block Instance List',
            'num_instances':sbi_list.num_active,
            'instances':sbi_list.active
    }


@APP.route('/version')
def version():
    """Return the Master version."""
    return {
        "message": "Version {}".format(VERSION)
    }


@APP.route('/state', methods=['GET', 'PUT'])
def state():
    """Return the SDP State."""

    # These are the states we allowed to request
    #~ states = ('OFF', 'STANDBY', 'ON', 'DISABLE')
    #~ APP.logger.debug(states)

    # it could be that this is not necessary as a query for another
    # item may simply go through another route
    request_keys = ('state',)

    #~ db = masterClient()
    db = SDPState()
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
        requested_state = request.data.get('state', '').lower()
        sdp_state = db.current_state
        states = db.allowed_state_transitions[sdp_state]
        if not states:
            APP.logger.warn('No allowed states - cannot continue')
            return ({'error': 'No Allowed States',
                     'message': 'No allowed state transition for {}'.format(sdp_state)},
                     status.HTTP_400_BAD_REQUEST)
        if requested_state not in states:
            APP.logger.debug('Invalid state: {}'.format(requested_state))
            return ({'error': 'Invalid Input',
                     'message': 'Invalid state: {}'.format(requested_state),
                     'allowed_states': states},
                    status.HTTP_400_BAD_REQUEST)
        response = {'message': 'Accepted state: {}'.format(requested_state)}
        try:
            APP.logger.debug('updating state')
            
            APP.logger.debug('SDP_state is {}'.format(sdp_state))

            # If different then update target state
            if sdp_state != requested_state:
                #~ db.target_state(requested_state)
                timestamp = db.update_target_state(requested_state)
        except redis.exceptions.ConnectionError:
            APP.logger.debug('failed to connect to DB')
            response['error'] = 'Unable to connect to database.'
        except  ValueError as err:
            APP.logger.debug('Error updating target state: {}'.format(err))

        # if requested_state == 'OFF' the master controller
        # will deal with it, not this program.
        return response

    # GET - if the state in the database is OFF we want to replace it with
    # INIT
    try:
        APP.logger.debug('getting current state')
        current_state = db.current_state
        APP.logger.debug('got(?) current state')
        if current_state is None:
            APP.logger.debug('current state set to none')
            return {'state': 'UNKNOWN',
                    'reason': 'database not initialised.'}
        APP.logger.debug(current_state)
        #~ if current_state == 'OFF':
            #~ APP.logger.debug('current state off - set to init')
            #~ current_state = 'INIT'

        # Check the timestamp to be sure that the watchdog is alive
        APP.logger.debug('getting timestamp')
        state_tmstmp = db.current_timestamp
        target_tmstmp = db.target_timestamp
        if state_tmstmp is None or target_tmstmp is None:
            APP.logger.warning('Timestamp not available')
            return {'state': 'UNKNOWN',
                    'reason': 'Master Controller Services may have died.'}
        else:
            APP.logger.debug("State timestamp: {}".format(state_tmstmp))
            APP.logger.debug("Target timestamp: {}".format(target_tmstmp))
            #~ state_tmstmp = datetime.strptime(state_tmstmp,
                                             #~ '%Y/%m/%d %H:%M:%S.%f')
            #~ target_tmstmp = datetime.strptime(target_tmstmp,
                                              #~ '%Y/%m/%d %H:%M:%S.%f')
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
