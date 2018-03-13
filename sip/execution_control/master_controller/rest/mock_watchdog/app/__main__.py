# -*- coding: utf-8 -*-
"""Mock services watchdog."""

import os
import redis
import datetime

DB = redis.Redis(host=os.getenv('DATABASE_HOST'))

ROOT = 'execution_control:master_controller'


def main():
    """Application entry point."""

    while True:
        target_state = DB.get(ROOT + ":target_state")
        if target_state != None:
            DB.set(ROOT + ":TANGO_state", target_state)
            DB.set(ROOT + ':state_timestamp', str(datetime.datetime.now()))


if __name__ == '__main__':
    main()
