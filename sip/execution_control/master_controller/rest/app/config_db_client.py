# -*- coding: utf-8 -*-
"""Client for the Redis Configuration database.

This provides configuration database accessfunctions for the master controller
"""
import os
import redis

DB = redis.Redis(host=os.getenv('DATABASE_HOST'))

ROOT = 'execution_control:master_controller'

def put_target_state(state):
    DB.set(ROOT + ':target_state', state)


def get_tango_state():
    return DB.get(ROOT + ':TANGO_state')
