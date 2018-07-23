# -*- coding: utf-8 -*-
""" Initialise test configuration database for the Master Controller."""

import redis
import datetime

from app.master_client import MasterClient as masterClient

db = masterClient()

mc_root = 'execution_control:master_controller'

db.update_value(mc_root, 'target_state', 'OFF')
db.update_value(mc_root, 'TANGO_state', 'OFF')
db.update_value(mc_root, 'state_timestamp', str(datetime.datetime.utcnow()))
