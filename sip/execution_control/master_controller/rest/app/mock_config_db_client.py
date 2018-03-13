# -*- coding: utf-8 -*-
"""Mock client for the Redis Configuration database.

This provides functions for testing the master controller
"""

TARGET_STATE = 'INIT'

def put_target_state(state):
    global TARGET_STATE
    TARGET_STATE = state

def get_tango_state():
    return TARGET_STATE
