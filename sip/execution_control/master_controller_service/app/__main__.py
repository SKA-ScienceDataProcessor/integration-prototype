# -*- coding: utf-8 -*-
"""Mock services watchdog."""

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

from .master_client import MasterClient as masterClient

MC = 'execution_control:master_controller'
PC = 'sdp_components:processing_controller'
#~ LOG = 'sdp_components:logging'

db = masterClient()

def main():
    """Application entry point."""

    logger = logging.getLogger(__name__)
    logger.debug("in main()")
    while True:
        time.sleep(1)
        try:
            logger.debug('Setting timestamp so that we know this process is working')
            db.update_value(MC, 'State_timestamp',
                        str(datetime.datetime.utcnow()))
            logger.debug('Getting target state')
            target_state = db.get_value(MC, "Target_state") ### Name?
            if target_state is not None:
                logger.info('Target state is {}'.format(target_state))
                sdp_state =  db.get_value(MC, "SDP_state") ### Name?
                if target_state != sdp_state:
                    logger.debug('Setting SDP_state to be the same as target_state')
                    db.update_value(MC, "SDP_state", target_state)
                    ### update component target states. Presumably processing 
                    ### controller & processing block controller?
                    ### is it as simple as this?
                    logger.debug('Setting PC_state to be the same as target_state')
                    db.update_value(PC, "Target_state", target_state)
                    ### We may need to check the target state prior to setting these?
            else:
                logger.warning('Could not establish target state')
            logger.debug('Getting states of components')
        except Exception as err:
            logger.warning('Exception occured {}'.format(err))
            pass


if __name__ == '__main__':
    logging.config.dictConfig(json.loads(logConfigAsJSON))
    logger = logging.getLogger(__name__)
    try:
        logger.debug("starting")
        main()
    except KeyboardInterrupt as err:
        logger.debug('Keyboard Interrupt {}'.format(err))
        logger.info('Exiting!')
