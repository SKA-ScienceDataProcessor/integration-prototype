# -*- coding: utf-8 -*-
"""Mock services watchdog."""

import datetime
import os
import time

from .master_client import masterClient

ROOT = 'execution_control:master_controller'

db = masterClient()

def main():
    """Application entry point."""

    while True:
        time.sleep(1)
        try:
            target_state = db.get_value(ROOT, "target_state")
            if target_state != None:
                db.update_value(ROOT, "TANGO_state", target_state)
                db.update_value(ROOT, 'state_timestamp',
                        str(datetime.datetime.now()))
        except:
            pass


if __name__ == '__main__':
    main()
