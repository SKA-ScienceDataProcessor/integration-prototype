# -*- coding: utf-8 -*-
"""SIP SDP Master Interface Service, Restful version."""

import redis
from flask import request
from flask_api import FlaskAPI, status

from sip_config_db.scheduling import ProcessingBlock, \
    SchedulingBlockInstance, SchedulingBlockInstanceList
from sip_config_db.states import SDPState
from sip_logging import init_logger
from .__init__ import __version__, LOG

# FIXME(BMo) Enable the logging name 'flask.logging.wsgi_errors_stream' ?
init_logger()

APP = FlaskAPI(__name__)


@APP.route('/')
def root():
    """Home page."""
    # logging
    return {
        "message": "Welcome to the SIP Master Controller (flask variant)",
        "_links": {
            "items": [
                {
                    "Link": "Version",
                    "href": "{}version".format(request.url)
                },
                {
                    "Link": "State",
                    "href": "{}target_state".format(request.url)
                },
                {
                    "Link": "Target state",
                    "href": "{}state".format(request.url)
                },
                {
                    "Link": "SchedulingBlockInstances",
                    "href": "{}SchedBlock".format(request.url)
                },
                {
                    "Link": "ProcessingBlocks-all",
                    "href": "{}ProcBlock/all".format(request.url)
                },
                {
                    "Link": "ProcessingBlocks-offline",
                    "href": "{}ProcBlock/offline".format(request.url)
                },
                {
                    "Link": "ProcessingBlocks-realtime",
                    "href": "{}ProcBlock/realtime".format(request.url)
                }
            ]
        }
    }


@APP.route('/ProcBlock/all')
def processing_block_list():
    """Return the list of processing blocks known to SDP."""
    # FIXME(BMo) should be able to use method on ProcessingBlockList.
    pb_ids = list()
    for sbi in (SchedulingBlockInstance(sbi) for sbi in
                SchedulingBlockInstanceList().active):
        pb_ids += sbi.get_pb_ids()
    pb_list = pb_ids
    return {
        'message': 'This is the Processing Block Instance List',
        'num_instances': len(pb_list),
        'instances': pb_list
    }


@APP.route('/ProcBlock/offline')
def offline_processing_blocks():
    """Return the list of offline processing blocks known to SDP."""
    # FIXME(BMo) should be able to use method on ProcessingBlockList.
    pb_ids = list()
    for sbi in (SchedulingBlockInstance(sbi) for sbi in
                SchedulingBlockInstanceList().active):
        pb_ids += sbi.get_pb_ids()
    pb_list = list(pb_id for pb_id in pb_ids
                   if ProcessingBlock(pb_id).type == 'offline')
    return {
        'message': 'This is the Processing Block Instance List',
        'num_instances': len(pb_list),
        'instances': pb_list
    }


@APP.route('/ProcBlock/realtime')
def realtime_processing_blocks():
    """Return list of realtime processing blocks known to SDP."""
    # FIXME(BMo) should be able to use method on ProcessingBlockList.
    pb_ids = list()
    for sbi in (SchedulingBlockInstance(sbi) for sbi in
                SchedulingBlockInstanceList().active):
        pb_ids += sbi.get_pb_ids()
    pb_list = list(pb_id for pb_id in pb_ids
                   if ProcessingBlock(pb_id).type == 'realtime')
    return {
        'message': 'This is the Processing Block Instance List',
        'num_instances': len(pb_list),
        'instances': pb_list
    }


@APP.route('/SchedBlock')
def scheduling_blocks():
    """Return list of Scheduling Block instances known to SDP."""
    sbi_list = SchedulingBlockInstanceList()
    return {
        'message': 'This is the Scheduling Block Instance List',
        'num_instances': sbi_list.num_active,
        'instances': sbi_list.active
    }


@APP.route('/version')
def version():
    """Return the Master version."""
    return {
        "message": "Version {}".format(__version__)
    }


@APP.route('/allowed_state_transitions')
def allowed_transitions():
    """Return the allowed state transitions."""
    return SDPState().allowed_state_transitions


@APP.route('/target_state')
def get_target_state():
    """Return the SDP target State."""
    sdp_state = SDPState()
    try:
        LOG.debug('getting target state')
        target_state = sdp_state.target_state
        LOG.debug('got(?) target state')
        if target_state is None:
            LOG.debug('target state set to none')
            return {'target_state': 'UNKNOWN',
                    'reason': 'database not initialised.'}
        LOG.debug(target_state)

        # Check the timestamp to be sure that the watchdog is alive
        LOG.debug('getting timestamp')
        state_tmstmp = sdp_state.current_timestamp
        target_tmstmp = sdp_state.target_timestamp
        if state_tmstmp is None or target_tmstmp is None:
            LOG.warning('Timestamp not available')
            return {'state': 'UNKNOWN',
                    'reason': 'Master Controller Services may have died.'}

        LOG.debug("State timestamp: %s", state_tmstmp.isoformat())
        LOG.debug("Target timestamp: %s", target_tmstmp.isoformat())
        if target_tmstmp < state_tmstmp:
            LOG.debug('timestamp okay')
            return {'target_state': target_state}

        LOG.warning('Timestamp for Master Controller Services is stale')
        return {'target_state': 'UNKNOWN',
                'reason': 'Master Controller Services may have died.'}
    except redis.exceptions.ConnectionError:
        LOG.debug('error connecting to DB')
        return {'state': 'UNKNOWN',
                'reason': 'Unable to connect to database.'}


@APP.route('/state', methods=['GET', 'PUT'])
def state():
    """Return the SDP State."""
    # pylint: disable=too-many-return-statements

    # These are the states we allowed to request
    # states = ('OFF', 'STANDBY', 'ON', 'DISABLE')
    # LOG.debug(states)

    # it could be that this is not necessary as a query for another
    # item may simply go through another route
    request_keys = ('state',)

    # db = masterClient()
    sdp_state = SDPState()
    if request.method == 'PUT':

        # Has the user used unknown keys in the query?
        unk_kys = [ky for ky in request.data.keys() if ky not in request_keys]

        # unk_kys should be empty
        if unk_kys:
            LOG.debug('Unrecognised keys in data')
            return (dict(error='Invalid request key(s) ({})'
                         .format(','.join(unk_kys)),
                         allowed_request_keys=request_keys),
                    status.HTTP_400_BAD_REQUEST)
        requested_state = request.data.get('state', '').lower()
        sdp_state = sdp_state.current_state
        states = sdp_state.allowed_state_transitions[sdp_state]
        if not states:
            LOG.warning('No allowed states - cannot continue')
            return (dict(error='No Allowed States',
                         message='No allowed state transition for {}'
                         .format(sdp_state)
                         ), status.HTTP_400_BAD_REQUEST)
        if requested_state not in states:
            LOG.debug('Invalid state: %s', requested_state)
            return ({'error': 'Invalid Input',
                     'message': 'Invalid state: {}'.format(requested_state),
                     'allowed_states': states},
                    status.HTTP_400_BAD_REQUEST)
        response = {'message': 'Accepted state: {}'.format(requested_state)}
        try:
            LOG.debug('Updating state, SDP state is: %s', sdp_state)

            # If different then update target state
            if sdp_state != requested_state:
                # db.target_state(requested_state)
                sdp_state.update_target_state(requested_state)

        except redis.exceptions.ConnectionError:
            LOG.debug('failed to connect to DB')
            response['error'] = 'Unable to connect to database.'
        except ValueError as err:
            LOG.debug('Error updating target state: %s', str(err))

        # if requested_state == 'OFF' the master controller
        # will deal with it, not this program.
        return response

    # GET - if the state in the database is OFF we want to replace it with
    # INIT
    try:
        LOG.debug('getting current state')
        current_state = sdp_state.current_state
        LOG.debug('got(?) current state')
        if current_state is None:
            LOG.debug('current state set to none')
            return {'state': 'UNKNOWN',
                    'reason': 'database not initialised.'}
        LOG.debug(current_state)
        # if current_state == 'OFF':
        # LOG.debug('current state off - set to init')
        # current_state = 'INIT'

        # Check the timestamp to be sure that the watchdog is alive
        LOG.debug('getting timestamp')
        state_tmstmp = sdp_state.current_timestamp
        target_tmstmp = sdp_state.target_timestamp
        if state_tmstmp is None or target_tmstmp is None:
            LOG.warning('Timestamp not available')
            return {'state': 'UNKNOWN',
                    'reason': 'Master Controller Services may have died.'}

        LOG.debug("State timestamp: %s", state_tmstmp.isoformat())
        LOG.debug("Target timestamp: %s", target_tmstmp.isoformat())
        # state_tmstmp = datetime.strptime(state_tmstmp,
        # '%Y/%m/%d %H:%M:%S.%f')
        # target_tmstmp = datetime.strptime(target_tmstmp,
        # '%Y/%m/%d %H:%M:%S.%f')
        if target_tmstmp < state_tmstmp:
            LOG.debug('timestamp okay')
            return {'state': current_state}

        LOG.warning(
            'Timestamp for Master Controller Services is stale')
        return {'state': 'UNKNOWN',
                'reason': 'Master Controller Services may have died.'}
    except redis.exceptions.ConnectionError:
        LOG.debug('error connecting to DB')
        return {'state': 'UNKNOWN',
                'reason': 'Unable to connect to database.'}
