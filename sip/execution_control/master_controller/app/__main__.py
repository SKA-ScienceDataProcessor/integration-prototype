# -*- coding: utf-8 -*-
"""Master Controller Service.

This version polls REDIS Events rather than the database directly.

FIXME(BMo): Make sure this is resilient to the REDIS database connection
            not being present.
"""
# FIXME(BMo) Review use of globals
# pylint: disable=global-statement
from time import time, sleep
from sched import scheduler
import random
import argparse

from sip_logging import init_logger
from sip_config_db.states import SDPState, ServiceState
from sip_config_db.states.services import get_service_state_list

from .__init__ import __service_id__, LOG, __subsystem__, __service_name__, \
    __version__


SDP_STATE = SDPState()
SERVICES = get_service_state_list()
SERVICE_READY = dict((service.id, False) for service in SERVICES)
EVENT_QUEUE = SDPState().subscribe(subscriber=__service_id__)
SCHEDULER = scheduler(time, sleep)


def generate_random_service_failure():
    """Randomly generate a fault or alarm state for one of the substates."""
    LOG.debug('Randomly generate a fault or alarm on a service.')
    state = (None, None, None, None, None, 'fault', 'alarm')[
        random.randint(0, 6)]

    if state is not None:
        service = random.choice(SERVICES)
        LOG.warning('Setting %s to %s', service.id, state)
        service.update_current_state(state)

    SCHEDULER.enter(random.uniform(0, 500), 1, generate_random_service_failure)


def update_sdp_current_state():
    """Update the current state of SDP based on the current state of services.

    Look for events from updating current state for each component and
    set SDP current state when all are set to the target state
    """
    global SERVICE_READY
    LOG.debug('Waiting on service states.')

    event = EVENT_QUEUE.get()
    if event and event.type == 'current_state_updated':

        service_id = event.object_id
        LOG.debug('handling event %s (service: %s)', event.id, service_id)
        SERVICE_READY[service_id] = True

        if all(SERVICE_READY.values()):
            SDP_STATE.update_current_state(SDP_STATE.target_state)
            LOG.debug("SDP current state updated to commanded target state %s",
                      SDP_STATE.target_state)

            SERVICE_READY = dict((service.id, False) for service in SERVICES)

            # Go back to check_event_queue
            SCHEDULER.enter(0, 1, check_event_queue)
        else:
            SCHEDULER.enter(0.5, 1, update_sdp_current_state)

    else:
        SCHEDULER.enter(0.5, 1, update_sdp_current_state)


def update_service_current_state(service: ServiceState):
    """Update the current state of a service.

    Updates the current state of services after their target state has changed.

    Args:
        service (ServiceState): Service state object to update

    """
    LOG.debug("Setting current state from target state for %s", service.id)
    service.update_current_state(service.target_state)


def update_services(sdp_target_state):
    """Update target states of services based on SDP target state.

    When we get a new target state this function is called to ensure
    components receive the target state(s) and act on them.

    Args:
        sdp_target_state (str): Target state of SDP

    """
    global SERVICE_READY

    # FIXME(BMo) better name for the following function (get_service_states?)
    services = get_service_state_list()

    wait_on_states = False

    for service in services:
        LOG.debug('Setting target state of %s to be %s', service.id,
                  sdp_target_state)

        _current_state = service.current_state

        if _current_state == sdp_target_state:
            SERVICE_READY[service.id] = True

        else:
            service.update_target_state(sdp_target_state)
            LOG.debug('Scheduling %s current state to be updated', service.id)
            SCHEDULER.enter(random.uniform(0, 5), 1,
                            update_service_current_state, argument=(service,))
            SERVICE_READY[service.id] = False
            wait_on_states = True

    if wait_on_states:
        SCHEDULER.enter(0.5, 1, update_sdp_current_state)

    else:
        LOG.debug('no need to wait on service states')
        SDP_STATE.update_current_state(SDP_STATE.target_state)
        SCHEDULER.enter(0, 1, check_event_queue)


def handle_sdp_target_state_updated_event():
    """Respond to an SDP target state change event.

    The target state may only be honored if the current state
    is a certain value. The correct values can be obtained from
    the database API so that we do not need to keep separate
    copies of the legal transitions.
    """
    LOG.info('Handling SDP target state updated event...')
    target_state = SDP_STATE.target_state
    current_state = SDP_STATE.current_state
    allowed_transitions = SDP_STATE.allowed_state_transitions[current_state]

    if target_state is None:
        LOG.critical('Target state does not exist in database.')

    LOG.info('SDP target state: %s', target_state)

    if target_state == current_state:
        return

    if target_state not in allowed_transitions:
        LOG.warning('Target state %s not in valid list (%s)',
                    target_state, allowed_transitions)
        return

    if target_state == 'standby':
        update_services('on')
    else:
        update_services(target_state)


def check_event_queue():
    """Poll the Event Queue for state change events.

    Call handle_event if there is an event of type updated.
    Reset the scheduler to call this function again in 1 second.
    """
    LOG.debug('Checking for state events ..')
    event = EVENT_QUEUE.get()
    if event:

        LOG.debug('Event detected! object_type = %s, object_id = %s',
                  event.object_type, event.object_id)

        # SDP target state change events
        if event.object_id == 'SDP' and event.type == 'target_state_updated':
            LOG.info('Target state of SDP updated! (event id = %s)',
                     event.id)
            handle_sdp_target_state_updated_event()
            return

        # Service current state change events
        if event.type == 'current_state_updated':
            LOG.debug('Current state of service %s updated! '
                      '(event id = %s)', event.object_id, event.id)
            new_state = event.data['state']
            if new_state in ('fault', 'alarm'):
                LOG.warning('We have a %s on %s', new_state,
                            event.object_id)
                if SDP_STATE.current_state not in ('disable', 'fault',
                                                   'off'):
                    SDP_STATE.update_current_state(new_state)

    # Return to this function after one second
    SCHEDULER.enter(1, 1, check_event_queue)


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

    if args.vv:
        init_logger(log_level='DEBUG', show_log_origin=True)
    elif args.v:
        init_logger(log_level='DEBUG')
    else:
        init_logger(log_level='INFO')

    return args


def main():
    """Start the Master Controller service.

    Logging, scheduling, database and database events are all set up here.

    DB event queue polling is done by the check_event_queue() which is
    registered with a Python Event Scheduler
    (https://docs.python.org/3/library/sched.html)
    """
    # Parse command line arguments.
    args = _parse_args()

    LOG.info("Starting service: %s", __service_id__)
    state = ServiceState(__subsystem__, __service_name__, __version__)
    state.update_current_state('on')

    # FIXME(BMo) If SDP is 'off' make sure it is set it to init and then
    # standby when services are started. As services start they should
    # either be set to 'on' by this service or by themselves.

    # FIXME(BMo) There is a bug when SDP starts in the 'off' state.

    try:

        # Set current state of all SDP Services to init (if unknown)
        for service in get_service_state_list():
            if service.current_state == 'unknown':
                LOG.debug("Setting current of service %s to: init", service.id)
                service.update_current_state('init')

        # Set the current state of SDP to init (if unknown)
        if SDP_STATE.current_state == 'unknown':
            LOG.debug("Setting SDP state to: init")
            SDP_STATE.update_current_state('init')

        # Once the state of all SDP services is on, set the SDP state to
        # standby.
        for service in get_service_state_list():
            if service.current_state == 'on':
                LOG.debug("Setting current of SDP %s to: standby", service.id)
                SDP_STATE.update_current_state('standby')

        # Schedule function to check for state change events.
        SCHEDULER.enter(0, 1, check_event_queue)

        if args.random_errors:
            # Schedule a random error (fault or alarm)
            _delay = random.uniform(5, 10)
            LOG.debug('Scheduling a random error in %.2f s', _delay)
            SCHEDULER.enter(_delay, 1, generate_random_service_failure)

        SCHEDULER.run()
    except KeyboardInterrupt as err:
        LOG.debug('Keyboard Interrupt %s', err)
        LOG.info('Exiting!')


if __name__ == '__main__':
    # TODO(BMo) wait for DB to be available (maybe not needed if not using \
    # globals for the db)
    main()
