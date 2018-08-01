# -*- coding: utf-8 -*-
""" Initialise test configuration database for the Master Controller."""

import redis
import datetime

from configuration_db.redis.db_client.master_client import MasterClient as masterClient

db = masterClient()

mc_root = 'execution_control:master_controller'

db.update_value(mc_root, 'Target_state', 'OFF')
db.update_value(mc_root, 'SDP_state', 'OFF')
db.update_value(mc_root, 'State_timestamp', str(datetime.datetime.utcnow()))
