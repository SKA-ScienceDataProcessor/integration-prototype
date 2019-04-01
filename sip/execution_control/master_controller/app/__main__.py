# -*- coding: utf-8 -*-
"""Master Controller Service.

This version polls REDIS Events rather than the database directly.
"""
import argparse
import random
import time
from typing import List
import urllib
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway

from sip_config_db._events.event import Event
from sip_config_db.states import SDPState, ServiceState
from sip_config_db.states.services import get_service_state_list
from sip_logging import init_logger
from .__init__ import LOG, __service_id__, __service_name__

# Create a collector registry for alarm gauges
COLLECTOR_REGISTRY = CollectorRegistry()

# Create a gauge for service state alarms. Its normal value is zero and
# we set it to 1 if there is a service in the alarm state.
SIP_STATE_ALARM = Gauge('sip_state', 'Gauge for generating SIP state alarms',
                        registry=COLLECTOR_REGISTRY)


def _update_service_current_state(service: ServiceState):
    """Update the current state of a service.

    Updates the current state of services after their target state has changed.

    Args:
        service (ServiceState): Service state object to update

    """
    LOG.debug("Setting current state from target state for %s", service.id)
    service.update_current_state(service.target_state)


def _update_services_instant_gratification(sdp_target_state: str):
    """For demonstration purposes only.

    This instantly updates the services current state with the
    target state, rather than wait on them or schedule random delays
    in bringing them back up.
    """
    service_states = get_service_state_list()

    # Set the target state of services
    for service in service_states:
        if service.current_state != sdp_target_state:
            LOG.debug('Setting the current state of %s to be %s', service.id,
                      sdp_target_state)
            service.update_current_state(sdp_target_state)

    # Should we be picking up the events?


def _update_services_target_state(sdp_target_state: str):
    """Update the target states of services based on SDP target state.

    When we get a new target state this function is called to ensure
    components receive the target state(s) and/or act on them.

    Args:
        sdp_target_state (str): Target state of SDP

    """
    service_states = get_service_state_list()

    # Set the target state of services
    for service in service_states:
        if service.current_state != sdp_target_state:
            LOG.debug('Setting the target state of %s to be %s', service.id,
                      sdp_target_state)
            service.update_target_state(sdp_target_state)

    # The function below should not be called here as it is updating the
    # **CURRENT** state of services!
    # LOG.debug("Simulate services changing state ...")
    # _update_services_instant_gratification(sdp_target_state)


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
        init_logger(logger_name='sip.ec.master_controller', log_level='DEBUG')
    else:
        init_logger(log_level='INFO')

    return args


def _init(sdp_state: SDPState):
    """Initialise the Master Controller Service.

    Performs the following actions:
    1. Registers ServiceState objects into the Config Db.
    2. If initialising for the first time (unknown state),
       sets the SDPState to 'init'
    3. Initialises the state of Services, if running for the first time
       (their state == unknown)
    4. Waits some time and sets the Service states to 'on'. This emulates
       waiting for Services to become available.
    5. Once all services are 'on', sets the SDP state to 'standby'.

    """
    # Parse command line arguments.
    LOG.info("Initialising: %s", __service_id__)

    # FIXME(BMo) There is a bug when SDP or services 'start' in the 'off'
    # state. At the moment it is impossible to transition out of this.

    # FIXME(BMo) **Hack** Register all services or if already registered do
    # nothing (this is handled by the ServiceState object).
    _services = [
        "ExecutionControl:AlarmReceiver:1.0.0",
        "ExecutionControl:AlertManager:1.0.0",
        "ExecutionControl:ConfigurationDatabase:5.0.1",
        "ExecutionControl:MasterController:1.3.0",
        "ExecutionControl:ProcessingController:1.2.6",
        "ExecutionControl:ProcessingBlockController:1.3.0",
        "TangoControl:Database:1.0.4",
        "TangoControl:MySQL:1.0.3",
        "TangoControl:SDPMaster:1.2.1",
        "TangoControl:Subarrays:1.2.0",
        "TangoControl:ProcessingBlocks:1.2.0",
        "Platform:Kafka:2.1.1",
        "Platform:Prometheus:1.0.0",
        "Platform:PrometheusPushGateway:0.7.0",
        "Platform:RedisCommander:210.0.0",
        "Platform:Zookeeper:3.4.13"
    ]
    for service_id in _services:
        subsystem, name, version = service_id.split(':')
        ServiceState(subsystem, name, version)

    # If the SDP state is 'unknown', mark the SDP state as init.
    # FIXME(BMo) This is not right as we want to allow for recovery from
    # failure without just reinitialising...!? ie. respect the old sate
    # NOTE: If the state is 'off' we will want to reset the database
    # with 'skasip_config_db_init --clear'
    if sdp_state.current_state in ['unknown', 'off']:
        try:
            LOG.info("Setting the SDPState to 'init'")
            sdp_state.update_current_state('init', force=True)
        except ValueError as error:
            LOG.critical('Unable to set the State of SDP to init! %s',
                         str(error))

    LOG.info("Updating Service States")
    service_state_list = get_service_state_list()

    # FIXME(BMo) **Hack** Mark all Services in the 'unknown' state as
    # initialising.
    for service_state in service_state_list:
        if service_state.current_state in ['unknown', 'off']:
            service_state.update_current_state('init', force=True)

    # FIXME(BMo) **Hack** After 'checking' that the services are 'on' set
    # their state on 'on' after a short delay.
    # FIXME(BMo) This check should not be serialised!!! (should be part of the
    # event loop)
    for service_state in service_state_list:
        if service_state.current_state == 'init':
            time.sleep(random.uniform(0, 0.2))
            service_state.update_current_state('on')

    # FIXME(BMo): **Hack** Now the all services are on, set the sate of SDP to
    # 'standby'
    # FIXME(BMo) This should also be part of the event loop.
    services_on = [service.current_state == 'on'
                   for service in service_state_list]
    if all(services_on):
        LOG.info('All Services are online!.')
        sdp_state.update_current_state('standby')
    else:
        LOG.critical('Master Controller failed to initialise.')

    return service_state_list


def _process_event(event: Event, sdp_state: SDPState,
                   service_states: List[ServiceState]):
    """Process a SDP state change event."""
    LOG.debug('Event detected! (id : "%s", type: "%s", data: "%s")',
              event.object_id, event.type, event.data)

    if event.object_id == 'SDP' and event.type == 'current_state_updated':
        LOG.info('SDP current state updated, no action required!')

    if event.object_id == 'SDP' and event.type == 'target_state_updated':
        LOG.info("SDP target state changed to '%s'",
                 sdp_state.target_state)

        # If the sdp is already in the target state do nothing
        if sdp_state.target_state == sdp_state.current_state:
            LOG.warning('SDP already in %s state',
                        sdp_state.current_state)
            return

        _update_services_target_state(sdp_state.target_state)

        # If asking SDP to turn off, also turn off services.
        if sdp_state.target_state == 'off':
            LOG.info('Turning off services!')
            for service_state in service_states:
                service_state.update_target_state('off')
                service_state.update_current_state('off')

        LOG.info('Processing target state change request ...')
        time.sleep(0.1)
        LOG.info('Done processing target state change request!')

        # Assuming that the SDP has responding to the target
        # target state command by now, set the current state
        # to the target state.
        sdp_state.update_current_state(sdp_state.target_state)

        if sdp_state.current_state == 'alarm':
            LOG.debug('raising SDP state alarm')
            SIP_STATE_ALARM.set(1)
        else:
            SIP_STATE_ALARM.set(0)
        try:
            # FIXME(BMo) the pushgateway host should not be hardcoded!
            push_to_gateway('platform_pushgateway:9091', job='SIP',
                            registry=COLLECTOR_REGISTRY)
        except urllib.error.URLError:
            LOG.warning("Unable to connect to the Alarms service!")

    # TODO(BMo) function to watch for changes in the \
    # current state of services and update the state of SDP
    # accordingly.


def _process_state_change_events():
    """Process events relating to the overall state of SDP.

    This function starts and event loop which continually checks for
    and responds to SDP state change events.
    """
    sdp_state = SDPState()
    service_states = get_service_state_list()
    state_events = sdp_state.get_event_queue(subscriber=__service_name__)
    state_is_off = sdp_state.current_state == 'off'

    counter = 0
    while True:
        time.sleep(0.1)
        if not state_is_off:

            # *Hack* to avoid problems with historical events not being
            # correctly handled by EventQueue.get(), replay old events every
            # 10s
            # - see issue #54
            if counter % 1000 == 0:
                LOG.debug('Checking published events ... %d', counter / 1000)
                _published_events = state_events.get_published_events(
                    process=True)
                for _state_event in _published_events:
                    _process_event(_state_event, sdp_state, service_states)
            else:
                _state_event = state_events.get()
                if _state_event:
                    _process_event(_state_event, sdp_state, service_states)
                    state_is_off = sdp_state.current_state == 'off'
            counter += 1


def main():
    """Merge temp_main and main."""
    # Parse command line args.
    _parse_args()
    LOG.info("Starting: %s", __service_id__)

    # Subscribe to state change events.
    # FIXME(BMo) This API is unfortunate as it looks like we are only
    # subscribing to sdp_state events.
    LOG.info('Subscribing to state change events (subscriber = %s)',
             __service_name__)
    sdp_state = SDPState()
    _ = sdp_state.subscribe(subscriber=__service_name__)

    # Initialise the service.
    _ = _init(sdp_state)
    LOG.info('Finished initialising!')

    # Enter a pseudo event-loop (using Sched) to monitor for state change
    # events
    # (Also random set services into a fault or alarm state if enabled)
    LOG.info('Responding to state change events ...')
    try:
        _process_state_change_events()
    except ValueError as error:
        LOG.critical('Value error: %s', str(error))
    except KeyboardInterrupt as err:
        LOG.debug('Keyboard Interrupt %s', err)
    LOG.info('Exiting!')


if __name__ == '__main__':
    main()
