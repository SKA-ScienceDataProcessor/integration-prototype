# -*- coding: utf-8 -*-
"""
    Master Controller Service.
    This version polls REDIS Events rather
    than the database directly.
"""

import datetime
import os
import time
import json
import logging
import logging.config

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

from .master_client import MasterDbClient as masterClient

MC = 'master_controller'
PC = 'processing_controller'
LOG = 'logging'
#~ MC = 'execution_control:master_controller'
#~ PC = 'sdp_components:processing_controller'
#~ LOG = 'sdp_components:logging'

db = masterClient()

def update_components(target_state):
    '''
    When we get a new target state this function is called
    to ensure components receive the target state(s) and act
    on them.
    '''
    logger = logging.getLogger(__name__)
    ### update component target states. Presumably processing
    ### controller & processing block controller?
    ### is it as simple as this?
    logger.debug('Setting PC state to be {}'.format(target_state))
    db.update_component_state(PC, "Target_state", target_state)
    db.update_component_state(LOG, "Target_state", target_state)

                        ### We may need to check the target state prior to
                        ### setting these?
    # What SHOULD we do if the target state is OFF?
    # Change to init?
    # Should we have an OFF/INIT sequence?
    # For the time being we assume that we have made further calls to the
    # subcomponents and received a new status from them
    # at this point the Current_State for the components should have been
    # modified we will do this ourselves for now
    if target_state == 'OFF':
        logger.info('Target State is OFF')
        logger.debug('Pretend to do work. New state is INIT.')
        target_state = 'INIT'
        #~ return('INIT')
    db.update_component_state(PC, "Current_state", target_state)
    db.update_component_state(LOG, "Current_state", target_state)
    logger.debug('Pretend to do work. New state is {}.'.format(target_state))
    return(target_state)


def main():
    """Application entry point.
        In the original version we would poll the database.
        In this version we subscribe to the events we are
        interested in and then poll the event queue until
        our event comes up.
    """

    logger = logging.getLogger(__name__)
    logger.debug("in main()")
    subscriber = 'Master_Controller_Service'
    logger.debug('About to register with event queue')
    event_queue = db.subscribe(subscriber)
    active_subs = db.get_subscribers()
    logger.debug('Subcribers: {}'.format(active_subs))
    while True:
        time.sleep(1)
        '''
        Poll the event queue and loop round if there is no event.
        My understanding is I do not have to check the event type
        here, because I only subscribe to the events I am interested in
        and the event queue only returns events I have subcribed to.
        '''
        event = event_queue.get()
        logger.debug('Event is {}'.format(event))
        if event:
            logger.debug('Event ID is {}'.format(event.id))
            logger.debug('Aggregate Type is {}'.format(event.aggregate_type))
            try:
                logger.debug('Getting target state')
                target_state = db.get_value(MC, "Target_state")
                if target_state is not None:
                    logger.info('Target state is {}'.format(target_state))
                    '''
                    The target state may have been set to the same as the
                    current state, in which case don't bother changing it.
                    Alternatively we could assume if the target state has
                    been set it will be different to the current state and
                    we should change regardless.
                    '''
                    sdp_state =  db.get_value(MC, "SDP_state")
                    if target_state != sdp_state:
                        logger.debug(
                            'Communicating target_state to component systems')
                        updated_state = update_components(target_state)
                        logger.debug(
                          'Setting SDP_state to be the new state {}.'.\
                                                        format(updated_state))
                        db.update_sdp_state("SDP_state", updated_state)
                else:
                    logger.warning('Target state does not exist in database.')
                # this probably wants to be moved into update_components
                logger.debug('Getting states of components')
            except Exception as err:
                logger.warning('Exception occured {}'.format(err))


if __name__ == '__main__':
    logging.config.dictConfig(json.loads(logConfigAsJSON))
    logger = logging.getLogger(__name__)
    try:
        logger.debug("starting")
        main()
    except KeyboardInterrupt as err:
        logger.debug('Keyboard Interrupt {}'.format(err))
        logger.info('Exiting!')
