# -*- coding: utf-8 -*-
"""SIP SDP Master Interface Service, Restful version."""

import time
from http import HTTPStatus

import redis
from flask import request
from flask_api import FlaskAPI

from sip_config_db.scheduling import ProcessingBlockList, \
    SchedulingBlockInstanceList
from sip_config_db.states import SDPState
from sip_logging import init_logger
from .release import LOG, __service_id__, __version__

init_logger('flask.logging.wsgi_errors_stream')
init_logger()

APP = FlaskAPI(__name__)

START_TIME = time.time()


@APP.route('/')
def root():
    """Home page."""
    return {
        "message": "Welcome to the SIP Master Controller (flask variant)",
        "_links": {
            "items": [
                {
                    "Link": "Health",
                    "href": "{}health".format(request.url)
                },
                {
                    "Link": "Version",
                    "href": "{}version".format(request.url)
                },
                {
                    "Link": "Allowed target states",
                    "href": "{}allowed_target_sdp_states".format(request.url)
                },
                {
                    "Link": "SDP state",
                    "href": "{}state".format(request.url)
                },
                {
                    "Link": "SDP target state",
                    "href": "{}state/target".format(request.url)
                },
                {
                    "Link": "SDP current state",
                    "href": "{}state/current".format(request.url)
                },
                {
                    "Link": "Scheduling Block Instances",
                    "href": "{}scheduling_block_instances".format(request.url)
                },
                {
                    "Link": "Processing Blocks",
                    "href": "{}processing_blocks".format(request.url)
                }
            ]
        }
    }


@APP.route('/health')
def health():
    """Check the health of this service."""
    up_time = time.time() - START_TIME
    response = dict(service=__service_id__,
                    uptime='{:.2f}s'.format(up_time))
    return response, HTTPStatus.OK


@APP.route('/version')
def version():
    """Service Version."""
    return {
        "message": "Version {}".format(__version__)
    }


@APP.route('/allowed_target_sdp_states')
def allowed_transitions():
    """Get target states allowed for the current state."""
    sdp_state = SDPState()
    return sdp_state.allowed_target_states[sdp_state.current_state]


@APP.route('/state', methods=['GET'])
def get_state():
    """SDP State."""
    sdp_state = SDPState()
    _last_updated = sdp_state.current_timestamp
    if sdp_state.target_timestamp > _last_updated:
        _last_updated = sdp_state.target_timestamp

    return dict(
        current_state=sdp_state.current_state,
        target_state=sdp_state.target_state,
        allowed_target_states=sdp_state.allowed_target_states[
            sdp_state.current_state],
        last_updated=_last_updated.isoformat()
    ), HTTPStatus.OK


@APP.route('/state', methods=['PUT'])
def put_state():
    """SDP State."""
    sdp_state = SDPState()
    request_data = request.data
    target_state = request_data['value']
    sdp_state.update_target_state(target_state)
    return dict(message='Target state successfully updated to {}'
                .format(target_state)), HTTPStatus.ACCEPTED


@APP.route('/state/target', methods=['GET'])
def get_target_state():
    """SDP target State."""
    sdp_state = SDPState()
    try:
        LOG.debug('Getting target state')
        target_state = sdp_state.target_state
        LOG.debug('Target state = %s', target_state)
        return dict(
            current_target_state=target_state,
            allowed_target_states=sdp_state.allowed_target_states[
                sdp_state.current_state],
            last_updated=sdp_state.target_timestamp.isoformat())
        # if target_state is None:
        #     LOG.debug('target state unknown')
        #     return {'target_state': target_state,
        #             'reason': 'database not initialised.'}
        #
        # # Check the timestamp to be sure that the watchdog is alive
        # LOG.debug('getting timestamp')
        # state_tmstmp = sdp_state.current_timestamp
        # target_tmstmp = sdp_state.target_timestamp
        # if state_tmstmp is None or target_tmstmp is None:
        #     LOG.warning('Timestamp not available')
        #     return {'state': 'UNKNOWN',
        #             'reason': 'Master Controller Services may have died.'}
        #
        # LOG.debug("State timestamp: %s", state_tmstmp.isoformat())
        # LOG.debug("Target timestamp: %s", target_tmstmp.isoformat())
        # if target_tmstmp < state_tmstmp:
        #     LOG.debug('timestamp okay')
        #     return {'target_state': target_state}
        #
        # LOG.warning('Timestamp for Master Controller Services is stale')
        # return {'target_state': 'UNKNOWN',
        #         'reason': 'Master Controller Services may have died.'}

    except redis.exceptions.ConnectionError:
        LOG.debug('error connecting to DB')
        return {'target_state': 'unknown',
                'reason': 'Unable to connect to database.'}


@APP.route('/state/target', methods=['PUT'])
def put_target_state():
    """SDP target State."""
    sdp_state = SDPState()

    try:
        request_data = request.data
        target_state = request_data['value']
        sdp_state.update_target_state(target_state)
        return dict(message='Target state successfully updated to {}'
                    .format(target_state))

        # LOG.debug('getting target state')
        # target_state = sdp_state.target_state
        # LOG.debug('got(?) target state')
        # if target_state is None:
        #     LOG.debug('target state set to none')
        #     return {'target_state': 'UNKNOWN',
        #             'reason': 'database not initialised.'}
        # LOG.debug(target_state)
        #
        # # Check the timestamp to be sure that the watchdog is alive
        # LOG.debug('getting timestamp')
        # state_tmstmp = sdp_state.current_timestamp
        # target_tmstmp = sdp_state.target_timestamp
        # if state_tmstmp is None or target_tmstmp is None:
        #     LOG.warning('Timestamp not available')
        #     return {'state': 'UNKNOWN',
        #             'reason': 'Master Controller Services may have died.'}
        #
        # LOG.debug("State timestamp: %s", state_tmstmp.isoformat())
        # LOG.debug("Target timestamp: %s", target_tmstmp.isoformat())
        # if target_tmstmp < state_tmstmp:
        #     LOG.debug('timestamp okay')
        #     return {'target_state': target_state}
        #
        # LOG.warning('Timestamp for Master Controller Services is stale')
        # return {'target_state': 'UNKNOWN',
        #         'reason': 'Master Controller Services may have died.'}
    except ValueError as error:
        return dict(error='Failed to set target state',
                    reason=str(error))
    except RuntimeError as error:
        return dict(error='RunTime error',
                    reason=str(error))


@APP.route('/state/current', methods=['GET'])
def get_current_state():
    """Return the SDP State."""
    sdp_state = SDPState()
    return dict(current_state=sdp_state.current_state,
                last_updated=sdp_state.current_timestamp.isoformat())
    # pylint: disable=too-many-return-statements

    # These are the states we allowed to request
    # states = ('OFF', 'STANDBY', 'ON', 'DISABLE')
    # LOG.debug(states)

    # it could be that this is not necessary as a query for another
    # item may simply go through another route
    # request_keys = ('state',)
    #
    # # db = masterClient()
    # sdp_state = SDPState()
    # if request.method == 'PUT':
    #
    #     # Has the user used unknown keys in the query?
    #     unk_kys = [ky for ky in request.data.keys()
    #                if ky not in request_keys]
    #
    #     # unk_kys should be empty
    #     if unk_kys:
    #         LOG.debug('Unrecognised keys in data')
    #         return (dict(error='Invalid request key(s) ({})'
    #                      .format(','.join(unk_kys)),
    #                      allowed_request_keys=request_keys),
    #                 status.HTTP_400_BAD_REQUEST)
    #     requested_state = request.data.get('state', '').lower()
    #     sdp_state = sdp_state.current_state
    #     states = sdp_state.allowed_state_transitions[sdp_state]
    #     if not states:
    #         LOG.warning('No allowed states - cannot continue')
    #         return (dict(error='No Allowed States',
    #                      message='No allowed state transition for {}'
    #                      .format(sdp_state)
    #                      ), status.HTTP_400_BAD_REQUEST)
    #     if requested_state not in states:
    #         LOG.debug('Invalid state: %s', requested_state)
    #         return ({'error': 'Invalid Input',
    #                  'message': 'Invalid state: {}'.format(requested_state),
    #                  'allowed_states': states},
    #                 status.HTTP_400_BAD_REQUEST)
    #     response = {'message': 'Accepted state: {}'.format(requested_state)}
    #     try:
    #         LOG.debug('Updating state, SDP state is: %s', sdp_state)
    #
    #         # If different then update target state
    #         if sdp_state != requested_state:
    #             # db.target_state(requested_state)
    #             sdp_state.update_target_state(requested_state)
    #
    #     except redis.exceptions.ConnectionError:
    #         LOG.debug('failed to connect to DB')
    #         response['error'] = 'Unable to connect to database.'
    #     except ValueError as err:
    #         LOG.debug('Error updating target state: %s', str(err))
    #
    #     # if requested_state == 'OFF' the master controller
    #     # will deal with it, not this program.
    #     return response
    #
    # # GET - if the state in the database is OFF we want to replace it with
    # # INIT
    # try:
    #     LOG.debug('getting current state')
    #     current_state = sdp_state.current_state
    #     LOG.debug('got(?) current state')
    #     if current_state is None:
    #         LOG.debug('current state set to none')
    #         return {'state': 'UNKNOWN',
    #                 'reason': 'database not initialised.'}
    #     LOG.debug(current_state)
    #     # if current_state == 'OFF':
    #     # LOG.debug('current state off - set to init')
    #     # current_state = 'INIT'
    #
    #     # Check the timestamp to be sure that the watchdog is alive
    #     LOG.debug('getting timestamp')
    #     state_tmstmp = sdp_state.current_timestamp
    #     target_tmstmp = sdp_state.target_timestamp
    #     if state_tmstmp is None or target_tmstmp is None:
    #         LOG.warning('Timestamp not available')
    #         return {'state': 'UNKNOWN',
    #                 'reason': 'Master Controller Services may have died.'}
    #
    #     LOG.debug("State timestamp: %s", state_tmstmp.isoformat())
    #     LOG.debug("Target timestamp: %s", target_tmstmp.isoformat())
    #     # state_tmstmp = datetime.strptime(state_tmstmp,
    #     # '%Y/%m/%d %H:%M:%S.%f')
    #     # target_tmstmp = datetime.strptime(target_tmstmp,
    #     # '%Y/%m/%d %H:%M:%S.%f')
    #     if target_tmstmp < state_tmstmp:
    #         LOG.debug('timestamp okay')
    #         return {'state': current_state}
    #
    #     LOG.warning(
    #         'Timestamp for Master Controller Services is stale')
    #     return {'state': 'UNKNOWN',
    #             'reason': 'Master Controller Services may have died.'}
    # except redis.exceptions.ConnectionError:
    #     LOG.debug('error connecting to DB')
    #     return {'state': 'UNKNOWN',
    #             'reason': 'Unable to connect to database.'}


@APP.route('/processing_blocks')
def processing_block_list():
    """Return the list of processing blocks known to SDP."""
    pb_list = ProcessingBlockList()
    return dict(active=pb_list.active,
                completed=pb_list.completed,
                aborted=pb_list.aborted)


@APP.route('/scheduling_block_instances')
def scheduling_blocks():
    """Return list of Scheduling Block instances known to SDP."""
    sbi_list = SchedulingBlockInstanceList()
    return dict(active=sbi_list.active,
                completed=sbi_list.completed,
                aborted=sbi_list.aborted)
