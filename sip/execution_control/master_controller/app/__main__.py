# -*- coding: utf-8 -*-
"""Master Controller Service.

This version polls REDIS Events rather than the database directly.

FIXME(BMo): Make sure this is resilient to the REDIS database connection
            not being present.
"""
import time
import sched
import random
import argparse

from sip_logging import init_logger
from sip_config_db.states import SDPState, ServiceState
from sip_config_db.states.services import get_service_state_list

from .__init__ import __service_id__, LOG, __subsystem__, __service_name__, \
    __version__


SCHEDULER = sched.scheduler(time.time, time.sleep)


def _generate_random_service_failure():
    """Randomly generate a fault or alarm state for one of the substates."""
    service_states = get_service_state_list()
    roll = random.uniform(0, 1)
    if 0.9 > roll >= 0.5:
        service = random.choice(service_states)
        LOG.debug('Generating a alarm on service %s', service.id)
        service.update_current_state('alarm')

    if roll >= 0.9:
        service = random.choice(service_states)
        LOG.debug('Generating a fault on service %s', service.id)
        service.update_current_state('fault')

    # Don't roll the dice again until some time in the future.
    delay = random.uniform(120, 300)
    SCHEDULER.enter(delay, 1, _generate_random_service_failure)


def _update_sdp_current_state():
    """Update the current state of SDP based on the current state of services.

    Look for events from updating current state for each component and
    set SDP current state when all are set to the target state
    """
    LOG.debug('Waiting on service states.')
    sdp_state = SDPState()
    state_queue = sdp_state.get_event_queue(subscriber=__service_name__)
    services = get_service_state_list()

    service_ready = dict((service.id, False) for service in services)

    event = state_queue.get()
    if event and event.type == 'current_state_updated':
        service_id = event.object_id

        LOG.debug('handling event %s (service: %s)', event.id, service_id)
        service_ready[service_id] = True

        if all(service_ready.values()):
            sdp_state.update_current_state(sdp_state.target_state)
            LOG.debug("SDP current state updated to commanded target state %s",
                      sdp_state.target_state)

            # Go back to check_event_queue
            SCHEDULER.enter(0, 1, _process_events)
        else:
            SCHEDULER.enter(0.5, 1, _update_sdp_current_state)

    else:
        SCHEDULER.enter(0.5, 1, _update_sdp_current_state)


def _update_service_current_state(service: ServiceState):
    """Update the current state of a service.

    Updates the current state of services after their target state has changed.

    Args:
        service (ServiceState): Service state object to update

    """
    LOG.debug("Setting current state from target state for %s", service.id)
    service.update_current_state(service.target_state)


def _update_services_target_state(sdp_target_state: str):
    """Update the target states of services based on SDP target state.

    When we get a new target state this function is called to ensure
    components receive the target state(s) and/or act on them.

    Args:
        sdp_target_state (str): Target state of SDP

    # """
    sdp_state = SDPState()
    service_states = get_service_state_list()

    # Set the target state of services
    for service in service_states:
        LOG.debug('Setting the target state of %s to be %s', service.id,
                  sdp_target_state)
        service.update_target_state(sdp_target_state)

        # Schedule a call to update the current state of each service.
        delay = random.uniform(0.2, 3)
        SCHEDULER.enter(delay, 1, _update_service_current_state)

        # Schedule a call to update the current state of the SDP.
        delay = random.uniform(0.4, 0.5)
        SCHEDULER.enter(delay, 1, _update_sdp_current_state)

    else:
        LOG.debug('no need to wait on service states')
        sdp_state.update_current_state(sdp_state.target_state)
        SCHEDULER.enter(0, 1, _process_events)


def _handle_sdp_target_state_updated(sdp_state: SDPState):
    """Respond to an SDP target state change event.

    This function sets the current state of SDP to the target state if that is
    possible.

    TODO(BMo) This cant be done as a blocking function as it is here!
    """
    LOG.info('Handling SDP target state updated event...')
    LOG.info('SDP target state: %s', sdp_state.target_state)

    # Map between the SDP target state and the service target state?
    if sdp_state.target_state == 'off':
        _update_services_target_state('off')

    # TODO: Work out if the state of SDP has reached the target state.

    # If yes, update the current state.
    sdp_state.update_current_state(sdp_state.target_state)


def _process_events():
    """Poll the Event Queue for state change events.

    Call handle_event if there is an event of type updated.
    Reset the scheduler to call this function again in 1 second.
    """
    LOG.debug('Processing state events ...')
    sdp_state = SDPState()
    state_events = sdp_state.get_event_queue(subscriber=__service_name__)
    event = state_events.get()
    if event:
        LOG.into('Event detected object_type = %s, object_id = %s',
                 event.object_type, event.object_id)

        # The SDP target state changes.
        if event.object_id == 'SDP' and event.type == 'target_state_updated':
            LOG.info('Target state of SDP updated! (event id = %s)',
                     event.id)
            _handle_sdp_target_state_updated(sdp_state)

        # A service state changes current state
        if event.object_id != 'SDP' and event.type == 'current_state_updated':
            LOG.info('Current state of service %s updated! '
                     '(event id = %s)', event.object_id, event.id)
            new_service_state = event.data['state']
            if new_service_state in ['fault', 'alarm']:
                LOG.warning('Service %s has an %s', event.object_id,
                            new_service_state)
                # Respond to the service state change by updating the SDP state.
                # sdp_state.update_current_state(new_service_state)
                # TODO(BMo) need to review logic here.

    # Return to this function after one second
    SCHEDULER.enter(1, 1, _process_events)


def _parse_args():
    """Command line parser."""
    parser = argparse.ArgumentParser(description='{} service.'.
                                     format(__service_id__))
    parser.add_argument('--random_errors', action='store_true',
                        help='Enable random errors')
    parser.add_argument('-v', action='store_true',
                        help='Verbose mode (enable debug printing)')
    parser.add_argument('-vv', action='store_true', help='Extra verbose mode')
    args = parser.parse_args()

    # if args.vv:
    #     init_logger(log_level='DEBUG', show_log_origin=True)
    # elif args.v:
    #     init_logger(log_level='DEBUG')
    # else:
    #     init_logger(log_level='INFO')
    init_logger(log_level='DEBUG', show_log_origin=True)

    return args


def _init(sdp_state: SDPState):
    """Initialise the Master Controller Service."""
    # Parse command line arguments.
    LOG.info("Initialising: %s", __service_id__)

    # FIXME(BMo) There is a bug when SDP or services 'start' in the 'off'
    # state. At the moment it is impossible to transition out of this.

    # FIXME(BMo) **Hack** Register all services or if already registered do
    # nothing (this is handled by the ServiceState object).
    _services = [
        "ExecutionControl:MasterController:1.1.3",
        "ExecutionControl:ProcessingController:1.1.3",
        "ExecutionControl:ProcessingBlockController:1.1.3",
        "ExecutionControl:ConfigurationDatabase:4.0.6",
        "ExecutionControl:ProcessingBlockControllerBroker:4.0.6",
        "ExecutionControl:ProcessingBlockControllerBackend:4.0.6",
        "TangoControl:SDPMaster:1.1.3",
        "TangoControl:Subarrays:1.1.3",
        "TangoControl:ProcessingBlocks:1.1.3",
        "TangoControl:Database:1.0.4",
        "TangoControl:MySQL:1.0.3",
        "TangoControl:FlaskMaster:1.1.3"
    ]
    for service_id in _services:
        subsystem, name, version = service_id.split(':')
        ServiceState(subsystem, name, version)

    # Mark the SDP state as init.
    # FIXME(BMo) This is not right as we want to allow for recovery from
    # failure without just reinitialising...!? ie. respect the old sate
    # NOTE: If the state is 'off' we will want to reset the database
    # with 'skasip_config_db_init --clear'
    if sdp_state.current_state in ['unknown']:
        try:
            sdp_state.update_current_state('init', force=True)
        except ValueError as error:
            LOG.critical('Unable to set the State of SDP to init! %s',
                         str(error))

    service_states = get_service_state_list()

    # FIXME(BMo) **Hack** Mark all Services in the 'unknown' state as
    # initialising.
    for service_state in service_states:
        if service_state.current_state in ['unknown']:
            service_state.update_current_state('init', force=True)

    # FIXME(BMo) **Hack** After 'checking' that the services are 'on' set
    # their state on 'on' after a short delay.
    # FIXME(BMo) This check should not be serialised!!! (should be part of the
    # event loop)
    for service_state in service_states:
        if service_state.current_state == 'init':
            time.sleep(random.uniform(0, 0.2))
            service_state.update_current_state('on')

    # FIXME(BMo): **Hack** Now the all services are on, set the sate of SDP to
    # 'standby'
    # FIXME(BMo) This should also be part of the event loop.
    services_on = [service.current_state == 'on' for service in service_states]
    if all(services_on):
        LOG.info('All Services are online!.')
        sdp_state.update_current_state('standby')
    else:
        LOG.critical('Master Controller failed to initialise.')

    return service_states


def main():
    """Start the Master Controller service.

    Logging, scheduling, database and database events are all set up here.

    DB event queue polling is done by the check_event_queue() which is
    registered with a Python Event Scheduler
    (https://docs.python.org/3/library/sched.html)
    """
    # Parse command line args.
    args = _parse_args()
    LOG.info("Starting: %s", __service_id__)

    sdp_state = SDPState()

    # Subscribe to state change events.
    # FIXME(BMo) This API is unfortunate as it looks like we are only
    # subscribing to sdp_state events.
    LOG.info('Subscribing to state change events (subscriber = %s)',
             __service_name__)
    sdp_state.subscribe(subscriber=__service_name__)

    # Initialise the service.
    _init(sdp_state)

    # Enter a pseudo event-loop (using Sched) to monitor for state change
    # events
    # (Also random set services into a fault or alarm state if enabled)
    try:
        # Schedule function to check for state change events.
        SCHEDULER.enter(0, 1, _process_events)

        if args.random_errors:
            # Schedule a random error (fault or alarm)
            _delay = random.uniform(5, 10)
            LOG.debug('Scheduling a random error in %.2f s', _delay)
            SCHEDULER.enter(_delay, 1, _generate_random_service_failure)

            SCHEDULER.run()
    except KeyboardInterrupt as err:
        LOG.debug('Keyboard Interrupt %s', err)
        LOG.info('Exiting!')


def main2():
    """New Main."""
    # Parse command line args.
    args = _parse_args()
    LOG.info("Starting: %s", __service_id__)

    sdp_state = SDPState()

    # Subscribe to state change events.
    # FIXME(BMo) This API is unfortunate as it looks like we are only
    # subscribing to sdp_state events.
    LOG.info('Subscribing to state change events (subscriber = %s)',
             __service_name__)
    state_events = sdp_state.subscribe(subscriber=__service_name__)

    # Initialise the service.
    service_states = _init(sdp_state)

    # Enter a pseudo event-loop (using Sched) to monitor for state change
    # events
    # (Also random set services into a fault or alarm state if enabled)
    LOG.info('Finished initialising!')
    LOG.info('Responding to state change events ...')
    try:
        while True:
            time.sleep(0.2)
            event = state_events.get()
            if event:
                LOG.debug('>> event detected: %s %s %s', event.object_id,
                          event.type, event.data)
                if event.object_id == 'SDP' and \
                        event.type == 'target_state_updated':
                    LOG.info('SDP target state changed to %s',
                             sdp_state.target_state)

                    # If the sdp is already in the target state do nothing
                    if sdp_state.target_state == sdp_state.current_state:
                        LOG.warning('SDP already in %s state',
                                    sdp_state.current_state)
                        continue

                    # If asking SDP to turn off, also turn off services.
                    if sdp_state.target_state == 'off':
                        LOG.info('Turning off services!')
                        for service_state in service_states:
                            service_state.update_target_state('off')
                            service_state.update_current_state('off')

                    LOG.info('Processing target state change request ...')
                    time.sleep(0.05)
                    LOG.info('Done processing target state change request!')

                    # Assuming that the SDP has responding to the target
                    # target state command by now, set the current state
                    # to the target state.
                    try:
                        sdp_state.update_current_state(
                            sdp_state.target_state)
                    except ValueError as error:
                        LOG.critical('Unable to update current state: %s',
                                     str(error))

                # TODO(BMo) function to watch for changes in the \
                # current state of services and update the state of SDP
                # accordingly.

    except KeyboardInterrupt as err:
        LOG.debug('Keyboard Interrupt %s', err)
        LOG.info('Exiting!')


if __name__ == '__main__':
    main2()
