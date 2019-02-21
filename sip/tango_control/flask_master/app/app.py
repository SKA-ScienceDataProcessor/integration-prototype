# -*- coding: utf-8 -*-
"""SIP SDP Master Interface Service, Restful version."""

from random import randrange
import time
from http import HTTPStatus
import jsonschema

from flask import request
from flask_api import FlaskAPI

from sip_config_db.scheduling import ProcessingBlockList, \
    SchedulingBlockInstanceList
from sip_config_db.states import SDPState
from sip_config_db.scheduling import Subarray, SubarrayList
from sip_logging import init_logger
from .release import LOG, __service_id__, __version__

init_logger('flask.logging.wsgi_errors_stream')
init_logger()

APP = FlaskAPI(__name__)

START_TIME = time.time()


def _check_status(sdp_state):
    """SDP Status check.

    Do all the tests to determine, if the SDP state is
    "broken", what could be the cause, and return a
    suitable status message to be sent back by the calling
    function.
    """
    try:
        errval = "error"
        errdict = dict(state="unknown", reason="unknown")
        if sdp_state.current_state == "unknown":
            errdict['reason'] = 'database not initialised.'
            LOG.debug('Current state is unknown;')
            LOG.debug('Target state is %s;', sdp_state.target_state)
            LOG.debug('Current state timestamp is %s;',
                      sdp_state.current_timestamp)
        elif sdp_state.current_state is None:
            errdict['reason'] = 'Master Controller Services may have died.'
            LOG.debug('Current state is NONE;')
            LOG.debug('Target state is %s;', sdp_state.target_state)
            LOG.debug('Current state timestamp is %s;',
                      sdp_state.current_timestamp)
        elif sdp_state.target_state is None:
            errdict['reason'] = 'Master Controller Services may have died.'
            LOG.debug('Current state is  %s;',
                      sdp_state.current_state)
            LOG.debug('Target state is NONE;')
            LOG.debug('Current state timestamp is %s;',
                      sdp_state.current_timestamp)
            LOG.debug('Target state timestamp is %s;',
                      sdp_state.target_timestamp)
        elif sdp_state.current_timestamp is None:
            errdict['reason'] = 'Master Controller Services may have died.'
            LOG.debug('Current state is  %s;',
                      sdp_state.current_state)
            LOG.debug('Target state is %s;', sdp_state.target_state)
            LOG.debug('Current state timestamp is NONE')
            LOG.debug('Target state timestamp is %s;',
                      sdp_state.target_timestamp)
        elif sdp_state.target_timestamp is None:
            errdict['reason'] = 'Master Controller Services may have died.'
            LOG.debug('Current state is  %s;',
                      sdp_state.current_state)
            LOG.debug('Target state is %s;', sdp_state.target_state)
            LOG.debug('Current state timestamp is %s;',
                      sdp_state.current_timestamp)
            LOG.debug('Target state timestamp is NONE')
        elif sdp_state.current_timestamp < sdp_state.target_timestamp:
            errdict['reason'] = \
                'Timestamp for Master Controller Services is stale.'
            LOG.debug('Current state is  %s;',
                      sdp_state.current_state)
            LOG.debug('Target state is %s;', sdp_state.target_state)
            LOG.debug('Current state timestamp is %s;',
                      sdp_state.current_timestamp)
            LOG.debug('Target state timestamp is %s;',
                      sdp_state.target_timestamp)
        else:
            errval = "okay"
    except ConnectionError as err:
        errdict['reason'] = err
        LOG.debug('Connection Error %s', err)
    return errval, errdict


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
                    "Link": "SDP target state",
                    "href": "{}target_state".format(request.url)
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
                },
                {
                    "Link": "Resource Availability",
                    "href": "{}resource_availability".format(request.url)
                },
                {
                    "Link": "Configure SBI",
                    "href": "{}configure_sbi".format(request.url)
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
    try:
        sdp_state = SDPState()
        return sdp_state.allowed_target_states[sdp_state.current_state]
    except KeyError:
        LOG.error("Key Error")
        return dict(state="KeyError", reason="KeyError")


@APP.route('/state', methods=['GET'])
def get_state():
    """SDP State.

    Return current state; target state and allowed
    target states.
    """
    sdp_state = SDPState()
    errval, errdict = _check_status(sdp_state)
    if errval == "error":
        LOG.debug(errdict['reason'])
        return dict(
            current_state="unknown",
            target_state="unknown",
            last_updated="unknown",
            reason=errdict['reason']
        )
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


@APP.route('/state/target', methods=['GET'], strict_slashes=False)
@APP.route('/target_state', methods=['GET'], strict_slashes=False)
def get_target_state():
    """SDP target State.

    Returns the target state; allowed target states and time updated
    """
    sdp_state = SDPState()
    errval, errdict = _check_status(sdp_state)
    if errval == "error":
        LOG.debug(errdict['reason'])
        return dict(
            current_target_state="unknown",
            last_updated="unknown",
            reason=errdict['reason']
        )
    LOG.debug('Getting target state')
    target_state = sdp_state.target_state
    LOG.debug('Target state = %s', target_state)
    return dict(
        current_target_state=target_state,
        allowed_target_states=sdp_state.allowed_target_states[
            sdp_state.current_state],
        last_updated=sdp_state.target_timestamp.isoformat())


@APP.route('/state/current', methods=['GET'])
def get_current_state():
    """Return the SDP State and the timestamp for when it was updated."""
    sdp_state = SDPState()
    errval, errdict = _check_status(sdp_state)
    if errval == "error":
        LOG.debug(errdict['reason'])
        return dict(
            current_state="unknown",
            last_updated="unknown",
            reason=errdict['reason']
        )
    LOG.debug('Current State: %s', sdp_state.current_state)
    LOG.debug('Current State last updated: %s',
              sdp_state.current_timestamp.isoformat())
    return dict(
        current_state=sdp_state.current_state,
        last_updated=sdp_state.current_timestamp.isoformat()
    ), HTTPStatus.OK


@APP.route('/state/target', methods=['PUT'], strict_slashes=False)
@APP.route('/target_state', methods=['PUT'], strict_slashes=False)
def put_target_state():
    """SDP target State.

    Sets the target state
    """
    sdp_state = SDPState()
    errval, errdict = _check_status(sdp_state)
    if errval == "error":
        LOG.debug(errdict['reason'])
        rdict = dict(
            current_state="unknown",
            last_updated="unknown",
            reason=errdict['reason']
        )
    else:
        try:
            LOG.debug('request is of type %s', type(request))
            request_data = request.data
            LOG.debug('request data is of type %s', type(request_data))
            LOG.debug('request is %s', request_data)
            request_data = request.data
            target_state = request_data['value'].lower()
            sdp_state.update_target_state(target_state)
            rdict = dict(message='Target state successfully updated to {}'
                         .format(target_state))
        except ValueError as error:
            rdict = dict(error='Failed to set target state',
                         reason=str(error))
        except RuntimeError as error:
            rdict = dict(error='RunTime error',
                         reason=str(error))
    return rdict


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


@APP.route('/resource_availability')
def resource_availability():
    """Return the Resource Availability.

    (next available resource? number of available resouces?).
    Currently unable to calculate this so send back a random number.
    This is identical to the TANGO function.
    """
    return dict(nodes_free=randrange(1, 500))


@APP.route('/configure_sbi', methods=['GET'])
@APP.route('/configure_sbi', methods=['PUT'])
@APP.route('/configure_sbi', methods=['POST'])
def configure_sbi():
    """Configure an SBI using POSTed configuration."""
    # Need an ID for the subarray - guessing I just get
    # the list of inactive subarrays and use the first
    inactive_list = SubarrayList().inactive
    request_data = request.data
    LOG.debug('request is of type %s', type(request_data))
    try:
        sbi = Subarray(inactive_list[0])
        sbi.activate()
        sbi.configure_sbi(request_data)
    except jsonschema.exceptions.ValidationError as error:
        LOG.error('Error configuring SBI: %s', error)
        return dict(path=error.absolute_path.__str__(),
                    schema_path=error.schema_path.__str__(),
                    message=error.message)
    return dict(status="Accepted SBI: {}".format(sbi.id))
