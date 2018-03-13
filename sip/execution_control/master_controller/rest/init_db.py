# -*- coding: utf-8 -*-
""" Initialise test configuration database for the Master Controller."""

import redis
import datetime

DB = redis.Redis(host='localhost', port=6379)

DB.flushall()

mc_root = 'execution_control:master_controller'

DB.set(mc_root + ':target_state', 'OFF')
DB.set(mc_root + ':TANGO_state', 'OFF')
DB.set(mc_root + ':state_timestamp', str(datetime.datetime.now()))
