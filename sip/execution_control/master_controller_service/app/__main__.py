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
#~ from . import events # ? probably access events as masterClient.events if I needed to

MC = 'master_controller'
PC = 'processing_controller'
#~ MC = 'execution_control:master_controller'
#~ PC = 'sdp_components:processing_controller'
#~ LOG = 'sdp_components:logging'

db = masterClient()

def main():
    """Application entry point.
        In the original version we would poll the database.
        In this version we subscribe to the events we are
        interested in and then poll the event queue until
        our event comes up.
    """

    logger = logging.getLogger(__name__)
    logger.debug("in main()")
    #~ aggregate_type = 'rest_interface' # placeholder
    subscriber = 'Master_Controller_Service'
    #~ event_type = 'change'
    #~ aggregate_key = 'chuck' # placeholder - not needed?
    logger.debug('About to register with event queue')
    #~ event_queue = events.subscribe(aggregate_type, subscriber)
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
                #~ logger.debug(
                  #~ 'Setting timestamp so that we know this process is working')
                #~ db.update_value(MC, 'State_timestamp',
                            #~ str(datetime.datetime.utcnow()))
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
                        # What SHOULD we do if the target state is OFF?
                        # Change to init?
                        # Should we have an OFF/INIT sequence?
                        if target_state == 'OFF':
                            logger.info('Target State is OFF')
                        logger.debug(
                          'Setting SDP_state to be the same as target_state')
                        #~ db.update_value(MC, "SDP_state", target_state)
                        #~ db.update_sdp_state(target_state)
                        db.update_sdp_state("SDP_state", target_state)
                        ### update component target states. Presumably processing 
                        ### controller & processing block controller?
                        ### is it as simple as this?
                        logger.debug(
                            'Setting PC_state to be the same as target_state')
                        #~ db.update_value(PC, "Target_state", target_state)
                        db.update_component_state(PC, "Target_state", target_state)
                        ### We may need to check the target state prior to
                        ### setting these?
                else:
                    logger.warning('Target state does not exist in database.')
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
