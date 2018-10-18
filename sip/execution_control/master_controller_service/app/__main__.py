# -*- coding: utf-8 -*-
"""
    Master Controller Service.

    This version polls REDIS Events rather
    than the database directly.
"""

from time import time, sleep
from sched import scheduler
import json
import logging
import logging.config
from config_db.master_client import MasterDbClient as masterClient

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


MC = 'master_controller'
PC = 'processing_controller'
LOG = 'logging'

db = masterClient()


def update_components(target_state):
    """
    When we get a new target state this function is called
    to ensure components receive the target state(s) and act
    on them.
    """

    # ### update component target states. Presumably processing
    # ### controller & processing block controller?
    # ### is it as simple as this?
    # ### We may need to check the target state prior to
    # ### setting these?
    logger.debug('Setting PC state to be {}'.format(target_state))
    db.update_component_state(PC, "Target_state", target_state)
    db.update_component_state(LOG, "Target_state", target_state)

    # What SHOULD we do if the target state is OFF?
    # Change to init?
    # Should we have an OFF/INIT sequence?
    # For the time being we assume that we have made further calls to the
    # subcomponents and received a new status from them
    # at this point the Current_State for the components should have been
    # modified we will do this ourselves for now
    if target_state == 'OFF':
        logger.info('Target State is OFF')
        logger.debug('Pretend to do extra work. New state is INIT.')
        target_state = 'INIT'
    # Presumably in a later version we would actually set target state, eg:
    # db.update_component_state(PC, "Target_state", target_state)
    # We could then use the scheduler schedule another function to check 
    # that they have changed.
    db.update_component_state(PC, "Current_state", target_state)
    db.update_component_state(LOG, "Current_state", target_state)
    logger.debug('Pretend to do work. New state is {}.'.format(target_state))
    return(target_state)


def handle_event(event):
    """
    Retrieve the target state and update the SDP state.
    """

    try:
        logger.debug('Getting target state')
        target_state = db.get_value(MC, "Target_state")
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
            sdp_state = db.get_value(MC, "SDP_state")
            if target_state == sdp_state:
                return
            logger.debug(
                'Communicating target_state to component systems')
            updated_state = update_components(target_state)
            logger.debug(
              'Setting SDP_state to be the new state {}.'.
              format(updated_state))
            db.update_sdp_state("SDP_state", updated_state)
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
    if event and event.type == 'updated':
        logger.debug('Event ID is {}'.format(event.id))
        handle_event(event)
    # Return to this function after one second
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
        subscriber = 'Master_Controller_Service'
        logger.debug('About to register with event queue')
        event_queue = db.subscribe(subscriber)
        active_subs = db.get_subscribers()
        logger.debug('Subscribers: {}'.format(active_subs))
        sch.enter(0, 1, check_event_queue)
        sch.run()
    except KeyboardInterrupt as err:
        logger.debug('Keyboard Interrupt {}'.format(err))
        logger.info('Exiting!')
