# -*- coding: utf-8 -*-
"""
    Master Controller Service.

    This version polls REDIS Events rather
    than the database directly.
    
    Changes to the REDIS DB
    from config_db.sdp_state import SDPState
    from config_db.service_state import ServiceState
    sdp_state = SDPState()
    event_queue = sdp_state.subscribe(...)
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

from time import time, sleep
from sched import scheduler
import json
import logging
import logging.config
#~ from config_db.master_client import MasterDbClient as masterClient
from config_db.sdp_state import SDPState
from config_db.service_state import ServiceState

logConfigAsJSON = '''{
    "version": 1,
    "formatters":
    {
        "default":
        {
            "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
        }
    },
    "handlers":
    {
        "console":
        {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "default",
            "stream": "ext://sys.stdout"
        }
    },
    "root":
    {
        "level": "DEBUG",
        "handlers": ["console"]
    }
}
'''


sdp_db = SDPState()
mc_db  = ServiceState("ExecutionControl", "MasterController", "test")
pc_db  = ServiceState("ExecutionControl", "ProcessingController", "test")
pbc_db = ServiceState("ExecutionControl", "ProcessingBlockController", "test")
al_db  = ServiceState("ExecutionControl", "Alerts", "test")


def update_sub_state(ob):
    ts = ob.update_current_state(ob.target_state)


def update_components(target_state):
    """
    When we get a new target state this function is called
    to ensure components receive the target state(s) and act
    on them.
    """

    # ### update component target states. 
    #~ logger.debug('Setting MC state to be {}'.format(target_state))
    #~ if mc_db.current_state != target_state:
        #~ mc_db.update_target_state(target_state)
        #~ sch.enter(1,1,update_sub_state,(mc_db,))
    #~ logger.debug('Setting PC state to be {}'.format(target_state))
    #~ if pc_db.current_state != target_state:
        #~ pc_db.update_target_state(target_state)
        #~ sch.enter(1,1,update_sub_state,(pc_db,))
    #~ logger.debug('Setting PBC state to be {}'.format(target_state))
    #~ if pbc_db.current_state != target_state:
        #~ pbc_db.update_target_state(target_state)
        #~ sch.enter(1,1,update_sub_state,(pbc_db,))
    #~ logger.debug('Setting AL state to be {}'.format(target_state))
    #~ if al_db.current_state != target_state:
        #~ al_db.update_target_state(target_state)
        #~ sch.enter(1,1,update_sub_state,(al_db,))

    #~ sleep(10) # allow the scheduler time to update the components - temporary kludge
    # If the target state is OFF we leave it. 
    # We cannot do anything from an OFF state.
    if target_state == 'OFF':
        logger.info('Target State is OFF - Operator intervention required.')
    logger.debug('New state is {}.'.format(target_state))
    return(target_state)


def handle_event(event):
    """
    Retrieve the target state and update the SDP state.
    """

    try:
        logger.debug('Getting target state')
        target_state = sdp_db.target_state
        if target_state is not None:
            logger.info('Target state is {}'.format(target_state))

            # The target state may have been set to the same as the
            # current state, in which case don't bother changing it.
            # Alternatively we could assume if the target state has
            # been set it will be different to the current state and
            # we should change regardless.
            # Certainly, in the REST variant of the Master Interface
            # Service will only change the target state if it is different
            # to the SDP state.
            sdp_state = sdp_db.current_state
            if target_state == sdp_state:
                return # what about timestamp?
            states = sdp_db.allowed_state_transitions[sdp_state]
            if not states:
                logger.warn('No allowed states; cannot continue')
                return
            if not target_state in states:
                logger.warn('Target state {} not in valide list ({})'.format(target_state,states))
                return
            logger.debug(
                'Communicating target_state to component systems')
            updated_state = update_components(target_state)
            logger.debug(
              'Setting SDP_state to be the new state {}.'.
              format(updated_state))
            ts = sdp_db.update_current_state(updated_state)
        else:
            logger.warning('Target state does not exist in database.')
    except Exception as err:
        logger.warning('Exception occured {}'.format(err))


def check_event_queue():
    """
    Poll the Event Queue.
    
    Call handle_event if there is an event of type updated.
    Reset the scheduler to call this function again in 1 second.
    """
    event = event_queue.get()
    logger.debug('Event is {}'.format(event))
    if event:
        logger.debug('Event type is {}'.format(event.type))
    if event and event.type == 'target_state_updated' and event.object_id == 'sdp_state':
        logger.debug('Event ID is {}'.format(event.id))
        handle_event(event)
    # Rerun this function after one second
    sch.enter(1, 1, check_event_queue)


if __name__ == '__main__':
    """Application entry point.

    Logging, scheduling, database and database events
    are all set up here.
    DB event queue polling is done by check_event_queue()
    which itself is called by sched.scheduler()
    """
    logging.config.dictConfig(json.loads(logConfigAsJSON))
    logger = logging.getLogger(__name__)
    sch = scheduler(time, sleep)
    try:
        logger.debug("starting")
        if sdp_db.current_state in ('unknown',):
            logger.debug("Required to switch current_state to init")
            sdp_db.update_current_state('init')
        subscriber = 'SDP'
        logger.debug('About to register with event queue')
        event_queue = sdp_db.subscribe(subscriber)
        active_subs = sdp_db.get_subscribers()
        logger.debug('Subscribers: {}'.format(active_subs))
        sch.enter(0, 1, check_event_queue)
        sch.run()
    except KeyboardInterrupt as err:
        logger.debug('Keyboard Interrupt {}'.format(err))
        logger.info('Exiting!')
