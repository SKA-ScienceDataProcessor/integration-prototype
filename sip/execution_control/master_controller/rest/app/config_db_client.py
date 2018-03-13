# -*- coding: utf-8 -*-
"""Client for the Redis Configuration database.

This provides configuration database accessfunctions for the master controller
"""
import os
import redis
from datetime import datetime

DB = redis.Redis(host=os.getenv('DATABASE_HOST'))

ROOT = 'execution_control:master_controller'

def put_target_state(state):
    """ Put the target state to the database"""
    DB.set(ROOT + ':target_state', state)


def get_tango_state():
    """ Get TANGO state from the database."""
    return DB.get(ROOT + ':TANGO_state').decode()


def check_timestamp():
    """Check that the timestamp is up-to-date."""
    timestamp = DB.get(ROOT + ':state_timestamp')
    if timestamp == None:
        return False
    s = timestamp.decode()
    timestamp = datetime.strptime(s, '%Y-%m-%d %H:%M:%S.%f')
    return (datetime.now() - timestamp).seconds < 10
