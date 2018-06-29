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
      "level": "INFO",
      "handlers": ["console"]
   }
}
'''

from .master_client import masterClient

ROOT = 'execution_control:master_controller'

db = masterClient()

def main():
    """Application entry point."""

    logger = logging.getLogger(__name__)
    logger.debug("in main()")
    while True:
        time.sleep(1)
        try:
            logger.debug('getting target state')
            target_state = db.get_value(ROOT, "target_state")
            if target_state != None:
                logger.info('Target state is {}'.format(target_state))
                db.update_value(ROOT, "TANGO_state", target_state)
                db.update_value(ROOT, 'state_timestamp',
                        str(datetime.datetime.utcnow()))
        except Exception as err:
            logger.debug('exception {}'.format(err))
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
